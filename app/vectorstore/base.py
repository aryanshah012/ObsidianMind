"""Base Vector Store Interface."""
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any, Optional
from langchain_core.documents import Document


class BaseVectorStore(ABC):
    """Abstract interface for persistent vector store implementations."""

    @abstractmethod
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Insert or upsert document chunks into the vector store."""
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """Perform semantic similarity search for a query string."""
        pass

    @abstractmethod
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[Document, float]]:
        """Perform semantic similarity search returning (Document, similarity_score) tuples."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return total number of indexed vectors."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Delete all vectors and reset the index."""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Return collection diagnostics and metadata."""
        pass
