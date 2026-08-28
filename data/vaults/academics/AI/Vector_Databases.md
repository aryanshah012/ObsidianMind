---
title: Vector Databases
tags: [ai, database, vector-store, chromadb]
aliases: [Vector Stores, ANN Search]
created: 2026-08-16
---

# Vector Databases

A Vector Database is a specialized storage and indexing engine optimized for storing high-dimensional vector embeddings and executing Approximate Nearest Neighbor (ANN) search at scale.

## Why Traditional Databases Fall Short
Standard SQL/relational databases use B-Trees or Hash Indexes designed for exact scalar match (`WHERE id = 5`) or range queries. In contrast, vector similarity requires searching across continuous vector spaces where distance metrics must be evaluated against millions of dense floating-point arrays.

## Key Vector Indexing Algorithms
1. **HNSW (Hierarchical Navigable Small World)**:
   - Graph-based indexing algorithm.
   - Builds multi-layer proximity graphs offering logarithmic search complexity and high recall.
   - Used by ChromaDB, FAISS, and Qdrant.
2. **IVF (Inverted File Index)**:
   - Clusters vector space into Voronoi cells and searches only closest clusters.
3. **Product Quantization (PQ)**:
   - Compresses vectors to reduce memory footprint by a factor of 8x-64x.

## Vector DB Comparison
- **ChromaDB**: Native open-source, developer-friendly embedding database written in Python/C++, perfect for local application development and embedded storage.
- **FAISS (Facebook AI Similarity Search)**: Ultra-fast library for dense vector clustering and ANN search on CPU/GPU.
- **Pinecone**: Fully managed, cloud-native serverless vector database.
- **Qdrant**: Rust-based vector search engine with rich payload filtering capabilities.

## Usage in ObsidianMind
ObsidianMind uses **ChromaDB** with persistent local disk storage. Chunks generated from notes are indexed alongside rich metadata (file path, tags, heading context) to enable filtered vector similarity retrieval in [[RAG]].
