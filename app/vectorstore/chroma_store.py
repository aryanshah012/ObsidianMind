"""
ChromaDB vector store implementation.
Provides persistent storage, deterministic ID generation, batch upserting,
and score-normalized similarity search.
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_core.documents import Document

from app.config import settings
from app.embeddings.base import BaseEmbedder
from app.embeddings.embedder import get_embedder
from app.vectorstore.base import BaseVectorStore


class ChromaEmbeddingFunctionAdapter:
    """Adapts our BaseEmbedder to ChromaDB's EmbeddingFunction interface."""

    def __init__(self, embedder: BaseEmbedder):
        self.embedder = embedder

    def __call__(self, input: Any) -> List[List[float]]:
        if isinstance(input, str):
            input = [input]
        return self.embedder.embed_documents(list(input))

    def embed_query(self, input: Any) -> List[List[float]]:
        if isinstance(input, str):
            return [self.embedder.embed_query(input)]
        return self.embedder.embed_documents(list(input))

    def embed_documents(self, input: Any) -> List[List[float]]:
        if isinstance(input, str):
            input = [input]
        return self.embedder.embed_documents(list(input))

    def name(self) -> str:
        return f"custom_{self.embedder.model_name}"


class ChromaVectorStore(BaseVectorStore):
    """Production-quality ChromaDB vector store wrapper."""

    def __init__(
        self,
        embedder: Optional[BaseEmbedder] = None,
        persist_dir: Optional[str] = None,
        collection_name: Optional[str] = None,
    ):
        self.embedder = embedder or get_embedder()
        self.persist_dir = Path(persist_dir or settings.CHROMA_PERSIST_DIRECTORY).resolve()
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME

        # Ensure persist directory exists
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.chroma_adapter = ChromaEmbeddingFunctionAdapter(self.embedder)

        # Initialize persistent client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False, is_persistent=True)
        )

        self._get_or_create_collection()

    def _get_or_create_collection(self) -> None:
        """Create or retrieve collection with cosine distance space."""
        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.chroma_adapter,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception:
            # Handle collection dimension mismatch by recreating collection
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.chroma_adapter,
                metadata={"hnsw:space": "cosine"}
            )

    def _generate_chunk_id(self, doc: Document, fallback_idx: int) -> str:
        """Generate deterministic chunk identifier to prevent duplicate entries."""
        source = doc.metadata.get("source", "doc")
        chunk_id = doc.metadata.get("chunk_id", fallback_idx)
        # Unique hash combining source + chunk_id + first 50 chars of content
        content_hash = hashlib.md5(doc.page_content[:100].encode("utf-8")).hexdigest()[:8]
        return f"{source}::c{chunk_id}::{content_hash}"

    def add_documents(self, documents: List[Document], batch_size: int = 150) -> List[str]:
        """
        Upsert documents into ChromaDB in batches.

        Args:
            documents: List of LangChain Document objects.
            batch_size: Batch size for insertions.

        Returns:
            List of generated document IDs.
        """
        if not documents:
            return []

        all_ids: List[str] = []

        for i in range(0, len(documents), batch_size):
            batch = documents[i : i + batch_size]
            batch_ids = [self._generate_chunk_id(doc, i + idx) for idx, doc in enumerate(batch)]
            batch_texts = [doc.page_content for doc in batch]
            
            # ChromaDB requires all metadata values to be str, int, float, bool
            batch_metadatas = []
            for doc in batch:
                clean_meta = {}
                for k, v in doc.metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean_meta[k] = v
                    elif isinstance(v, (list, tuple)):
                        clean_meta[k] = ", ".join(str(item) for item in v)
                    elif v is None:
                        clean_meta[k] = ""
                    else:
                        clean_meta[k] = str(v)
                batch_metadatas.append(clean_meta)

            try:
                self.collection.upsert(
                    ids=batch_ids,
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                )
            except Exception as e:
                if "dimension" in str(e).lower() or "expecting embedding" in str(e).lower():
                    self.clear()
                    self.collection.upsert(
                        ids=batch_ids,
                        documents=batch_texts,
                        metadatas=batch_metadatas,
                    )
                else:
                    raise
            all_ids.extend(batch_ids)

        return all_ids

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """Search top-k most similar document chunks."""
        results = self.similarity_search_with_score(query=query, k=k, filter_dict=filter_dict)
        return [doc for doc, _ in results]

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Search top-k similar chunks returning (Document, similarity_score) tuples.
        Distance in Chroma cosine space is d = 1 - cos(theta) where d in [0, 2].
        Normalized score is 1.0 - (d / 2.0) or max(0, 1.0 - d).
        """
        if self.count() == 0:
            return []

        effective_k = min(k, self.count())
        if effective_k <= 0:
            return []

        where_clause = filter_dict if filter_dict else None

        results = self.collection.query(
            query_texts=[query],
            n_results=effective_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        output: List[Tuple[Document, float]] = []

        if not results or not results["documents"] or not results["documents"][0]:
            return output

        documents = results["documents"][0]
        metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(documents)
        distances = results["distances"][0] if results["distances"] else [0.0] * len(documents)

        for text, meta, dist in zip(documents, metadatas, distances):
            # Chroma returns cosine distance (0 is exact match, 2 is opposite)
            # Normalize to 0..1 similarity score
            similarity_score = max(0.0, 1.0 - (dist / 2.0))
            doc = Document(page_content=text, metadata=meta or {})
            output.append((doc, similarity_score))

        return output

    def count(self) -> int:
        """Return total vector count in collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0

    def clear(self) -> None:
        """Delete collection vectors and re-initialize empty collection."""
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self._get_or_create_collection()

    def switch_collection(self, collection_name: str) -> None:
        """Dynamically switch active ChromaDB collection workspace."""
        if self.collection_name == collection_name:
            return
        self.collection_name = collection_name
        self._get_or_create_collection()

    def delete_collection(self, collection_name: str) -> bool:
        """Delete an entire named collection from persistent disk."""
        try:
            self.client.delete_collection(collection_name)
            if self.collection_name == collection_name:
                self.collection_name = settings.CHROMA_COLLECTION_NAME
                self._get_or_create_collection()
            return True
        except Exception:
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Return collection diagnostics."""
        count = self.count()
        return {
            "collection_name": self.collection_name,
            "count": count,
            "persist_directory": str(self.persist_dir),
            "embedding_model": self.embedder.model_name,
            "embedding_dim": self.embedder.dimension,
        }
