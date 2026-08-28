"""
ObsidianMind Streamlit Web Application.
Main UI entrypoint providing vault upload, indexing, and chat interaction.
"""

import sys
import tempfile
from pathlib import Path
import streamlit as st

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.config import settings
from app.services.rag_service import RAGService
from app.ui.styles import get_custom_css
from app.ui.components import (
    render_hero,
    render_sidebar_status,
    render_route_badge,
    render_source_citations,
    render_trace_drawer,
)


def get_or_create_service(
    llm_provider: str,
    llm_model: str,
    top_k: int,
    score_threshold: float,
) -> RAGService:
    """Retrieve existing RAGService from session_state or instantiate a new one."""
    current_key = f"{llm_provider}_{llm_model}_{top_k}_{score_threshold}"
    
    if "rag_service" not in st.session_state or st.session_state.get("service_key") != current_key:
        try:
            st.session_state.rag_service = RAGService(
                llm_provider=llm_provider,
                llm_model=llm_model,
                top_k=top_k,
                score_threshold=score_threshold,
            )
            st.session_state.service_key = current_key
        except Exception as e:
            st.error(f"Error initializing AI engine: {str(e)}")
            # Fallback to mock if API key is missing
            st.session_state.rag_service = RAGService(
                llm_provider="mock",
                top_k=top_k,
                score_threshold=score_threshold,
            )
            st.session_state.service_key = "mock"

    return st.session_state.rag_service


def main():
    st.set_page_config(
        page_title="ObsidianMind - AI Knowledge Assistant",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Inject custom styles
    st.markdown(get_custom_css(), unsafe_allow_html=True)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ---------------------------------------------------------
    # SIDEBAR CONTROLS
    # ---------------------------------------------------------
    st.sidebar.markdown("### ⚙️ Knowledge Base Setup")

    # Vault ZIP Uploader
    uploaded_zip = st.sidebar.file_uploader(
        "Upload Obsidian Vault (ZIP)",
        type=["zip"],
        help="Upload a zipped Obsidian vault folder. Ignored files (.obsidian, media) are filtered automatically.",
    )

    # 1-Click Sample Vault Button
    col_sample1, col_sample2 = st.sidebar.columns([1, 1])
    load_sample_btn = col_sample1.button("📁 Load Demo Vault", use_container_width=True)
    clear_chat_btn = col_sample2.button("🗑️ Clear Chat", use_container_width=True)

    # Model & Retrieval Settings
    with st.sidebar.expander("🛠️ Model & Retrieval Settings", expanded=False):
        # Check available API keys
        has_google = bool(settings.GOOGLE_API_KEY)
        has_openai = bool(settings.OPENAI_API_KEY)
        has_groq = bool(settings.GROQ_API_KEY)

        provider_options = ["google", "openai", "groq", "mock"]
        default_index = 0 if has_google else (1 if has_openai else (2 if has_groq else 3))

        selected_provider = st.selectbox(
            "LLM Provider",
            options=provider_options,
            index=default_index,
            help="Select your AI model provider. Ensure the corresponding API key is in .env.",
        )

        model_defaults = {
            "google": "gemini-2.5-flash",
            "openai": "gpt-4o-mini",
            "groq": "llama-3.3-70b-versatile",
            "mock": "mock-model",
        }

        selected_model = st.text_input(
            "Model Name",
            value=model_defaults.get(selected_provider, "gemini-2.5-flash"),
        )

        top_k = st.slider("Retrieval Top-K Chunks", min_value=1, max_value=10, value=settings.RETRIEVER_TOP_K)
        score_threshold = st.slider(
            "Relevance Score Threshold",
            min_value=0.0,
            max_value=1.0,
            value=settings.RETRIEVER_SCORE_THRESHOLD,
            step=0.05,
            help="Discards chunks with cosine similarity score below this threshold.",
        )

    # Initialize Service
    service = get_or_create_service(
        llm_provider=selected_provider,
        llm_model=selected_model,
        top_k=top_k,
        score_threshold=score_threshold,
    )

    # Handle Uploaded Vault ZIP
    if uploaded_zip is not None:
        if st.session_state.get("last_uploaded_name") != uploaded_zip.name:
            with st.spinner("Extracting and indexing Obsidian vault..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
                        tmp.write(uploaded_zip.getbuffer())
                        tmp_path = Path(tmp.name)

                    result = service.ingest_zip_vault(tmp_path)
                    st.session_state.last_uploaded_name = uploaded_zip.name
                    st.sidebar.success(
                        f"Indexed {result.total_notes_found} notes into {result.total_chunks_created} chunks!"
                    )
                except Exception as e:
                    st.sidebar.error(f"Ingestion failed: {str(e)}")

    # Handle Load Sample Vault
    if load_sample_btn:
        with st.spinner("Loading and indexing sample Obsidian vault..."):
            try:
                result = service.load_sample_vault()
                st.sidebar.success(
                    f"Sample vault loaded: {result.total_notes_found} notes, {result.total_chunks_created} chunks!"
                )
            except Exception as e:
                st.sidebar.error(f"Failed to load sample vault: {str(e)}")

    # Handle Clear Chat
    if clear_chat_btn:
        st.session_state.messages = []
        st.rerun()

    # Rebuild Index Button
    if st.sidebar.button("🔄 Reset Vector Database", use_container_width=True):
        service.clear_vault()
        st.sidebar.info("Vector database cleared.")
        st.rerun()

    # Render Sidebar Diagnostics Card
    vault_stats = service.get_stats()
    render_sidebar_status(vault_stats)

    # ---------------------------------------------------------
    # MAIN CHAT AREA
    # ---------------------------------------------------------
    render_hero()

    # Suggestion Chips if no chat history
    if not st.session_state.messages:
        st.markdown("**💡 Try these example questions:**")
        cols = st.columns(4)
        suggestions = [
            "Explain RAG from my notes",
            "Compare RAG and fine-tuning",
            "What are the results of CineMatch project?",
            "What is 25 * 4?",
        ]
        for idx, (col, sug) in enumerate(zip(cols, suggestions)):
            if col.button(sug, key=f"sug_{idx}", use_container_width=True):
                st.session_state.pending_prompt = sug
                st.rerun()

    # Render existing conversation
    for msg in st.session_state.messages:
        role = msg["role"]
        with st.chat_message(role, avatar="🧑‍💻" if role == "user" else "🧠"):
            if role == "assistant":
                route = msg.get("route", "KNOWLEDGE_BASE_QUERY")
                latency = msg.get("latency", 0.0)
                render_route_badge(route, latency)

            st.markdown(msg["content"])

            if role == "assistant":
                sources = msg.get("sources", [])
                if sources:
                    render_source_citations(sources)
                trace = msg.get("trace", [])
                if trace:
                    render_trace_drawer(trace)

    # User Input
    user_prompt = st.chat_input("Ask a question about your Obsidian vault notes...")

    # Check for prompt from suggestion chips
    if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
        user_prompt = st.session_state.pending_prompt
        del st.session_state.pending_prompt

    if user_prompt:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_prompt)

        # Prepare chat history format for multi-turn context
        chat_history = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]

        # Generate response
        with st.chat_message("assistant", avatar="🧠"):
            with st.spinner("Analyzing query and searching notes..."):
                try:
                    response_data = service.ask(
                        query=user_prompt,
                        chat_history=chat_history,
                    )
                    answer = response_data.get("answer", "")
                    route = response_data.get("route", "KNOWLEDGE_BASE_QUERY")
                    sources = response_data.get("sources", [])
                    trace = response_data.get("execution_trace", [])
                    latency = response_data.get("latency_sec", 0.0)

                    render_route_badge(route, latency)
                    st.markdown(answer)

                    if sources:
                        render_source_citations(sources)

                    if trace:
                        render_trace_drawer(trace)

                    # Append to session history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "route": route,
                        "sources": sources,
                        "trace": trace,
                        "latency": latency,
                    })

                except Exception as e:
                    error_msg = f"⚠️ Error processing your request: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "route": "GENERAL_QUERY",
                        "sources": [],
                        "trace": [f"Error: {e}"],
                        "latency": 0.0,
                    })


if __name__ == "__main__":
    main()
