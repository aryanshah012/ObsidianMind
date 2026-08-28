"""
Configuration management for ObsidianMind.
Loads environment variables, validates settings, and provides centralized configuration.
"""

import os
from pathlib import Path
from typing import Literal, Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    """Application configuration settings."""

    # Project metadata
    APP_NAME: str = "ObsidianMind"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Base Paths
    BASE_DIR: Path = BASE_DIR
    DATA_DIR: Path = BASE_DIR / "data"
    SAMPLE_VAULT_DIR: Path = BASE_DIR / "data" / "sample_vault"
    SAMPLE_VAULT_ZIP: Path = BASE_DIR / "data" / "sample_vault.zip"
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    EXTRACTED_DIR: Path = BASE_DIR / "data" / "extracted"

    # LLM Settings
    LLM_PROVIDER: Literal["google", "openai", "groq", "ollama"] = Field(
        default="google", description="LLM provider"
    )
    GOOGLE_API_KEY: Optional[str] = Field(default=None)
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    GROQ_API_KEY: Optional[str] = Field(default=None)
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    LLM_MODEL: str = "gemini-3.5-flash-lite"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 1500

    # Embedding Settings
    EMBEDDING_PROVIDER: Literal["huggingface", "google", "openai", "mock"] = Field(
        default="google" if os.getenv("GOOGLE_API_KEY") else "huggingface",
        description="Embedding provider"
    )
    EMBEDDING_MODEL: str = "gemini-embedding-001" if os.getenv("GOOGLE_API_KEY") else "all-MiniLM-L6-v2"

    # Vector Store Settings
    CHROMA_PERSIST_DIRECTORY: str = str(BASE_DIR / "chroma_db")
    CHROMA_COLLECTION_NAME: str = "obsidian_vault"

    # Chunking Configuration
    CHUNK_SIZE: int = 600
    CHUNK_OVERLAP: int = 100

    # Retrieval Configuration
    RETRIEVER_TOP_K: int = 4
    RETRIEVER_SCORE_THRESHOLD: float = 0.35

    # Router Configuration
    ROUTER_MODEL: Optional[str] = None  # Falls back to LLM_MODEL if None

    # Ingestion Constraints & Security
    MAX_FILE_SIZE_MB: int = 25  # Max ZIP upload size
    MAX_CHUNK_LIMIT: int = 10000

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_effective_router_model(self) -> str:
        """Return the model to use for query routing."""
        return self.ROUTER_MODEL or self.LLM_MODEL

    def ensure_directories(self) -> None:
        """Create necessary working directories if they do not exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.SAMPLE_VAULT_DIR.mkdir(parents=True, exist_ok=True)
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        self.EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
        Path(self.CHROMA_PERSIST_DIRECTORY).mkdir(parents=True, exist_ok=True)


# Global settings singleton
settings = Settings()
settings.ensure_directories()
