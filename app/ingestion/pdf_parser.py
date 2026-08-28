"""
PDF Document Parser for ObsidianMind.
Extracts text page-by-page from PDF documents, preserving page numbers,
headings, and hierarchical metadata.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
import pypdf

from app.ingestion.parser import ObsidianDocument


class PDFParser:
    """Extracts text and page-level metadata from PDF files."""

    def parse_file(
        self,
        file_path: Path,
        vault_root: Optional[Path] = None,
        override_filename: Optional[str] = None,
    ) -> List[ObsidianDocument]:
        """
        Parse a PDF file and return a list of ObsidianDocument objects (one per page).

        Args:
            file_path: Path to the .pdf file.
            vault_root: Optional root directory of the vault.
            override_filename: Optional explicit filename (e.g. from upload header).

        Returns:
            List of ObsidianDocument objects with page-level metadata.
        """
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        vault_root = vault_root or file_path.parent
        actual_name = override_filename or file_path.name

        try:
            rel_path = str(file_path.relative_to(vault_root)) if not override_filename else actual_name
        except ValueError:
            rel_path = actual_name

        folder = str(Path(rel_path).parent)
        if folder == ".":
            folder = "Root"

        stem = Path(actual_name).stem.replace("_", " ").replace("-", " ").title()

        page_documents: List[ObsidianDocument] = []

        try:
            reader = pypdf.PdfReader(str(file_path))
            total_pages = len(reader.pages)

            # Try to extract PDF document title from metadata if available
            pdf_title = stem
            if reader.metadata and reader.metadata.title:
                meta_title = str(reader.metadata.title).strip()
                if meta_title and meta_title.lower() not in ["(anonymous)", "untitled", "none", ""]:
                    pdf_title = meta_title

            for page_idx, page in enumerate(reader.pages, 1):
                # Extract text preserving linebreaks
                raw_text = page.extract_text() or ""
                # Normalize excessive spaces while keeping paragraphs/lines readable
                lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
                cleaned_text = "\n".join(lines)

                if not cleaned_text.strip():
                    continue

                page_title = f"{pdf_title} (Page {page_idx})"

                metadata: Dict[str, Any] = {
                    "source": rel_path,
                    "filename": actual_name,
                    "title": page_title,
                    "doc_title": pdf_title,
                    "folder": folder,
                    "page_number": page_idx,
                    "total_pages": total_pages,
                    "doc_type": "pdf",
                    "tags": ["pdf", folder.lower()],
                }

                doc = ObsidianDocument(
                    content=cleaned_text,
                    raw_content=raw_text,
                    metadata=metadata,
                    headings=[{"level": 1, "text": page_title, "start": 0}],
                )
                page_documents.append(doc)

        except Exception as e:
            raise IOError(f"Failed to extract text from PDF '{file_path.name}': {str(e)}")

        return page_documents
