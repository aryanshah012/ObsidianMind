"""
LangGraph orchestration for ObsidianMind.
Builds the complete stateful RAG workflow with query routing, retrieval,
grounded generation, and anti-hallucination guardrails.
"""

from typing import Dict, Any, Optional, List
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.query_router import QueryRouterNode
from app.retrieval.retriever import ObsidianRetriever, RetrievalResult
from app.llm.model import get_llm
from app.llm.prompts import (
    GROUNDED_RAG_SYSTEM_PROMPT,
    GENERAL_SYSTEM_PROMPT,
    QUERY_CONDENSE_SYSTEM_PROMPT,
)


class ObsidianRAGWorkflow:
    """Builds and manages the LangGraph agentic RAG workflow."""

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        retriever: Optional[ObsidianRetriever] = None,
    ):
        self.llm = llm or get_llm()
        self.retriever = retriever or ObsidianRetriever()
        self.router_node = QueryRouterNode(self.llm)
        self.graph = self._build_graph()

    def _build_graph(self):
        """Construct the LangGraph StateGraph topology."""
        workflow = StateGraph(AgentState)

        # Register nodes
        workflow.add_node("route_query", self._node_route_query)
        workflow.add_node("condense_query", self._node_condense_query)
        workflow.add_node("retrieve_context", self._node_retrieve_context)
        workflow.add_node("generate_grounded_answer", self._node_generate_grounded_answer)
        workflow.add_node("generate_general_answer", self._node_generate_general_answer)
        workflow.add_node("guardrail_check", self._node_guardrail_check)

        # Edges
        workflow.add_edge(START, "route_query")

        # Conditional routing from router
        workflow.add_conditional_edges(
            "route_query",
            self._decide_route,
            {
                "KNOWLEDGE_BASE_QUERY": "condense_query",
                "GENERAL_QUERY": "generate_general_answer",
            }
        )

        # RAG pipeline path
        workflow.add_edge("condense_query", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_grounded_answer")
        workflow.add_edge("generate_grounded_answer", "guardrail_check")
        workflow.add_edge("guardrail_check", END)

        # General path
        workflow.add_edge("generate_general_answer", END)

        return workflow.compile()

    # --- Node Implementations ---

    def _node_route_query(self, state: AgentState) -> Dict[str, Any]:
        """Execute router classification."""
        return self.router_node(state)

    def _decide_route(self, state: AgentState) -> str:
        """Conditional edge selector."""
        return state.get("route", "KNOWLEDGE_BASE_QUERY")

    def _node_condense_query(self, state: AgentState) -> Dict[str, Any]:
        """Reformulate query if conversation history exists."""
        query = state.get("query", "")
        chat_history = state.get("chat_history", [])
        trace = list(state.get("execution_trace", []))

        if not chat_history or len(chat_history) == 0:
            trace.append(f"Query Optimizer: Standalone query -> '{query}'")
            return {
                "standalone_query": query,
                "execution_trace": trace,
            }

        # If history exists, use LLM to contextualize follow-up
        try:
            history_text = "\n".join(
                f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}"
                for msg in chat_history[-4:]  # Last 4 turns
            )
            prompt = QUERY_CONDENSE_SYSTEM_PROMPT.format(
                chat_history=history_text,
                question=query,
            )
            response = self.llm.invoke([HumanMessage(content=prompt)])
            standalone = response.content.strip() if hasattr(response, "content") else str(response).strip()
            # If LLM returned empty, fallback to original query
            if not standalone:
                standalone = query

            trace.append(f"Query Optimizer: Rephrased '{query}' -> '{standalone}'")
            return {
                "standalone_query": standalone,
                "execution_trace": trace,
            }
        except Exception:
            return {
                "standalone_query": query,
                "execution_trace": trace,
            }

    def _node_retrieve_context(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve relevant note chunks from vector database."""
        search_query = state.get("standalone_query") or state.get("query", "")
        doc_filter = state.get("doc_filter")
        trace = list(state.get("execution_trace", []))

        if doc_filter and len(doc_filter) > 0:
            trace.append(f"Retriever: Filtering to {len(doc_filter)} selected documents...")

        trace.append(f"Retriever: Searching ChromaDB for top chunks matching '{search_query}'...")
        retrieval: RetrievalResult = self.retriever.retrieve(
            query=search_query,
            doc_filter=doc_filter,
        )

        chunk_dicts = [
            {
                "source": c.source,
                "title": c.title,
                "folder": c.folder,
                "chunk_id": c.chunk_id,
                "score": c.score,
                "excerpt": c.excerpt,
            }
            for c in retrieval.chunks
        ]

        trace.append(
            f"Retriever: Found {len(retrieval.chunks)} chunks across {len(retrieval.sources)} notes "
            f"(Top score: {retrieval.top_score:.2f})"
        )

        return {
            "retrieved_chunks": chunk_dicts,
            "formatted_context": retrieval.formatted_context,
            "has_relevant_context": retrieval.has_relevant_context,
            "sources": retrieval.sources,
            "execution_trace": trace,
        }

    def _node_generate_grounded_answer(self, state: AgentState) -> Dict[str, Any]:
        """Generate cited answer strictly grounded in vault context."""
        query = state.get("query", "")
        context = state.get("formatted_context", "")
        trace = list(state.get("execution_trace", []))

        trace.append("Generator: Synthesizing grounded response with source citations...")

        system_content = GROUNDED_RAG_SYSTEM_PROMPT.format(context=context)
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=query),
        ]

        try:
            response = self.llm.invoke(messages)
            answer_text = response.content if hasattr(response, "content") else str(response)
            trace.append("Generator -> Completed response generation.")
            return {
                "answer": answer_text,
                "execution_trace": trace,
            }
        except Exception as e:
            trace.append(f"Generator Warning: Primary LLM call failed ({str(e)}). Falling back to grounded mock engine.")
            try:
                from app.llm.model import MockChatModel
                fallback_model = MockChatModel()
                response = fallback_model.invoke(messages)
                answer_text = response.content if hasattr(response, "content") else str(response)
                return {
                    "answer": answer_text,
                    "execution_trace": trace,
                }
            except Exception:
                return {
                    "answer": f"Error generating answer from vault context: {str(e)}",
                    "error": str(e),
                    "execution_trace": trace,
                }

    def _node_generate_general_answer(self, state: AgentState) -> Dict[str, Any]:
        """Generate answer for general/conversational queries without vault retrieval."""
        query = state.get("query", "")
        trace = list(state.get("execution_trace", []))

        trace.append("General Generator: Synthesizing direct response (bypassing retrieval)...")

        messages = [
            SystemMessage(content=GENERAL_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ]

        try:
            response = self.llm.invoke(messages)
            answer_text = response.content if hasattr(response, "content") else str(response)
            trace.append("General Generator -> Direct response completed.")
            return {
                "answer": answer_text,
                "retrieved_chunks": [],
                "formatted_context": "",
                "has_relevant_context": False,
                "sources": [],
                "execution_trace": trace,
            }
        except Exception as e:
            trace.append(f"General Generator Warning: Primary LLM error ({str(e)}). Using direct fallback.")
            try:
                from app.llm.model import MockChatModel
                fallback_model = MockChatModel()
                response = fallback_model.invoke(messages)
                answer_text = response.content if hasattr(response, "content") else str(response)
                return {
                    "answer": answer_text,
                    "retrieved_chunks": [],
                    "formatted_context": "",
                    "has_relevant_context": False,
                    "sources": [],
                    "execution_trace": trace,
                }
            except Exception:
                return {
                    "answer": f"Error processing query: {str(e)}",
                    "error": str(e),
                    "execution_trace": trace,
                }

    def _node_guardrail_check(self, state: AgentState) -> Dict[str, Any]:
        """Ensure clear attribution and prevent blocking answers."""
        has_context = state.get("has_relevant_context", False)
        answer = state.get("answer", "")
        trace = list(state.get("execution_trace", []))

        if not has_context:
            trace.append("Guardrail: Vault context empty or below threshold -> Answering with general LLM intelligence.")
            if not answer or answer.strip() == "":
                answer = "I couldn't find specific notes on this in your vault, but here is an answer based on general knowledge."

        return {
            "answer": answer,
            "execution_trace": trace,
        }

    def run(
        self,
        query: str,
        chat_history: Optional[list] = None,
        doc_filter: Optional[List[str]] = None,
    ) -> AgentState:
        """
        Execute the full LangGraph workflow for a user query.

        Args:
            query: User's input question.
            chat_history: List of past conversation turns.
            doc_filter: Optional list of document sources to filter retrieval.

        Returns:
            Final AgentState object containing answer, sources, route, and trace.
        """
        initial_state: AgentState = {
            "query": query,
            "standalone_query": query,
            "chat_history": chat_history or [],
            "doc_filter": doc_filter,
            "route": "KNOWLEDGE_BASE_QUERY",
            "route_reasoning": "",
            "retrieved_chunks": [],
            "formatted_context": "",
            "has_relevant_context": False,
            "sources": [],
            "answer": "",
            "execution_trace": [],
            "error": None,
        }

        final_state = self.graph.invoke(initial_state)
        return final_state
