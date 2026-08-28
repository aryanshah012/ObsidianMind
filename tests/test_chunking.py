"""
Unit tests for Obsidian document chunking and metadata propagation.
"""

from app.ingestion.parser import ObsidianDocument
from app.ingestion.chunker import ObsidianChunker


def test_chunker_metadata_propagation():
    long_text = "\n\n".join([f"Paragraph {i} with detailed information on AI." for i in range(30)])
    
    doc = ObsidianDocument(
        content=long_text,
        raw_content=long_text,
        metadata={
            "source": "AI/Transformers.md",
            "filename": "Transformers.md",
            "title": "Transformers Architecture",
            "folder": "AI",
            "tags": ["transformers", "attention"],
            "created": "2026-08-10",
        },
        headings=[{"level": 1, "text": "Transformers Architecture", "start": 0}],
    )

    chunker = ObsidianChunker(chunk_size=300, chunk_overlap=50)
    chunks = chunker.chunk_document(doc)

    assert len(chunks) > 1
    for idx, chunk in enumerate(chunks):
        meta = chunk.metadata
        assert meta["source"] == "AI/Transformers.md"
        assert meta["title"] == "Transformers Architecture"
        assert meta["folder"] == "AI"
        assert meta["chunk_id"] == idx
        assert meta["total_chunks"] == len(chunks)
        assert len(chunk.page_content) > 0


def test_chunker_empty_document():
    doc = ObsidianDocument(
        content="   ",
        raw_content="   ",
        metadata={"source": "Empty.md", "title": "Empty"},
    )
    chunker = ObsidianChunker()
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 0
