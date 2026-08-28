---
title: Retrieval-Augmented Generation (RAG)
tags: [ai, rag, vector-search, information-retrieval]
aliases: [RAG, Grounding]
created: 2026-08-12
---

# Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is an AI framework that combines external information retrieval with neural text generation (Lewis et al., 2020). Instead of relying exclusively on parametric memory stored in model weights, RAG retrieves non-parametric knowledge from an external database to ground the LLM's answers in factual source data.

## The Standard RAG Architecture
A standard RAG pipeline operates in two distinct phases:

### 1. Ingestion Phase
1. **Document Loading**: Extract raw text from files (Markdown, PDF, HTML, Obsidian notes).
2. **Text Cleaning**: Strip unnecessary noise, syntax artifacts, and formatting issues.
3. **Chunking**: Split long documents into semantically coherent segments (e.g., 500-1000 characters with 100 character overlap).
4. **Embedding Generation**: Convert text chunks into dense continuous vector representations via [[Embeddings]].
5. **Vector Store Ingestion**: Store vectors and corresponding metadata into a database like [[Vector_Databases]] (e.g., ChromaDB).

### 2. Query / Retrieval Phase
1. **User Query**: User submits a natural language question.
2. **Query Embedding**: The query is transformed into a dense vector using the same embedding model.
3. **Similarity Search**: Top-$k$ nearest chunks are retrieved using distance metrics (Cosine Similarity, Euclidean Distance, or Dot Product).
4. **Context Construction**: Retrieved chunks and metadata citations are formatted into an augmented prompt.
5. **LLM Generation**: The [[LLMs]] generates a grounded, cited response strictly adhering to the provided context.

## Comparison: RAG vs Fine-Tuning
| Feature | Retrieval-Augmented Generation (RAG) | Fine-Tuning |
| :--- | :--- | :--- |
| **Knowledge Source** | Dynamic external data store | Static internal model weights |
| **Update Latency** | Instant (add/update document) | Slow (requires retraining / epochs) |
| **Cost & Compute** | Low (database query & embedding) | High (GPU compute & training time) |
| **Explainability** | High (exact source citation & paths) | Black box (opaque model weights) |
| **Hallucination Risk**| Minimal when properly prompted | Moderate (prone to confident errors) |
| **Primary Use Case** | Knowledge bases, private docs, FAQs | Style adaptation, syntax, reasoning skills |

## Advanced Techniques
- **Query Routing**: Deciding whether retrieval is necessary using [[LangGraph]] or lightweight classification.
- **Hypothetical Document Embeddings (HyDE)**: Generating a hypothetical answer before retrieval.
- **Reranking**: Using cross-encoders to score and reorder top candidates.
- **Contextual Chunk Headers**: Prepending document title and section headings to every chunk.
