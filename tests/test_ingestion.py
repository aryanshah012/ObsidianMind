"""
Unit tests for safe zip extraction, Obsidian Markdown parsing, and vault loading.
"""

import io
import zipfile
import pytest
from pathlib import Path

from app.ingestion.zip_extractor import extract_zip_safely, ZipExtractionError, is_safe_path
from app.ingestion.parser import ObsidianParser
from app.ingestion.loader import ObsidianVaultLoader


def test_is_safe_path():
    base = Path("/tmp/vault").resolve()
    assert is_safe_path(base, Path("/tmp/vault/AI/RAG.md"))
    assert not is_safe_path(base, Path("/tmp/vault/../../etc/passwd"))
    assert not is_safe_path(base, Path("/etc/passwd"))


def test_zip_extractor_valid(tmp_path):
    # Create sample zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("AI/RAG.md", "# RAG\nRetrieval Augmented Generation note.")
        zf.writestr("Notes/Daily.md", "# Daily\nMeeting notes.")
    
    zip_path = tmp_path / "test_vault.zip"
    zip_path.write_bytes(zip_buffer.getvalue())

    target_dir = tmp_path / "extracted"
    out_dir, files = extract_zip_safely(zip_path, target_dir)

    assert out_dir.exists()
    assert (out_dir / "AI" / "RAG.md").exists()
    assert (out_dir / "Notes" / "Daily.md").exists()
    assert len(files) == 2


def test_zip_extractor_malicious_path_traversal(tmp_path):
    # Create malicious ZipSlip zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("../../malicious.txt", "exploit payload")

    zip_path = tmp_path / "evil.zip"
    zip_path.write_bytes(zip_buffer.getvalue())

    target_dir = tmp_path / "extracted_evil"
    with pytest.raises(ZipExtractionError) as exc_info:
        extract_zip_safely(zip_path, target_dir)
    assert "traversal" in str(exc_info.value).lower()


def test_obsidian_parser_frontmatter_and_wikilinks(tmp_path):
    md_content = """---
title: Advanced RAG Techniques
tags: [rag, vector-search, nlp]
aliases: [Modular RAG]
created: 2026-08-15
---

# Advanced RAG Techniques

Retrieval-Augmented Generation connects [[LLMs|Large Language Models]] with [[Vector_Databases]].

## Subheading 1
Here is more text with an inline tag #experimentation and a comment %% secret note %%.
"""
    note_path = tmp_path / "Advanced_RAG.md"
    note_path.write_text(md_content, encoding="utf-8")

    parser = ObsidianParser()
    doc = parser.parse_file(note_path, tmp_path)

    assert doc.title == "Advanced RAG Techniques"
    assert "rag" in doc.tags
    assert "vector-search" in doc.tags
    assert "experimentation" in doc.tags
    assert doc.folder == "Root"
    # Wikilinks converted to plain text
    assert "Large Language Models" in doc.content
    assert "Vector_Databases" in doc.content
    assert "[[" not in doc.content
    # Comments stripped
    assert "secret note" not in doc.content


def test_obsidian_loader_filtering(tmp_path):
    vault_root = tmp_path / "my_vault"
    vault_root.mkdir()
    
    # Create valid markdown file
    (vault_root / "AI").mkdir()
    (vault_root / "AI" / "Notes.md").write_text("# AI Notes\nUseful AI details.", encoding="utf-8")

    # Create ignored files
    (vault_root / ".obsidian").mkdir()
    (vault_root / ".obsidian" / "workspace.json").write_text("{}", encoding="utf-8")
    (vault_root / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (vault_root / ".DS_Store").write_bytes(b"junk")

    loader = ObsidianVaultLoader()
    result = loader.load_vault(vault_root)

    assert result.total_notes_found == 1
    assert result.processed_files == ["AI/Notes.md"]
    assert len(result.skipped_files) >= 1
    assert len(result.chunks) > 0


def test_pdf_parser_and_loader(tmp_path):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from app.ingestion.pdf_parser import PDFParser

    pdf_path = tmp_path / "test_doc.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Transformer Self Attention Architecture", styles["Heading1"]),
        Paragraph("Self attention maps queries and keys to compute weighted context values.", styles["Normal"])
    ]
    doc.build(story)

    parser = PDFParser()
    docs = parser.parse_file(pdf_path, tmp_path)

    assert len(docs) == 1
    assert "Test Doc" in docs[0].title
    assert "queries and keys" in docs[0].content
    assert docs[0].metadata["doc_type"] == "pdf"
    assert docs[0].metadata["page_number"] == 1

    # Test via ObsidianVaultLoader
    loader = ObsidianVaultLoader()
    res = loader.load_pdf_file(pdf_path)
    assert res.total_notes_found == 1
    assert res.total_chunks_created >= 1
    assert "test_doc.pdf" in res.processed_files
