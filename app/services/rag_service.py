"""
Service facade for ObsidianMind.
Integrates Ingestion, Vector Storage, Retrieval, and LangGraph Agent workflow
into a clean, thread-safe service API for the UI and CLI with Multi-Vault support
and complete per-user isolation.
"""

import time
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from langchain_core.documents import Document

from app.config import settings
from app.ingestion.zip_extractor import extract_zip_safely
from app.ingestion.loader import ObsidianVaultLoader, IngestionResult
from app.embeddings.embedder import get_embedder
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import ObsidianRetriever
from app.llm.model import get_llm
from app.agents.rag_graph import ObsidianRAGWorkflow
from app.services.vault_manager import VaultManager, VaultMetadata


class RAGService:
    """High-level service facade for ObsidianMind with Multi-Vault and User isolation support."""

    def __init__(
        self,
        user_id: Optional[str] = None,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        api_key: Optional[str] = None,
        embedding_provider: Optional[str] = None,
        embedding_model: Optional[str] = None,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        vault_id: Optional[str] = None,
    ):
        self.user_id = user_id

        # Vault Workspace Manager scoped to user
        self.vault_manager = VaultManager(user_id=user_id)
        if vault_id:
            self.vault_manager.set_active_vault(vault_id)

        active_vault = self.vault_manager.get_active_vault()

        # Component initializations
        self.loader = ObsidianVaultLoader()
        self.embedder = get_embedder(
            provider=embedding_provider,
            model_name=embedding_model,
        )
        self.vector_store = ChromaVectorStore(
            embedder=self.embedder,
            persist_dir=settings.CHROMA_PERSIST_DIRECTORY,
            collection_name=active_vault.collection_name,
        )
        self.retriever = ObsidianRetriever(
            vector_store=self.vector_store,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        self.llm = get_llm(
            provider=llm_provider,
            model_name=llm_model,
            api_key=api_key,
        )
        self.workflow = ObsidianRAGWorkflow(
            llm=self.llm,
            retriever=self.retriever,
        )

        # Ingestion state tracking per vault
        self.last_ingestion_result: Optional[IngestionResult] = None
        self.last_indexed_at: Optional[str] = None

    def switch_vault(self, vault_id: str) -> bool:
        """Switch active vault workspace and re-target ChromaDB collection."""
        success = self.vault_manager.set_active_vault(vault_id)
        if success:
            active_vault = self.vault_manager.get_active_vault()
            self.vector_store.switch_collection(active_vault.collection_name)
            self.retriever.vector_store = self.vector_store
            self.last_ingestion_result = None
        return success

    def list_vaults(self) -> List[Dict[str, Any]]:
        """Return list of user vaults with live vector counts."""
        vaults = self.vault_manager.list_vaults()
        current_active = self.vault_manager.active_vault_id

        results = []
        for v in vaults:
            col_name = v.get("collection_name", "obsidian_vault")
            try:
                col = self.vector_store.client.get_collection(
                    name=col_name,
                    embedding_function=self.vector_store.chroma_adapter,
                )
                chunk_count = col.count()
            except Exception:
                chunk_count = 0

            results.append({
                **v,
                "chunk_count": chunk_count,
                "is_active": (v["id"] == current_active),
            })
        return results

    def create_vault(
        self,
        name: str,
        description: str = "",
        icon: str = "Folder",
        color: str = "#2E7D6A",
    ) -> VaultMetadata:
        """Create a new vault and switch to it."""
        new_vault = self.vault_manager.create_vault(
            name=name,
            description=description,
            icon=icon,
            color=color,
        )
        self.vector_store.switch_collection(new_vault.collection_name)
        self.retriever.vector_store = self.vector_store
        return new_vault

    def delete_vault(self, vault_id: str) -> bool:
        """Delete a custom vault workspace and its vector collection."""
        target = self.vault_manager.get_vault(vault_id)
        if not target or target.is_default:
            return False

        col_to_delete = target.collection_name
        success = self.vault_manager.delete_vault(vault_id)
        if success:
            self.vector_store.delete_collection(col_to_delete)
            active_vault = self.vault_manager.get_active_vault()
            self.vector_store.switch_collection(active_vault.collection_name)
            self.retriever.vector_store = self.vector_store

            # Remove disk storage for deleted vault
            vault_dir = self.get_vault_storage_dir(vault_id)
            if vault_dir.exists():
                shutil.rmtree(vault_dir, ignore_errors=True)

        return success

    def get_vault_storage_dir(self, vault_id: Optional[str] = None) -> Path:
        """Return and ensure disk storage directory for documents in target vault."""
        vid = vault_id or self.vault_manager.active_vault_id
        if self.user_id:
            target_dir = settings.USERS_DIR / self.user_id / "vaults" / vid
        else:
            target_dir = settings.DATA_DIR / "vaults" / vid
        target_dir.mkdir(parents=True, exist_ok=True)
        return target_dir

    def ingest_pdf_file(
        self,
        file_path: Path,
        clear_existing: bool = False,
        override_filename: Optional[str] = None,
        vault_id: Optional[str] = None,
    ) -> IngestionResult:
        """Parse, chunk, and index a single PDF document into target workspace."""
        if vault_id:
            self.switch_vault(vault_id)

        target_dir = self.get_vault_storage_dir(vault_id)
        saved_name = override_filename or file_path.name
        destination = target_dir / saved_name
        if file_path.resolve() != destination.resolve():
            shutil.copy2(file_path, destination)

        page_docs = self.loader.pdf_parser.parse_file(
            destination,
            vault_root=target_dir,
            override_filename=saved_name,
        )

        all_chunks: List[Document] = []
        for p_doc in page_docs:
            all_chunks.extend(self.loader.chunker.chunk_document(p_doc))

        if clear_existing:
            self.vector_store.clear()

        if all_chunks:
            self.vector_store.add_documents(all_chunks)

        self.last_indexed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return IngestionResult(
            total_notes_found=1,
            total_chunks_created=len(all_chunks),
            processed_files=[saved_name],
            documents=page_docs,
            chunks=all_chunks,
        )

    def ingest_markdown_file(
        self,
        file_path: Path,
        clear_existing: bool = False,
        override_filename: Optional[str] = None,
        vault_id: Optional[str] = None,
    ) -> IngestionResult:
        """Parse, chunk, and index a single Markdown document into target workspace."""
        if vault_id:
            self.switch_vault(vault_id)

        target_dir = self.get_vault_storage_dir(vault_id)
        saved_name = override_filename or file_path.name
        destination = target_dir / saved_name
        if file_path.resolve() != destination.resolve():
            shutil.copy2(file_path, destination)

        parsed_doc = self.loader.parser.parse_file(
            destination,
            vault_root=target_dir,
            override_filename=saved_name,
        )

        chunks = self.loader.chunker.chunk_document(parsed_doc)

        if clear_existing:
            self.vector_store.clear()

        if chunks:
            self.vector_store.add_documents(chunks)

        self.last_indexed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return IngestionResult(
            total_notes_found=1,
            total_chunks_created=len(chunks),
            processed_files=[saved_name],
            documents=[parsed_doc],
            chunks=chunks,
        )

    def ingest_zip_vault(
        self,
        zip_path: Path,
        clear_existing: bool = True,
        vault_id: Optional[str] = None,
    ) -> IngestionResult:
        """
        Safely extract and index an uploaded Obsidian vault ZIP into target workspace.
        """
        if vault_id:
            self.switch_vault(vault_id)

        extracted_dir = self.get_vault_storage_dir(vault_id)
        extracted_target, extracted_files = extract_zip_safely(
            zip_path=zip_path,
            target_dir=extracted_dir,
            max_size_mb=settings.MAX_FILE_SIZE_MB,
        )

        return self.ingest_directory_vault(extracted_target, clear_existing=clear_existing, vault_id=vault_id)

    def ingest_directory_vault(
        self,
        vault_dir: Path,
        clear_existing: bool = True,
        vault_id: Optional[str] = None,
    ) -> IngestionResult:
        """
        Index an unzipped Obsidian vault folder into target workspace.
        """
        if vault_id:
            self.switch_vault(vault_id)

        ingest_result = self.loader.load_vault(vault_dir)

        if clear_existing:
            self.vector_store.clear()

        all_chunks = ingest_result.chunks
        if all_chunks:
            self.vector_store.add_documents(all_chunks)

        self.last_ingestion_result = ingest_result
        self.last_indexed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return ingest_result

    def load_sample_vault(self, clear_existing: bool = True, vault_id: Optional[str] = None) -> IngestionResult:
        """Load pre-packaged sample Obsidian vault into user's private workspace."""
        if vault_id:
            self.switch_vault(vault_id)

        target_dir = self.get_vault_storage_dir(vault_id)

        sample_zip = settings.SAMPLE_VAULT_ZIP
        sample_dir = settings.SAMPLE_VAULT_DIR

        if sample_zip.exists():
            return self.ingest_zip_vault(sample_zip, clear_existing=clear_existing, vault_id=vault_id)
        elif sample_dir.exists():
            # Copy sample files into user's private vault storage directory
            for item in sample_dir.rglob("*"):
                if item.is_file() and not item.name.startswith("."):
                    rel_path = item.relative_to(sample_dir)
                    dest_file = target_dir / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_file)

            return self.ingest_directory_vault(target_dir, clear_existing=clear_existing, vault_id=vault_id)
        else:
            raise FileNotFoundError("Sample vault files not found in data/ directory.")

    def ask(
        self,
        query: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        doc_filter: Optional[List[str]] = None,
        vault_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a user question through the LangGraph RAG workflow in active or scoped vault.
        """
        if vault_id and vault_id != self.vault_manager.active_vault_id:
            self.switch_vault(vault_id)

        start_time = time.time()
        final_state = self.workflow.run(
            query=query,
            chat_history=chat_history or [],
            doc_filter=doc_filter,
        )
        elapsed_sec = round(time.time() - start_time, 2)

        return {
            "query": query,
            "answer": final_state.get("answer", ""),
            "route": final_state.get("route", "KNOWLEDGE_BASE_QUERY"),
            "route_reasoning": final_state.get("route_reasoning", ""),
            "sources": final_state.get("sources", []),
            "retrieved_chunks": final_state.get("retrieved_chunks", []),
            "has_relevant_context": final_state.get("has_relevant_context", False),
            "execution_trace": final_state.get("execution_trace", []),
            "latency_sec": elapsed_sec,
            "error": final_state.get("error"),
            "vault_id": self.vault_manager.active_vault_id,
        }

    def clear_vault(self, vault_id: Optional[str] = None) -> None:
        """Clear indexed vectors and storage for active or specified vault."""
        if vault_id:
            self.switch_vault(vault_id)
        self.vector_store.clear()
        self.last_ingestion_result = None
        self.last_indexed_at = None

        # Clean files in user's vault storage
        target_dir = self.get_vault_storage_dir(vault_id)
        if target_dir.exists():
            for item in target_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)

    def get_stats(self, vault_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve diagnostics and status for active or specified vault workspace."""
        if vault_id and vault_id != self.vault_manager.active_vault_id:
            self.switch_vault(vault_id)

        active_vault = self.vault_manager.get_active_vault()
        total_chunks = self.vector_store.count()

        # Check files on disk in target vault storage
        vault_storage = self.get_vault_storage_dir(active_vault.id)
        vault_files = [p for p in vault_storage.rglob("*") if p.is_file() and p.suffix.lower() in [".md", ".pdf", ".txt"]]

        total_size_bytes = sum(p.stat().st_size for p in vault_files)
        total_notes = len(vault_files)

        folder_counts: Dict[str, int] = {}
        for p in vault_files:
            folder_name = p.parent.name if p.parent != vault_storage else "Root"
            folder_counts[folder_name] = folder_counts.get(folder_name, 0) + 1

        total_size_mb = f"{round(max(0.1, total_size_bytes / (1024 * 1024)), 1)} MB" if total_size_bytes > 0 else "0.0 MB"

        return {
            "status": "Ready" if total_chunks > 0 else "Empty",
            "vault_id": active_vault.id,
            "vault_name": active_vault.name,
            "vault_icon": active_vault.icon,
            "vault_color": active_vault.color,
            "total_notes": total_notes,
            "total_chunks": total_chunks,
            "total_size_mb": total_size_mb,
            "folders_count": len(folder_counts) if folder_counts else (1 if total_notes > 0 else 0),
            "folder_breakdown": folder_counts,
            "skipped_files": 0,
            "errors_count": 0,
            "last_indexed_at": self.last_indexed_at or ("Live" if total_chunks > 0 else "Not indexed"),
            "embedding_model": self.embedder.model_name,
            "llm_model": getattr(self.llm, "model_name", getattr(self.llm, "model", settings.LLM_MODEL)),
        }
