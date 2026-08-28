---
title: Large Language Models (LLMs)
tags: [ai, nlp, llm, transformers]
aliases: [LLMs, Foundation Models]
created: 2026-08-10
---

# Large Language Models (LLMs)

Large Language Models (LLMs) are deep learning neural networks based on the **Transformer architecture** (introduced in "Attention Is All You Need", Vaswani et al., 2017). They are trained on vast corpora of text using self-supervised objectives (such as autoregressive next-token prediction).

## Core Mechanisms
1. **Self-Attention**: Computes dynamic relationships between all tokens in a sequence using Query ($Q$), Key ($K$), and Value ($V$) matrices:
   $$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
2. **Positional Encodings**: Injects token position information (e.g., RoPE - Rotary Position Embeddings).
3. **Layer Normalization and Residual Connections**: Facilitate training deep networks with hundreds of layers.

## Pretraining vs Post-Training
- **Pretraining**: Predict next token over trillions of tokens (creates the base foundation model).
- **Instruction Tuning (SFT)**: Supervised fine-tuning on high-quality instruction-response pairs.
- **Alignment (RLHF / DPO)**: Reinforcement Learning from Human Feedback or Direct Preference Optimization to ensure helpfulness and harmlessness.

## Challenges & Limitations
- **Hallucination**: Generating plausible-sounding but factually incorrect statements.
- **Knowledge Cutoff**: Base weights cannot access information after training completed.
- **Context Window Bottleneck**: Processing extremely long documents can lead to "needle in a haystack" retrieval degradation and high computational cost.

## Solutions to Limitations
To ground LLMs in private or dynamic real-time data, we combine them with [[RAG]] (Retrieval-Augmented Generation) and [[Agents]] for multi-step reasoning.
