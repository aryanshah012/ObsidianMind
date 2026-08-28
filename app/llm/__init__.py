"""LLM module for ObsidianMind."""
from app.llm.model import get_llm, MockChatModel
from app.llm.prompts import (
    QUERY_ROUTER_SYSTEM_PROMPT,
    GROUNDED_RAG_SYSTEM_PROMPT,
    QUERY_CONDENSE_SYSTEM_PROMPT,
    GENERAL_SYSTEM_PROMPT,
)

__all__ = [
    "get_llm",
    "MockChatModel",
    "QUERY_ROUTER_SYSTEM_PROMPT",
    "GROUNDED_RAG_SYSTEM_PROMPT",
    "QUERY_CONDENSE_SYSTEM_PROMPT",
    "GENERAL_SYSTEM_PROMPT",
]
