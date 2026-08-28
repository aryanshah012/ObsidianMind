"""
Reusable UI components for ObsidianMind Streamlit application.
"""

from typing import Dict, Any, List
import streamlit as st


def render_hero() -> None:
    """Render the application header and welcome banner."""
    st.markdown(
        """
        <div class="brand-hero">
            <h1 class="brand-title">
                <span>🧠</span> ObsidianMind
            </h1>
            <p class="brand-subtitle">
                AI-Powered Personal Knowledge Assistant grounded in your Obsidian Markdown Vault.
                Combines <strong>Agentic Query Routing (LangGraph)</strong> and <strong>Retrieval-Augmented Generation (ChromaDB)</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_badge(status: str) -> str:
    """Return HTML for real-time status pill."""
    if status.lower() == "ready":
        return '<span class="status-badge-ready"><span class="pulse-dot"></span> Ready</span>'
    return '<span class="status-badge-empty"><span class="pulse-dot"></span> Empty</span>'


def render_sidebar_status(stats: Dict[str, Any]) -> None:
    """Render the knowledge base diagnostics card in the sidebar."""
    status = stats.get("status", "Empty")
    total_notes = stats.get("total_notes", 0)
    total_chunks = stats.get("total_chunks", 0)
    last_indexed = stats.get("last_indexed_at", "Never")
    skipped = stats.get("skipped_files", 0)
    errors = stats.get("errors_count", 0)

    st.sidebar.markdown(
        f"""
        <div class="stat-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="stat-header">Vault Status</span>
                {render_status_badge(status)}
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px;">
                <div>
                    <div class="stat-header">Indexed Notes</div>
                    <div class="stat-value">{total_notes}</div>
                </div>
                <div>
                    <div class="stat-header">Vector Chunks</div>
                    <div class="stat-value">{total_chunks}</div>
                </div>
            </div>
            <div style="margin-top: 10px; font-size: 11px; color: #64748b;">
                <strong>Last Indexed:</strong> {last_indexed}<br/>
                <strong>Skipped / Errors:</strong> {skipped} / {errors}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_route_badge(route: str, latency: float = 0.0) -> None:
    """Render routing classification and latency indicator."""
    if route == "KNOWLEDGE_BASE_QUERY":
        badge_html = (
            f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">'
            f'<span class="badge-rag">🔍 Grounded in Vault Notes</span>'
            f'<span style="font-size: 11px; color: #64748b;">⏱️ {latency:.2f}s</span>'
            f'</div>'
        )
    else:
        badge_html = (
            f'<div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">'
            f'<span class="badge-general">💡 Direct General AI</span>'
            f'<span style="font-size: 11px; color: #64748b;">⏱️ {latency:.2f}s</span>'
            f'</div>'
        )
    st.markdown(badge_html, unsafe_allow_html=True)


def render_source_citations(sources: List[Dict[str, Any]]) -> None:
    """Render expandable source citation drawers with note excerpts."""
    if not sources:
        return

    with st.expander(f"📚 Source Citations ({len(sources)} Notes Referenced)", expanded=False):
        for i, src in enumerate(sources, 1):
            title = src.get("title", "Note")
            path = src.get("source", "")
            score = src.get("highest_score", 0.0)
            tags = src.get("tags", "")
            excerpts = src.get("excerpts", [])

            excerpts_html = "".join(
                f'<div class="source-excerpt">"{exc}"</div>' for exc in excerpts[:2]
            )

            st.markdown(
                f"""
                <div class="source-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div class="source-title">
                            📄 <strong>{title}</strong>
                        </div>
                        <span class="source-path">{path}</span>
                    </div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 4px;">
                        Relevance: <strong>{score:.2f}</strong> | Tags: {tags or "none"}
                    </div>
                    {excerpts_html}
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_trace_drawer(trace: List[str]) -> None:
    """Render LangGraph state machine trace for pipeline explainability."""
    if not trace:
        return

    with st.expander("🛠️ Agentic Pipeline Trace (LangGraph Steps)", expanded=False):
        steps_html = "<br/>".join(f"• {step}" for step in trace)
        st.markdown(
            f'<div class="trace-container">{steps_html}</div>',
            unsafe_allow_html=True,
        )
