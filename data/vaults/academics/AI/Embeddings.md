---
title: Text Embeddings
tags: [ai, embeddings, vectors, nlp]
aliases: [Dense Embeddings, Vector Representations]
created: 2026-08-14
---

# Text Embeddings

A text embedding is a numerical representation of linguistic semantics as a high-dimensional dense vector of floating-point numbers ($\mathbb{R}^d$, typically $d \in [384, 1536, 3072]$). 

In vector space, texts with similar conceptual meaning are situated geometrically close to each other.

## How Embeddings Work
Dense embedding models map arbitrary strings of text into a normalized embedding space where geometric distance correlates directly with semantic similarity.

### Common Distance Metrics
1. **Cosine Similarity**:
   $$\text{CosineSim}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
   Measures the cosine of the angle between vectors (invariant to vector length when normalized).
2. **Dot Product (Inner Product)**:
   $$\text{IP}(\mathbf{u}, \mathbf{v}) = \sum_{i=1}^d u_i v_i$$
   Equal to cosine similarity when vectors are $L_2$-normalized.
3. **Euclidean Distance ($L_2$)**:
   $$\text{Distance}_{L_2}(\mathbf{u}, \mathbf{v}) = \sqrt{\sum_{i=1}^d (u_i - v_i)^2}$$

## Popular Embedding Models
- **all-MiniLM-L6-v2**: Fast 384-dimensional local sentence transformer model, optimal for local and CPU execution.
- **text-embedding-004 (Google)**: 768-dimensional multimodal/text embedding model optimized for retrieval.
- **text-embedding-3-small / large (OpenAI)**: 1536/3072-dimensional embeddings with dimension truncation support.
- **BGE (BAAI General Embeddings)**: State-of-the-art open-source embeddings with strong cross-lingual and retrieval performance.

## Role in RAG
Embeddings are the bridge between raw textual notes in an Obsidian vault and dense vector indexing in [[Vector_Databases]]. Without high quality embeddings, semantic retrieval in [[RAG]] fails.
