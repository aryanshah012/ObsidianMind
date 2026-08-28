---
title: Real-Time SMS & Email Spam Detector
tags: [project, nlp, classification, scikit-learn, naive-bayes]
aliases: [Spam Guard, Spam Filter]
status: active
created: 2026-08-05
---

# Real-Time SMS & Email Spam Detector

An end-to-end NLP classification pipeline designed to filter phishing and promotional spam messages in real-time.

## Pipeline Details
1. **Text Preprocessing**:
   - Lowercasing, regex tokenization, punctuation removal.
   - Stopword removal and Porter Stemming.
2. **Feature Extraction**:
   - TF-IDF (Term Frequency - Inverse Document Frequency) with n-gram range (1, 2) and sublinear term scaling.
3. **Model Selection & Benchmarks**:
   - **Multinomial Naive Bayes (MNB)**: Best baseline for high precision (Precision: 0.992, Accuracy: 0.984).
   - **Support Vector Machines (Linear SVC)**: Accuracy: 0.988, Recall: 0.931.
   - **DistilBERT**: Accuracy: 0.993, but higher inference latency (35ms vs 1.2ms for MNB).

## Production Deployment
- Deployed as a lightweight containerized microservice via Docker and FastAPI.
- Reaches sub-5ms inference latency on standard cloud CPU instances.
