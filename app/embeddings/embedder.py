"""
Embedding model implementations supporting Google Gemini, HuggingFace, OpenAI,
and a deterministic Mock embedder for offline unit tests.
"""

import os
import hashlib
import numpy as np
from typing import List, Optional, Any
from langchain_core.embeddings import Embeddings

from app.config import settings
from app.embeddings.base import BaseEmbedder


class GoogleGenAIEmbedder(BaseEmbedder, Embeddings):
    """Google Gemini text embedding model (Ultra-low RAM, cloud-hosted)."""

    def __init__(self, model_name: str = "gemini-embedding-001", api_key: Optional[str] = None):
        self._model_name = model_name
        self._dim = 3072
        self._api_key = api_key or settings.GOOGLE_API_KEY
        if not self._api_key:
            raise ValueError(
                "GOOGLE_API_KEY must be provided in .env or settings for Google embeddings."
            )
        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google GenAI Client: {e}")

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        try:
            # Batch embedding via Google GenAI API
            model_id = self._model_name.replace("models/", "")
            results = []
            for text in texts:
                res = self._client.models.embed_content(
                    model=model_id,
                    contents=[text]
                )
                if res and res.embeddings:
                    vec = res.embeddings[0].values
                    results.append(list(vec))
                else:
                    results.append([0.0] * self._dim)
            return results
        except Exception as e:
            # Fallback to langchain_google_genai if available
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                lc_client = GoogleGenerativeAIEmbeddings(
                    model=self._model_name,
                    google_api_key=self._api_key,
                )
                return lc_client.embed_documents(texts)
            except Exception:
                raise RuntimeError(f"Google embedding API error: {e}")

    def embed_query(self, text: str) -> List[float]:
        model_id = self._model_name.replace("models/", "")
        try:
            res = self._client.models.embed_content(
                model=model_id,
                contents=[text]
            )
            if res and res.embeddings:
                return list(res.embeddings[0].values)
            return [0.0] * self._dim
        except Exception as e:
            try:
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                lc_client = GoogleGenerativeAIEmbeddings(
                    model=self._model_name,
                    google_api_key=self._api_key,
                )
                return lc_client.embed_query(text)
            except Exception:
                raise RuntimeError(f"Google embedding query error: {e}")


class HuggingFaceEmbedder(BaseEmbedder, Embeddings):
    """Local HuggingFace sentence-transformers embedder (Free, offline, fast)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._dim = 384
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            if hasattr(self.model, "get_embedding_dimension"):
                self._dim = self.model.get_embedding_dimension()
            elif hasattr(self.model, "get_sentence_embedding_dimension"):
                self._dim = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise RuntimeError(
                f"Failed to load HuggingFace embedding model '{model_name}': {e}"
            )

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode(
            text,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding.tolist()


class OpenAIEmbedder(BaseEmbedder, Embeddings):
    """OpenAI embedding model."""

    def __init__(self, model_name: str = "text-embedding-3-small", api_key: Optional[str] = None):
        self._model_name = model_name
        self._dim = 1536
        key = api_key or settings.OPENAI_API_KEY
        if not key:
            raise ValueError(
                "OPENAI_API_KEY must be provided in .env or settings for OpenAI embeddings."
            )
        try:
            from langchain_openai import OpenAIEmbeddings
            self._client = OpenAIEmbeddings(
                model=model_name,
                openai_api_key=key,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI embeddings: {e}")

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dim

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._client.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._client.embed_query(text)


class MockEmbedder(BaseEmbedder, Embeddings):
    """
    Deterministic pseudo-random embedder for lightning-fast offline unit tests.
    Generates normalized 64-dimensional vectors based on text hash.
    """

    def __init__(self, dim: int = 64):
        self._dim = dim
        self._model_name = "mock-embedder"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimension(self) -> int:
        return self._dim

    def _hash_to_vec(self, text: Any) -> List[float]:
        if isinstance(text, (list, tuple)):
            text = " ".join(str(t) for t in text)
        else:
            text = str(text)
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        vec = rng.randn(self._dim)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._hash_to_vec(t) for t in texts]

    def embed_query(self, text: Any) -> List[float]:
        return self._hash_to_vec(text)


def get_embedder(
    provider: Optional[str] = None,
    model_name: Optional[str] = None
) -> BaseEmbedder:
    """
    Factory to instantiate configured embedding model.
    Prioritizes low-memory cloud embeddings on cloud environments like Render.
    """
    prov = (provider or settings.EMBEDDING_PROVIDER).lower()
    model = model_name or settings.EMBEDDING_MODEL

    if prov == "google":
        return GoogleGenAIEmbedder(model_name=model)
    elif prov == "openai":
        return OpenAIEmbedder(model_name=model)
    elif prov == "huggingface":
        try:
            return HuggingFaceEmbedder(model_name=model)
        except Exception:
            if settings.GOOGLE_API_KEY:
                return GoogleGenAIEmbedder(model_name="gemini-embedding-001")
            return MockEmbedder()
    elif prov == "mock":
        return MockEmbedder()
    else:
        if settings.GOOGLE_API_KEY:
            return GoogleGenAIEmbedder(model_name="gemini-embedding-001")
        return MockEmbedder()
