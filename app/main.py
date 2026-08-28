"""
Main entry point for ObsidianMind.
Supports both interactive Web UI (Streamlit) and Command Line Interface (CLI).
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.config import settings
from app.services.rag_service import RAGService
from app.ui.streamlit_app import main as run_streamlit_app


def run_cli_query(query: str, sample_if_empty: bool = True) -> None:
    """Execute a query from the command line."""
    print(f"\n🧠 Initializing ObsidianMind Engine...")
    service = RAGService()

    # Check if index has documents
    if service.vector_store.count() == 0 and sample_if_empty:
        print(f"📦 Index is currently empty. Loading sample vault from {settings.SAMPLE_VAULT_DIR}...")
        res = service.load_sample_vault()
        print(f"✓ Indexed {res.total_notes_found} notes ({res.total_chunks_created} chunks)")

    print(f"\n❓ Question: {query}")
    print("⏳ Processing through LangGraph query router and retriever...")
    
    result = service.ask(query)
    
    print("\n" + "=" * 60)
    print(f"ROUTE: {result['route']} (Latency: {result['latency_sec']}s)")
    print("=" * 60)
    print(f"\nANSWER:\n{result['answer']}\n")

    if result.get("sources"):
        print("=" * 60)
        print(f"SOURCES ({len(result['sources'])} notes):")
        for src in result["sources"]:
            print(f"- 📄 {src['title']} ({src['source']}) [Score: {src['highest_score']}]")
            for exc in src.get("excerpts", [])[:1]:
                print(f"  Excerpt: \"{exc}\"")
        print("=" * 60)


def run_cli_index(vault_path_str: str) -> None:
    """Index an Obsidian vault directory via CLI."""
    vault_path = Path(vault_path_str).resolve()
    print(f"\n📁 Indexing Obsidian vault from: {vault_path}")
    service = RAGService()

    if vault_path.suffix == ".zip":
        result = service.ingest_zip_vault(vault_path)
    else:
        result = service.ingest_directory_vault(vault_path)

    print(f"\n✓ Indexing complete!")
    print(f"  • Notes found: {result.total_notes_found}")
    print(f"  • Chunks created: {result.total_chunks_created}")
    print(f"  • Skipped files: {len(result.skipped_files)}")
    if result.errors:
        print(f"  • Errors: {result.errors}")


def run_server(port: int = 8000, host: str = "0.0.0.0") -> None:
    """Launch the FastAPI server and serve the Lovable Web UI."""
    import os
    import uvicorn
    env_port = os.getenv("PORT")
    final_port = int(env_port) if env_port else port
    print("\n" + "=" * 65)
    print("🧠 Starting ObsidianMind - Lovable Web Application")
    print("=" * 65)
    print(f"🚀 Web Interface: http://{host}:{final_port}")
    print(f"📡 API Docs:      http://{host}:{final_port}/docs")
    print("=" * 65 + "\n")
    uvicorn.run("app.api.server:app", host=host, port=final_port, reload=False)


def main():
    parser = argparse.ArgumentParser(description="ObsidianMind - AI Knowledge Assistant")
    parser.add_argument("--query", "-q", type=str, help="Ask a question via CLI")
    parser.add_argument("--index", "-i", type=str, help="Index an Obsidian vault folder or ZIP")
    parser.add_argument("--stats", "-s", action="store_true", help="Print vector database stats")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to run web server on")
    parser.add_argument("--streamlit", action="store_true", help="Run Streamlit Web UI instead")
    parser.add_argument("--server", action="store_true", help="Run FastAPI backend server")

    # If run via `streamlit run app/main.py`
    is_streamlit = any("streamlit" in arg for arg in sys.argv)
    
    if is_streamlit:
        run_streamlit_app()
        return

    # If run with no args: start the Lovable Web UI
    if len(sys.argv) == 1:
        run_server()
        return

    args = parser.parse_args()

    if args.query:
        run_cli_query(args.query)
    elif args.index:
        run_cli_index(args.index)
    elif args.stats:
        service = RAGService()
        stats = service.get_stats()
        print("\n📊 Knowledge Base Diagnostics:")
        for k, v in stats.items():
            print(f"  • {k}: {v}")
    elif args.streamlit:
        run_streamlit_app()
    elif args.server:
        run_server(port=args.port)
    else:
        run_server(port=args.port)


if __name__ == "__main__":
    main()

