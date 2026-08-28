---
title: LangGraph Workflow Framework
tags: [ai, langgraph, langchain, agents, workflows]
aliases: [LangGraph, StateGraph]
created: 2026-08-20
---

# LangGraph Workflow Framework

LangGraph is an orchestration library built on top of LangChain designed for developing robust, stateful, multi-actor applications with LLMs. Unlike traditional linear chains (like LCEL or sequential chains), LangGraph models workflows as **state machines** with nodes, edges, and conditional branches.

## Core Concepts
1. **State (`AgentState`)**: A typed schema (often a `TypedDict` or Pydantic model) that holds the shared data structure updated by nodes as execution progresses.
2. **Nodes**: Python functions or callables that accept the current state, perform computation (like invoking an LLM or querying a database), and return state updates.
3. **Edges**: Connections between nodes determining the execution order.
4. **Conditional Edges**: Dynamic routing functions that evaluate state fields and determine which branch or node to execute next.
5. **Persistence & Checkpointing**: Built-in mechanisms to persist state across turns for interactive human-in-the-loop workflows.

## ObsidianMind Graph Topology
ObsidianMind implements a lightweight, deterministic LangGraph workflow:

```
[START]
   │
   ▼
[Query Router Node]
   │
   ├── (KNOWLEDGE_BASE_QUERY) ──► [Retriever Node] ──► [Grounded Generator Node] ──┐
   │                                                                               │
   └── (GENERAL_QUERY) ─────────► [General Generator Node] ────────────────────────┤
                                                                                   ▼
                                                                           [Guardrail Node]
                                                                                   │
                                                                                   ▼
                                                                                 [END]
```

## Benefits of LangGraph for RAG
- **Explainability**: Every step in the decision process is logged as a discrete node execution.
- **Modularity**: Nodes can be swapped, tested in isolation, or updated without altering the surrounding pipeline.
- **Extensibility**: Allows easy integration of corrective RAG (CRAG), self-reflection, or multi-hop retrieval loops.
