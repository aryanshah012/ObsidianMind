"""
Unit tests for Multi-Vault & Workspace Management.
Verifies vault creation, isolation, vector store switching, and deletion.
"""

import pytest
from pathlib import Path
from langchain_core.documents import Document

from app.services.vault_manager import VaultManager
from app.embeddings.embedder import MockEmbedder
from app.vectorstore.chroma_store import ChromaVectorStore
from app.services.rag_service import RAGService


def test_vault_manager_crud(tmp_path):
    storage_file = tmp_path / "vaults_test.json"
    manager = VaultManager(storage_path=storage_file)

    # Initial defaults
    vaults = manager.list_vaults()
    assert len(vaults) >= 1
    assert any(v["id"] == "default" for v in vaults)
    assert manager.get_active_vault().id == "default"

    # Create new workspace
    new_v = manager.create_vault(
        name="Physics 101",
        description="Classical mechanics and thermodynamics",
        icon="BookOpen",
        color="#3B82F6",
    )
    assert new_v.id == "physics-101"
    assert new_v.collection_name == "obsidian_vault_physics_101"
    assert manager.active_vault_id == "physics-101"

    # Switch back to default
    assert manager.set_active_vault("default") is True
    assert manager.get_active_vault().id == "default"

    # Delete custom workspace
    assert manager.delete_vault("physics-101") is True
    assert manager.get_vault("physics-101") is None

    # Cannot delete default
    assert manager.delete_vault("default") is False


def test_cross_vault_vector_isolation(tmp_path):
    """Verify vectors in Vault A do not bleed into Vault B."""
    persist_dir = str(tmp_path / "chroma_multi_test")
    embedder = MockEmbedder()

    # Collection 1: College
    store_a = ChromaVectorStore(
        embedder=embedder,
        persist_dir=persist_dir,
        collection_name="obsidian_vault_college_test",
    )
    store_a.add_documents([
        Document(
            page_content="Course: Data Science 101. Student: Aryan. Grade: A+.",
            metadata={"source": "College/Gradecard.md", "title": "Gradecard"},
        )
    ])
    assert store_a.count() == 1

    # Collection 2: Work (Empty initially)
    store_b = ChromaVectorStore(
        embedder=embedder,
        persist_dir=persist_dir,
        collection_name="obsidian_vault_work_test",
    )
    assert store_b.count() == 0

    # Query in Store B should find nothing
    results_b = store_b.similarity_search("Aryan", k=2)
    assert len(results_b) == 0

    # Query in Store A should find the note
    results_a = store_a.similarity_search("Aryan", k=2)
    assert len(results_a) == 1
    assert "Aryan" in results_a[0].page_content

    # Switch Store A to collection B
    store_a.switch_collection("obsidian_vault_work_test")
    assert store_a.count() == 0


def test_vault_file_ingestion(tmp_path):
    """Test saving and indexing a markdown file into a specific vault."""
    service = RAGService(vault_id="academics")
    
    # Create test note file
    note_path = tmp_path / "Linear_Algebra.md"
    note_path.write_text(
        "# Linear Algebra\nEigenvalues and eigenvectors of transformation matrices.\nStudent: Aryan Kumar.",
        encoding="utf-8",
    )

    result = service.ingest_markdown_file(note_path, override_filename="Linear_Algebra.md", vault_id="academics")
    assert result.total_notes_found == 1
    assert result.total_chunks_created >= 1
    assert "Linear_Algebra.md" in result.processed_files

    # Verify query retrieves the chunk in academics vault
    res = service.ask("What are eigenvalues?", vault_id="academics")
    assert res["vault_id"] == "academics"

