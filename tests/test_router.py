"""
Unit tests for QueryRouterNode and LangGraph Agent workflow.
"""

from app.llm.model import MockChatModel
from app.embeddings.embedder import MockEmbedder
from app.vectorstore.chroma_store import ChromaVectorStore
from app.retrieval.retriever import ObsidianRetriever
from app.agents.query_router import QueryRouterNode
from app.agents.rag_graph import ObsidianRAGWorkflow


def test_query_router_classification():
    llm = MockChatModel()
    router = QueryRouterNode(llm)

    # General question (greeting or math fast path)
    res_gen = router({"query": "Hello there!", "execution_trace": []})
    assert res_gen["route"] == "GENERAL_QUERY"

    res_math = router({"query": "what is 2 + 2?", "execution_trace": []})
    assert res_math["route"] == "GENERAL_QUERY"

    # Knowledge base question
    res_kb = router({"query": "What do my notes say about RAG?", "execution_trace": []})
    assert res_kb["route"] == "KNOWLEDGE_BASE_QUERY"


def test_rag_workflow_execution(tmp_path):
    persist_dir = str(tmp_path / "chroma_workflow_test")
    embedder = MockEmbedder()
    store = ChromaVectorStore(embedder=embedder, persist_dir=persist_dir, collection_name="wf_col")
    retriever = ObsidianRetriever(vector_store=store)
    llm = MockChatModel()

    workflow = ObsidianRAGWorkflow(llm=llm, retriever=retriever)

    # Run general question
    state_gen = workflow.run("Hello, who are you?")
    assert state_gen["route"] == "GENERAL_QUERY"
    assert len(state_gen["answer"]) > 0

    # Run unindexed KB question (answers with general intelligence or project overview)
    state_kb = workflow.run("What are the results of my CineMatch project?")
    assert state_kb["route"] == "KNOWLEDGE_BASE_QUERY"
    assert len(state_kb["answer"]) > 0


def test_point_to_point_response_formatting(tmp_path):
    """Verify responses are direct, point-to-point, and never dump raw chunk metadata."""
    from langchain_core.documents import Document

    persist_dir = str(tmp_path / "chroma_p2p_test")
    embedder = MockEmbedder()
    store = ChromaVectorStore(embedder=embedder, persist_dir=persist_dir, collection_name="p2p_col")
    store.add_documents([
        Document(
            page_content="Aryan Shah - Resume\nEducation: Bachelor of Technology in Computer Science & Engineering. CPI: 8.84 / 10.0.\nExperience: Machine Learning & Generative AI Intern.\nSkills: Python, React, FastAPI, LangGraph, Retrieval-Augmented Generation (RAG).",
            metadata={"source": "Papers/Sample_Resume.pdf", "title": "Sample Resume", "folder": "Papers", "chunk_id": 0},
        )
    ])
    retriever = ObsidianRetriever(vector_store=store, top_k=2, score_threshold=0.0)
    llm = MockChatModel()
    workflow = ObsidianRAGWorkflow(llm=llm, retriever=retriever)

    # Test "what is my college name"
    state_college = workflow.run("what is my college name")
    answer = state_college["answer"]
    assert "--- DOCUMENT CHUNK" not in answer
    assert "[Source: Document]" not in answer
    assert "couldn't find your college" in answer.lower()
    assert "8.84" in answer

    # Test "what is my CPI"
    state_cpi = workflow.run("what is my cpi")
    assert "--- DOCUMENT CHUNK" not in state_cpi["answer"]
    assert "8.84" in state_cpi["answer"]


def test_dynamic_arithmetic_evaluation():
    """Verify any dynamic arithmetic calculation evaluates accurately."""
    llm = MockChatModel()
    router = QueryRouterNode(llm)
    workflow = ObsidianRAGWorkflow(llm=llm, retriever=None)

    # Pure math with no spaces
    res = workflow.run("what is 786*22")
    assert res["route"] == "GENERAL_QUERY"
    assert "17,292" in res["answer"] or "17292" in res["answer"]

    # Complex math expression with parenthesis
    res_complex = workflow.run("calculate (150 + 50) * 4")
    assert res_complex["route"] == "GENERAL_QUERY"
    assert "800" in res_complex["answer"]

