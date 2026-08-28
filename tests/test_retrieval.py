"""
Unit tests for ChromaDB storage, deduplication, and semantic retrieval.
"""

from langchain_core.documents import Document

from app.embeddings.embedder import MockEmbedder
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import ObsidianRetriever


def test_chroma_store_operations(tmp_path):
    persist_dir = str(tmp_path / "chroma_test")
    embedder = MockEmbedder()
    store = ChromaVectorStore(embedder=embedder, persist_dir=persist_dir, collection_name="test_col")

    docs = [
        Document(page_content="Retrieval-Augmented Generation combines search and generation.", metadata={"source": "AI/RAG.md", "title": "RAG", "chunk_id": 0}),
        Document(page_content="Transformers use multi-head self-attention mechanisms.", metadata={"source": "AI/LLMs.md", "title": "LLMs", "chunk_id": 0}),
    ]

    # Insert docs
    ids = store.add_documents(docs)
    assert len(ids) == 2
    assert store.count() == 2

    # Test deduplication on re-inserting same docs
    ids_re = store.add_documents(docs)
    assert len(ids_re) == 2
    assert store.count() == 2  # Count should remain 2, not duplicate!

    # Test search
    results = store.similarity_search("What is RAG?", k=2)
    assert len(results) == 2


def test_retriever_context_assembly(tmp_path):
    persist_dir = str(tmp_path / "chroma_retriever_test")
    embedder = MockEmbedder()
    store = ChromaVectorStore(embedder=embedder, persist_dir=persist_dir, collection_name="retriever_col")

    docs = [
        Document(
            page_content="LangGraph is a library for building stateful multi-actor agent workflows.",
            metadata={"source": "AI/LangGraph.md", "title": "LangGraph", "folder": "AI", "chunk_id": 0, "tags": "langgraph, agents"},
        ),
    ]
    store.add_documents(docs)

    retriever = ObsidianRetriever(vector_store=store, top_k=2, score_threshold=0.0)
    result = retriever.retrieve("How does LangGraph work?")

    assert result.has_relevant_context is True
    assert len(result.chunks) == 1
    assert "LangGraph" in result.formatted_context
    assert len(result.sources) == 1
    assert result.sources[0]["source"] == "AI/LangGraph.md"


def test_retriever_multi_document_filter(tmp_path):
    persist_dir = str(tmp_path / "chroma_filter_test")
    embedder = MockEmbedder()
    store = ChromaVectorStore(embedder=embedder, persist_dir=persist_dir, collection_name="filter_col")

    docs = [
        Document(page_content="RAG pipelines combine retrieval with LLM generation.", metadata={"source": "AI/RAG.md", "title": "RAG", "folder": "AI", "chunk_id": 0}),
        Document(page_content="Transformers use scaled dot product attention.", metadata={"source": "Papers/Transformers.pdf", "title": "Transformers", "folder": "Papers", "chunk_id": 0}),
        Document(page_content="Daily standup notes for Monday.", metadata={"source": "Daily/2026-08-18.md", "title": "Daily", "folder": "Daily", "chunk_id": 0}),
    ]
    store.add_documents(docs)

    retriever = ObsidianRetriever(vector_store=store, top_k=5, score_threshold=0.0)

    # Filter to only AI/RAG.md and Papers/Transformers.pdf
    result = retriever.retrieve("notes", doc_filter=["AI/RAG.md", "Papers/Transformers.pdf"])
    retrieved_sources = [c.source for c in result.chunks]

    assert "Daily/2026-08-18.md" not in retrieved_sources
    assert all(s in ["AI/RAG.md", "Papers/Transformers.pdf"] for s in retrieved_sources)
