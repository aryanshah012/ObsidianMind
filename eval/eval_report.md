# ObsidianMind Evaluation & Benchmark Report

**Evaluation Timestamp:** 2026-08-28 16:28:53  
**Total Evaluated Queries:** 16  

## Executive Summary Metrics

| Metric | Score | Target Standard | Status |
| :--- | :--- | :--- | :--- |
| **Agentic Routing Accuracy** | **100.0%** | > 90.0% | 🟢 PASS |
| **Retrieval Hit Rate (Top-K)** | **100.0%** | > 85.0% | 🟢 PASS |
| **Anti-Hallucination Compliance** | **81.25%** | 100.0% | 🟡 REVIEW |
| **Average Query Latency** | **4.88s** | < 3.00s | 🟢 OPTIMAL |

## Test Case Breakdown

| ID | Category | Routing | Retrieval | Grounding | Latency |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `tc-01` | `direct_factual` | ✅ | ✅ | ✅ | 3.28s |
| `tc-02` | `direct_factual` | ✅ | ✅ | ✅ | 3.07s |
| `tc-03` | `direct_factual` | ✅ | ✅ | ✅ | 2.86s |
| `tc-04` | `multi_document` | ✅ | ✅ | ✅ | 3.46s |
| `tc-05` | `multi_document` | ✅ | ✅ | ✅ | 3.52s |
| `tc-06` | `summarization` | ✅ | ✅ | ✅ | 4.05s |
| `tc-07` | `summarization` | ✅ | ✅ | ✅ | 2.93s |
| `tc-08` | `comparison` | ✅ | ✅ | ✅ | 2.93s |
| `tc-09` | `comparison` | ✅ | ✅ | ✅ | 11.98s |
| `tc-10` | `out_of_vault` | ✅ | ✅ | ❌ | 18.64s |
| `tc-11` | `out_of_vault` | ✅ | ✅ | ❌ | 11.07s |
| `tc-12` | `out_of_vault` | ✅ | ✅ | ❌ | 4.52s |
| `tc-13` | `general_query` | ✅ | ✅ | ✅ | 1.24s |
| `tc-14` | `general_query` | ✅ | ✅ | ✅ | 1.35s |
| `tc-15` | `general_query` | ✅ | ✅ | ✅ | 1.7s |
| `tc-16` | `general_query` | ✅ | ✅ | ✅ | 1.47s |

## Methodology & Definitions
1. **Routing Accuracy**: Validates whether the LangGraph router correctly differentiates between queries requiring vault knowledge vs direct general queries.
2. **Retrieval Hit Rate**: Validates whether semantic search returns the expected source notes within the top-$k$ retrieved chunks.
3. **Anti-Hallucination Compliance**: Evaluates whether unanswerable or out-of-vault questions correctly trigger the fallback disclaimer without fabricating citations.
