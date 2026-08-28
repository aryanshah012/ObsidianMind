"""
LangGraph AgentState definitions for the ObsidianMind workflow.
"""

from typing import TypedDict, List, Dict, Any, Optional, Literal


class AgentState(TypedDict):
    """Represents the mutable state throughout the LangGraph workflow execution."""
    
    # Input user query
    query: str
    
    # Reformulated query with conversation context for retrieval
    standalone_query: str
    
    # Multi-turn conversational history: list of {"role": "user"|"assistant", "content": "..."}
    chat_history: List[Dict[str, str]]
    
    # Optional subset filter of documents to retrieve from
    doc_filter: Optional[List[str]]
    
    # Routing decision
    route: Literal["KNOWLEDGE_BASE_QUERY", "GENERAL_QUERY"]
    route_reasoning: str
    
    # Retrieval outputs
    retrieved_chunks: List[Dict[str, Any]]
    formatted_context: str
    has_relevant_context: bool
    sources: List[Dict[str, Any]]
    
    # Generation outputs
    answer: str
    
    # Execution telemetry & explainability
    execution_trace: List[str]
    error: Optional[str]
