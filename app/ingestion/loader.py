"""
Vault Loader module.
Recursively inspects vault directories, skips irrelevant / system files,
parses markdown notes, and triggers the chunking pipeline.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Optional
from langchain_core.documents import Document

from app.ingestion.parser import ObsidianParser, ObsidianDocument
from app.ingestion.pdf_parser import PDFParser
from app.ingestion.chunker import ObsidianChunker


@dataclass
class IngestionResult:
    """Summary and artifacts resulting from vault ingestion."""
    total_notes_found: int = 0
    total_chunks_created: int = 0
    processed_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    documents: List[ObsidianDocument] = field(default_factory=list)
    chunks: List[Document] = field(default_factory=list)

    @property
    def is_success(self) -> bool:
        return self.total_notes_found > 0 and len(self.errors) == 0


class ObsidianVaultLoader:
    """Recursively loads, filters, parses, and chunks notes and PDFs from an Obsidian vault."""

    IGNORED_DIRECTORIES: Set[str] = {
        ".obsidian",
        ".trash",
        ".git",
        ".vscode",
        ".idea",
        "node_modules",
        "__pycache__",
        ".cache",
        "templates",
        "__MACOSX",
    }

    IGNORED_EXTENSIONS: Set[str] = {
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
        ".mp4", ".mov", ".avi", ".mkv",
        ".mp3", ".wav", ".ogg",
        ".zip", ".tar", ".gz",
        ".json", ".css", ".js", ".pyc", ".DS_Store"
    }

    def __init__(
        self,
        parser: Optional[ObsidianParser] = None,
        pdf_parser: Optional[PDFParser] = None,
        chunker: Optional[ObsidianChunker] = None,
    ):
        self.parser = parser or ObsidianParser()
        self.pdf_parser = pdf_parser or PDFParser()
        self.chunker = chunker or ObsidianChunker()

    def load_vault(self, vault_path: Path) -> IngestionResult:
        """
        Scan and process all markdown notes and PDF documents within the vault directory.

        Args:
            vault_path: Path to the root directory of the vault.

        Returns:
            IngestionResult containing statistics, documents, and chunks.
        """
        vault_path = Path(vault_path).resolve()
        result = IngestionResult()

        if not vault_path.exists():
            result.errors.append(f"Vault path does not exist: {vault_path}")
            return result

        if not vault_path.is_dir():
            # If path is a single PDF or Markdown/Text file
            ext = vault_path.suffix.lower()
            if ext == ".pdf":
                return self.load_pdf_file(vault_path)
            elif ext in [".md", ".markdown", ".txt"]:
                return self.load_markdown_file(vault_path)
            result.errors.append(f"Vault path is not a directory or supported file: {vault_path}")
            return result

        # Traverse directory
        for item in vault_path.rglob("*"):
            # Check if any parent component is in ignored directories
            parts = item.relative_to(vault_path).parts
            if any(part in self.IGNORED_DIRECTORIES or part.startswith(".") for part in parts):
                continue

            if item.is_dir():
                continue

            # Skip hidden files or AppleDouble metadata files (e.g. ._filename.pdf)
            if item.name.startswith(".") or item.name.startswith("._"):
                continue

            ext = item.suffix.lower()

            # Handle PDF files
            if ext == ".pdf":
                try:
                    pdf_docs = self.pdf_parser.parse_file(item, vault_path)
                    if not pdf_docs:
                        result.skipped_files.append(f"{item.name} (empty or scanned PDF)")
                        continue

                    pdf_chunks = self.chunker.chunk_documents(pdf_docs)
                    result.documents.extend(pdf_docs)
                    result.chunks.extend(pdf_chunks)
                    result.processed_files.append(str(item.relative_to(vault_path)))
                    result.total_notes_found += 1
                    result.total_chunks_created += len(pdf_chunks)
                except Exception as e:
                    result.errors.append(f"Failed to process PDF {item.name}: {str(e)}")
                continue

            # Skip non-markdown/non-text files
            if ext not in [".md", ".markdown", ".txt"]:
                if ext in self.IGNORED_EXTENSIONS or item.name.startswith("."):
                    result.skipped_files.append(str(item.relative_to(vault_path)))
                continue

            # Process valid Markdown or Text note
            try:
                doc = self.parser.parse_file(item, vault_path)
                
                # Check for empty content
                if not doc.content.strip():
                    result.skipped_files.append(f"{doc.source} (empty file)")
                    continue

                chunks = self.chunker.chunk_document(doc)
                
                result.documents.append(doc)
                result.chunks.extend(chunks)
                result.processed_files.append(doc.source)
                result.total_notes_found += 1
                result.total_chunks_created += len(chunks)

            except Exception as e:
                err_msg = f"Failed to process {item.name}: {str(e)}"
                result.errors.append(err_msg)

        return result

    def load_pdf_file(self, pdf_path: Path, override_filename: Optional[str] = None) -> IngestionResult:
        """Process a single standalone PDF document."""
        result = IngestionResult()
        pdf_path = Path(pdf_path).resolve()
        display_name = override_filename or pdf_path.name

        try:
            pdf_docs = self.pdf_parser.parse_file(pdf_path, override_filename=override_filename)
            if not pdf_docs:
                result.skipped_files.append(f"{display_name} (empty PDF)")
                return result

            pdf_chunks = self.chunker.chunk_documents(pdf_docs)
            result.documents.extend(pdf_docs)
            result.chunks.extend(pdf_chunks)
            result.processed_files.append(display_name)
            result.total_notes_found = 1
            result.total_chunks_created = len(pdf_chunks)
        except Exception as e:
            result.errors.append(f"Failed to process PDF: {str(e)}")

        return result

    def load_markdown_file(self, md_path: Path, override_filename: Optional[str] = None) -> IngestionResult:
        """Process a single standalone Markdown or text document."""
        result = IngestionResult()
        md_path = Path(md_path).resolve()
        display_name = override_filename or md_path.name

        try:
            doc = self.parser.parse_file(md_path, override_filename=override_filename)
            if not doc.content.strip():
                result.skipped_files.append(f"{display_name} (empty file)")
                return result

            chunks = self.chunker.chunk_document(doc)
            result.documents.append(doc)
            result.chunks.extend(chunks)
            result.processed_files.append(display_name)
            result.total_notes_found = 1
            result.total_chunks_created = len(chunks)
        except Exception as e:
            result.errors.append(f"Failed to process note: {str(e)}")

        return result
