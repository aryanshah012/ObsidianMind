"""
Retrieval module for ObsidianMind.
Performs semantic similarity search with score thresholding, citation extraction,
and prompt context serialization.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from langchain_core.documents import Document

from app.config import settings
from app.vectorstore.base import BaseVectorStore
from app.vectorstore.chroma_store import ChromaVectorStore


@dataclass
class RetrievedChunk:
    """Represents a retrieved document chunk with relevance score."""
    content: str
    source: str
    title: str
    folder: str
    chunk_id: int
    score: float
    tags: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def excerpt(self) -> str:
        """Return a clean preview excerpt for citation display."""
        clean = " ".join(self.content.split())
        return clean[:220] + "..." if len(clean) > 220 else clean


@dataclass
class RetrievalResult:
    """Consolidated retrieval result containing chunks, context, and unique sources."""
    query: str
    chunks: List[RetrievedChunk] = field(default_factory=list)
    formatted_context: str = ""
    sources: List[Dict[str, Any]] = field(default_factory=list)
    has_relevant_context: bool = False

    @property
    def top_score(self) -> float:
        return self.chunks[0].score if self.chunks else 0.0


class ObsidianRetriever:
    """Retrieves and packages relevant context chunks from the vector database."""

    def __init__(
        self,
        vector_store: Optional[BaseVectorStore] = None,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
    ):
        self.vector_store = vector_store or ChromaVectorStore()
        self.top_k = top_k or settings.RETRIEVER_TOP_K
        self.score_threshold = score_threshold if score_threshold is not None else settings.RETRIEVER_SCORE_THRESHOLD

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        score_threshold: Optional[float] = None,
        doc_filter: Optional[List[str]] = None,
    ) -> RetrievalResult:
        """
        Execute semantic retrieval and assemble formatted LLM context.

        Args:
            query: User's search query.
            top_k: Optional override for number of retrieved chunks.
            score_threshold: Optional override for minimum similarity score.
            doc_filter: Optional list of source paths to restrict retrieval to.

        Returns:
            RetrievalResult object.
        """
        k = top_k or self.top_k
        threshold = score_threshold if score_threshold is not None else self.score_threshold

        filter_dict = None
        if doc_filter and len(doc_filter) > 0:
            if len(doc_filter) == 1:
                filter_dict = {"source": doc_filter[0]}
            else:
                filter_dict = {"source": {"$in": doc_filter}}

        # Execute similarity search with scores
        raw_results: List[Tuple[Document, float]] = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter_dict=filter_dict,
        )

        retrieved_chunks: List[RetrievedChunk] = []
        unique_sources: Dict[str, Dict[str, Any]] = {}

        for doc, score in raw_results:
            # Check relevance threshold
            if score < threshold:
                continue

            meta = doc.metadata or {}
            source_path = meta.get("source", "Unknown Note")
            title = meta.get("title", source_path)
            folder = meta.get("folder", "Root")
            chunk_id = int(meta.get("chunk_id", 0))
            tags = meta.get("tags", "")

            chunk = RetrievedChunk(
                content=doc.page_content,
                source=source_path,
                title=title,
                folder=folder,
                chunk_id=chunk_id,
                score=round(score, 4),
                tags=tags,
                metadata=meta,
            )
            retrieved_chunks.append(chunk)

            # Record unique sources for citation summary
            if source_path not in unique_sources:
                unique_sources[source_path] = {
                    "source": source_path,
                    "title": title,
                    "folder": folder,
                    "tags": tags,
                    "highest_score": round(score, 4),
                    "excerpts": [chunk.excerpt],
                }
            else:
                unique_sources[source_path]["excerpts"].append(chunk.excerpt)

        # Assemble formatted context string for LLM injection
        if not retrieved_chunks:
            return RetrievalResult(
                query=query,
                chunks=[],
                formatted_context="[No specific notes found in your vault on this topic. Please answer accurately and directly using general knowledge.]",
                sources=[],
                has_relevant_context=False,
            )

        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            block = (
                f"[Document: {chunk.title} ({chunk.source})]\n"
                f"{chunk.content.strip()}\n"
            )
            context_blocks.append(block)

        formatted_context = "\n".join(context_blocks)
        sources_list = sorted(
            list(unique_sources.values()),
            key=lambda x: x["highest_score"],
            reverse=True
        )

        return RetrievalResult(
            query=query,
            chunks=retrieved_chunks,
            formatted_context=formatted_context,
            sources=sources_list,
            has_relevant_context=True,
        )
