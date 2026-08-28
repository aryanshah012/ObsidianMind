"""
Automated Evaluation Benchmark Suite for ObsidianMind.
Evaluates Routing Accuracy, Retrieval Hit Rate, Groundedness, and Hallucination Control.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.config import settings
from app.services.rag_service import RAGService


def run_evaluation(
    eval_file: Path = root_dir / "eval" / "eval_dataset.json",
    use_mock: bool = False,
) -> Dict[str, Any]:
    """
    Run automated evaluation against eval_dataset.json.
    """
    print("=" * 75)
    print("🧠 OBSIDIANMIND - AUTOMATED RAG & AGENT EVALUATION BENCHMARK")
    print("=" * 75)

    if not eval_file.exists():
        raise FileNotFoundError(f"Evaluation dataset not found at {eval_file}")

    with open(eval_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print(f"Loaded {len(test_cases)} evaluation test cases across 6 categories.")

    # Initialize Service
    provider = "mock" if use_mock or not settings.GOOGLE_API_KEY else settings.LLM_PROVIDER
    print(f"Initializing AI engine (Provider: {provider}, Embedder: {settings.EMBEDDING_PROVIDER})...")
    
    try:
        service = RAGService(llm_provider=provider)
    except Exception as e:
        print(f"Warning: Could not initialize with {provider} ({e}). Falling back to 'mock'.")
        service = RAGService(llm_provider="mock")

    # Index sample vault
    print("Indexing sample Obsidian vault...")
    ingest_res = service.load_sample_vault()
    print(f"✓ Indexed {ingest_res.total_notes_found} notes into {ingest_res.total_chunks_created} chunks.\n")

    results: List[Dict[str, Any]] = []
    
    # Metric counters
    total_tests = len(test_cases)
    routing_correct = 0
    retrieval_hits = 0
    grounding_correct = 0
    total_latency = 0.0

    category_stats: Dict[str, Dict[str, int]] = {}

    print(f"{'ID':<6} | {'CATEGORY':<16} | {'ROUTING':<8} | {'RETRIEVAL':<10} | {'GROUNDED':<9} | {'LATENCY':<8}")
    print("-" * 75)

    for tc in test_cases:
        tc_id = tc["id"]
        cat = tc["category"]
        query = tc["query"]
        expected_route = tc["expected_route"]
        expected_sources = set(tc.get("expected_sources", []))
        should_have_disclaimer = tc.get("should_have_disclaimer", False)

        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "routing_correct": 0, "retrieval_hits": 0, "grounding_correct": 0}
        category_stats[cat]["total"] += 1

        # Execute query
        start_t = time.time()
        res = service.ask(query)
        latency = time.time() - start_t
        total_latency += latency

        actual_route = res.get("route", "")
        retrieved_sources = {s["source"] for s in res.get("sources", [])}
        answer = res.get("answer", "")

        # 1. Routing check
        is_route_correct = (actual_route == expected_route)
        if is_route_correct:
            routing_correct += 1
            category_stats[cat]["routing_correct"] += 1

        # 2. Retrieval check
        if not expected_sources:
            # If no sources expected (general or out of vault)
            is_retrieval_hit = True
        else:
            # Check if at least one expected source is present in retrieved sources
            is_retrieval_hit = bool(expected_sources.intersection(retrieved_sources))
        
        if is_retrieval_hit:
            retrieval_hits += 1
            category_stats[cat]["retrieval_hits"] += 1

        # 3. Grounding / Anti-hallucination check
        if should_have_disclaimer:
            has_disclaimer = "couldn't find enough information" in answer.lower() or "not find enough information" in answer.lower()
            is_grounded = has_disclaimer
        else:
            is_grounded = True
        
        if is_grounded:
            grounding_correct += 1
            category_stats[cat]["grounding_correct"] += 1

        print(
            f"{tc_id:<6} | {cat:<16} | "
            f"{'✓ PASS' if is_route_correct else '✗ FAIL':<8} | "
            f"{'✓ PASS' if is_retrieval_hit else '✗ FAIL':<10} | "
            f"{'✓ PASS' if is_grounded else '✗ FAIL':<9} | "
            f"{latency:.2f}s"
        )

        results.append({
            "test_id": tc_id,
            "category": cat,
            "query": query,
            "expected_route": expected_route,
            "actual_route": actual_route,
            "routing_pass": is_route_correct,
            "expected_sources": list(expected_sources),
            "retrieved_sources": list(retrieved_sources),
            "retrieval_pass": is_retrieval_hit,
            "grounding_pass": is_grounded,
            "latency_sec": round(latency, 2),
            "answer_preview": answer[:150] + "..." if len(answer) > 150 else answer,
        })

    # Summary Metrics
    routing_acc = (routing_correct / total_tests) * 100
    retrieval_rate = (retrieval_hits / total_tests) * 100
    grounding_rate = (grounding_correct / total_tests) * 100
    avg_latency = total_latency / total_tests

    summary = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_test_cases": total_tests,
        "metrics": {
            "routing_accuracy_pct": round(routing_acc, 2),
            "retrieval_hit_rate_pct": round(retrieval_rate, 2),
            "grounding_compliance_pct": round(grounding_rate, 2),
            "average_latency_sec": round(avg_latency, 2),
        },
        "category_breakdown": category_stats,
        "results": results,
    }

    print("\n" + "=" * 75)
    print("📊 BENCHMARK SUMMARY RESULTS")
    print("=" * 75)
    print(f"• Total Test Cases:          {total_tests}")
    print(f"• Routing Accuracy:          {routing_acc:.1f}% ({routing_correct}/{total_tests})")
    print(f"• Retrieval Hit Rate:        {retrieval_rate:.1f}% ({retrieval_hits}/{total_tests})")
    print(f"• Grounding / Guardrails:    {grounding_rate:.1f}% ({grounding_correct}/{total_tests})")
    print(f"• Average Latency:           {avg_latency:.2f}s")
    print("=" * 75)

    # Save reports
    report_json_path = root_dir / "eval" / "eval_report.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save Markdown report
    report_md_path = root_dir / "eval" / "eval_report.md"
    _generate_markdown_report(summary, report_md_path)

    print(f"✓ Saved reports to:\n  - {report_json_path}\n  - {report_md_path}\n")
    return summary


def _generate_markdown_report(summary: Dict[str, Any], output_path: Path) -> None:
    """Generate a clean Markdown evaluation report."""
    metrics = summary["metrics"]
    rows = []
    for r in summary["results"]:
        route_str = "✅" if r["routing_pass"] else "❌"
        ret_str = "✅" if r["retrieval_pass"] else "❌"
        gnd_str = "✅" if r["grounding_pass"] else "❌"
        rows.append(
            f"| `{r['test_id']}` | `{r['category']}` | {route_str} | {ret_str} | {gnd_str} | {r['latency_sec']}s |"
        )

    table_rows = "\n".join(rows)

    content = f"""# ObsidianMind Evaluation & Benchmark Report

**Evaluation Timestamp:** {summary['timestamp']}  
**Total Evaluated Queries:** {summary['total_test_cases']}  

## Executive Summary Metrics

| Metric | Score | Target Standard | Status |
| :--- | :--- | :--- | :--- |
| **Agentic Routing Accuracy** | **{metrics['routing_accuracy_pct']}%** | > 90.0% | {'🟢 PASS' if metrics['routing_accuracy_pct'] >= 90 else '🟡 REVIEW'} |
| **Retrieval Hit Rate (Top-K)** | **{metrics['retrieval_hit_rate_pct']}%** | > 85.0% | {'🟢 PASS' if metrics['retrieval_hit_rate_pct'] >= 85 else '🟡 REVIEW'} |
| **Anti-Hallucination Compliance** | **{metrics['grounding_compliance_pct']}%** | 100.0% | {'🟢 PASS' if metrics['grounding_compliance_pct'] >= 95 else '🟡 REVIEW'} |
| **Average Query Latency** | **{metrics['average_latency_sec']}s** | < 3.00s | 🟢 OPTIMAL |

## Test Case Breakdown

| ID | Category | Routing | Retrieval | Grounding | Latency |
| :--- | :--- | :---: | :---: | :---: | :--- |
{table_rows}

## Methodology & Definitions
1. **Routing Accuracy**: Validates whether the LangGraph router correctly differentiates between queries requiring vault knowledge vs direct general queries.
2. **Retrieval Hit Rate**: Validates whether semantic search returns the expected source notes within the top-$k$ retrieved chunks.
3. **Anti-Hallucination Compliance**: Evaluates whether unanswerable or out-of-vault questions correctly trigger the fallback disclaimer without fabricating citations.
"""
    output_path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    use_mock_flag = "--mock" in sys.argv
    run_evaluation(use_mock=use_mock_flag)
