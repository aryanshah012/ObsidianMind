"""
Agentic Query Router Node for LangGraph.
Classifies user intent between KNOWLEDGE_BASE_QUERY and GENERAL_QUERY.
"""

import json
import re
from typing import Dict, Any
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.language_models.chat_models import BaseChatModel

from app.agents.state import AgentState
from app.llm.prompts import QUERY_ROUTER_SYSTEM_PROMPT


def extract_json(text: str) -> Dict[str, Any]:
    """Extract and parse JSON object from LLM response text."""
    # Strip markdown code fences if present
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
    
    # Try direct parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # Try searching for JSON-like substring
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    return {}


class QueryRouterNode:
    """Classifies incoming query intent using LLM reasoning."""

    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        query = state.get("query", "").strip()
        trace = list(state.get("execution_trace", []))
        trace.append("Router: Evaluating query intent...")

        # Fast heuristic checks for instant greeting, pure math, or coding queries
        query_lower = query.lower()
        if any(query_lower.startswith(g) for g in ["hi", "hello", "hey", "who are you", "what can you do", "help"]):
            trace.append("Router -> Fast Path: Classified as GENERAL_QUERY (greeting)")
            return {
                "route": "GENERAL_QUERY",
                "route_reasoning": "Conversational greeting",
                "execution_trace": trace,
            }

        # Check for pure arithmetic like 'what is 2+2', '786*22', 'calculate 50*20'
        if re.search(r"\b(?:\d+[\s\+\-\*\/\^\(\)\.\%x×÷]+\d+)\b", query_lower) or re.match(r"^(?:what\s+is|calculate|solve|evaluate|compute)?\s*[\d\s\+\-\*\/\^\(\)\.\%x×÷]+\??$", query_lower):
            trace.append("Router -> Fast Path: Classified as GENERAL_QUERY (arithmetic)")
            return {
                "route": "GENERAL_QUERY",
                "route_reasoning": "Basic arithmetic calculation",
                "execution_trace": trace,
            }

        # Check for generic programming / coding requests that don't refer to notes
        if any(query_lower.startswith(c) for c in ["write a python", "write python", "write a function", "write code", "implement a function", "how to write in python"]):
            trace.append("Router -> Fast Path: Classified as GENERAL_QUERY (generic coding)")
            return {
                "route": "GENERAL_QUERY",
                "route_reasoning": "Generic programming question",
                "execution_trace": trace,
            }

        messages = [
            SystemMessage(content=QUERY_ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=f"User Query: {query}")
        ]

        try:
            response = self.llm.invoke(messages)
            response_text = response.content if hasattr(response, "content") else str(response)
            parsed = extract_json(response_text)

            route = parsed.get("route", "").strip().upper()
            reasoning = parsed.get("reasoning", "LLM intent classification")

            if route not in ["KNOWLEDGE_BASE_QUERY", "GENERAL_QUERY"]:
                # Fallback heuristic
                if "GENERAL_QUERY" in response_text:
                    route = "GENERAL_QUERY"
                else:
                    route = "KNOWLEDGE_BASE_QUERY"

            trace.append(f"Router -> Classified as {route} ({reasoning})")
            return {
                "route": route,
                "route_reasoning": reasoning,
                "execution_trace": trace,
            }

        except Exception as e:
            # Safe default fallback to knowledge base search
            trace.append(f"Router -> Defaulted to Knowledge Base Query")
            return {
                "route": "KNOWLEDGE_BASE_QUERY",
                "route_reasoning": "Standard knowledge base retrieval fallback",
                "execution_trace": trace,
            }
