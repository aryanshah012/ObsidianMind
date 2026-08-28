"""
Chunking module for Obsidian markdown notes.
Splits parsed documents into semantically coherent segments while preserving rich metadata.
"""

from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.ingestion.parser import ObsidianDocument


class ObsidianChunker:
    """Chunks Obsidian markdown documents with metadata propagation."""

    # Markdown-aware separators prioritizing section boundaries
    DEFAULT_SEPARATORS = [
        "\n# ",
        "\n## ",
        "\n### ",
        "\n#### ",
        "\n\n",
        "\n",
        ". ",
        " ",
        "",
    ]

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        separators: Optional[List[str]] = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.separators = separators or self.DEFAULT_SEPARATORS

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            keep_separator=True,
            length_function=len,
        )

    def chunk_document(self, doc: ObsidianDocument) -> List[Document]:
        """
        Split a single ObsidianDocument into LangChain Document chunks.

        Args:
            doc: Parsed ObsidianDocument.

        Returns:
            List of LangChain Document objects with preserved metadata.
        """
        content = doc.content.strip()
        if not content:
            return []

        # Split text
        text_chunks = self.splitter.split_text(content)
        total_chunks = len(text_chunks)

        documents: List[Document] = []
        tags_str = ", ".join(doc.tags) if isinstance(doc.tags, list) else str(doc.tags)

        for idx, chunk_text in enumerate(text_chunks):
            # ChromaDB metadata values must be str, int, float, or bool
            chunk_metadata = {
                "source": doc.source,
                "filename": doc.metadata.get("filename", ""),
                "title": doc.title,
                "folder": doc.folder,
                "tags": tags_str,
                "created": doc.metadata.get("created", ""),
                "chunk_id": idx,
                "total_chunks": total_chunks,
                "char_count": len(chunk_text),
            }

            doc_chunk = Document(
                page_content=chunk_text,
                metadata=chunk_metadata,
            )
            documents.append(doc_chunk)

        return documents

    def chunk_documents(self, docs: List[ObsidianDocument]) -> List[Document]:
        """
        Chunk a list of parsed ObsidianDocuments.

        Args:
            docs: List of ObsidianDocument instances.

        Returns:
            Flattened list of all chunked Document objects.
        """
        all_chunks: List[Document] = []
        for doc in docs:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        return all_chunks
