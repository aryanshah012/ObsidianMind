---
title: AI Agents & Autonomous Workflows
tags: [ai, agents, reasoning, tool-calling]
aliases: [AI Agents, Agentic AI]
created: 2026-08-18
---

# AI Agents & Autonomous Workflows

An AI Agent is an autonomous or semi-autonomous system powered by an [[LLMs]] core that perceives its environment, plans sequential actions, calls tools, and executes feedback loops to accomplish a goal.

## Key Components of an Agent
1. **Brain / Core LLM**: Performs reasoning, step-by-step planning (e.g. ReAct - Reason + Act, Chain of Thought).
2. **Memory**:
   - Short-term: Conversational context window and session state.
   - Long-term: External retrieval database or knowledge graph via [[RAG]].
3. **Tools**: External functions the agent can execute (calculators, web search, database query, vector search).
4. **Planning & Routing**: Breaking complex goals into sub-tasks and dynamically routing requests based on intent.

## Query Routing Pattern
In knowledge assistants, query routing is an agentic pattern where an intent-classification router evaluates incoming user prompts:
- If the question requires internal knowledge: Route to **Knowledge Base Retrieval**.
- If the question is conversational or general world knowledge (e.g. math, general coding): Route directly to **Direct LLM**.

This avoids redundant vector searches, reduces retrieval noise, and enhances answer quality. Query routing workflows can be explicitly structured as directed cyclic/acyclic state machines using [[LangGraph]].
