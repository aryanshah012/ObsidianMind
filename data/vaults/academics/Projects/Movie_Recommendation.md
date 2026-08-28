---
title: Movie Recommendation Engine Project
tags: [project, ml, recommendation-systems, collaborative-filtering, embeddings]
aliases: [Movie RecSys, CineMatch]
status: completed
created: 2026-08-01
---

# Movie Recommendation Engine Project (CineMatch)

CineMatch is a hybrid recommendation system built to provide personalized movie recommendations by fusing collaborative filtering and content-based semantic embeddings.

## Key Architecture
1. **Content-Based Filtering**:
   - Movie metadata (plot synopsis, genre, director, cast) is vectorized using [[Embeddings]] (`sentence-transformers/all-MiniLM-L6-v2`).
   - Indexed in a [[Vector_Databases]] collection for semantic plot similarity.
2. **Collaborative Filtering**:
   - Matrix Factorization using Singular Value Decomposition (SVD) on user-item rating matrices.
3. **Hybrid Ensemble**:
   - Weighted blending: $Score = 0.6 \times \text{Collaborative} + 0.4 \times \text{ContentSim}$.

## Results & Performance
- **Dataset**: MovieLens 1M (1 million ratings across 6,000 users and 4,000 movies).
- **Evaluation Metrics**:
  - RMSE: 0.864
  - Precision@10: 0.812
  - Recall@10: 0.745
- **Tech Stack**: Python, PyTorch, Scikit-Learn, ChromaDB, FastAPI, Streamlit.

## Future Improvements
- Integrate two-tower neural network architecture.
- Add real-time session-based recommendations using Recurrent Neural Networks or Transformers.
