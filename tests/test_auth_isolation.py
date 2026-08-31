"""
Comprehensive tests for User Authentication and Multi-Tenant Data Isolation.
Verifies registration, login, JWT token validation, and complete separation of
vaults, file storage, and vector retrieval between different users.
"""

import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from app.api.server import app
from app.services.auth_service import AuthService
from app.models.user import UserRegisterRequest, UserLoginRequest
from app.services.vault_manager import VaultManager
from app.services.rag_service import RAGService


@pytest.fixture
def auth_svc(tmp_path):
    """Isolated test auth service with dedicated temporary database."""
    db_file = tmp_path / "test_users.db"
    return AuthService(db_path=db_file)


def test_user_registration_and_login(auth_svc):
    # 1. Register User 1
    req1 = UserRegisterRequest(
        username="alice",
        email="alice@example.com",
        password="secretpassword123",
        full_name="Alice Smith",
    )
    user1 = auth_svc.register_user(req1)
    assert user1.username == "alice"
    assert user1.email == "alice@example.com"
    assert user1.id.startswith("u_")

    # 2. Duplicate registration rejection
    with pytest.raises(ValueError, match="already taken"):
        auth_svc.register_user(req1)

    # 3. Successful Login
    login_user = auth_svc.authenticate_user("alice", "secretpassword123")
    assert login_user is not None
    assert login_user.id == user1.id

    # 4. Failed Login (Wrong Password)
    bad_login = auth_svc.authenticate_user("alice", "wrongpass")
    assert bad_login is None

    # 5. JWT Generation & Verification
    token = auth_svc.create_access_token(user1)
    assert isinstance(token, str) and len(token) > 20
    payload = auth_svc.decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == user1.id
    assert payload["username"] == "alice"


def test_cross_user_vault_isolation(tmp_path):
    """Verify that User 1 and User 2 have completely isolated workspace configurations."""
    u1_file = tmp_path / "u1_vaults.json"
    u2_file = tmp_path / "u2_vaults.json"

    mgr_u1 = VaultManager(user_id="user_1", storage_path=u1_file)
    mgr_u2 = VaultManager(user_id="user_2", storage_path=u2_file)

    # User 1 creates custom vault
    u1_custom = mgr_u1.create_vault(name="Alice Private Project")
    assert u1_custom.id == "alice-private-project"
    assert "user_user_1" in u1_custom.collection_name

    # User 2 should only have default vaults, not User 1's custom vault
    u2_vaults = mgr_u2.list_vaults()
    assert not any(v["id"] == "alice-private-project" for v in u2_vaults)


def test_cross_user_document_and_rag_isolation(tmp_path):
    """Verify that User 1's uploaded notes are never accessible to User 2."""
    service_u1 = RAGService(user_id="user_alice_test", vault_id="default")
    service_u2 = RAGService(user_id="user_bob_test", vault_id="default")

    # Clear initial collections
    service_u1.vector_store.clear()
    service_u2.vector_store.clear()

    # User 1 indexes a private confidential note
    note_u1 = tmp_path / "Alice_Secret.md"
    note_u1.write_text(
        "# Alice Confidential Project\nProject Code: SUPERNOVA-99.\nAccess Key: ALICE_SECURE_TOKEN_XYZ",
        encoding="utf-8",
    )
    service_u1.ingest_markdown_file(note_u1, override_filename="Alice_Secret.md", vault_id="default")

    assert service_u1.vector_store.count() >= 1

    # User 2 vector store MUST be empty
    assert service_u2.vector_store.count() == 0

    # User 2 queries for Alice's secret
    result_u2 = service_u2.ask("What is the Project Code for Alice's project?", vault_id="default")
    assert "SUPERNOVA-99" not in result_u2["answer"]
    assert len(result_u2.get("sources", [])) == 0

    # User 1 queries for Alice's secret
    result_u1 = service_u1.ask("What is the Project Code for Alice's project?", vault_id="default")
    assert any("SUPERNOVA-99" in s.get("title", "") or "SUPERNOVA-99" in str(s) or "SUPERNOVA-99" in result_u1["answer"] for s in result_u1.get("sources", [])) or "SUPERNOVA-99" in result_u1["answer"] or len(result_u1.get("sources", [])) > 0


def test_api_auth_endpoints():
    """Verify API endpoints require authentication and handle user isolation."""
    client = TestClient(app)

    # 1. Register User via API
    reg_payload = {
        "username": "tester_clt",
        "email": "tester_clt@test.com",
        "password": "pass12345678",
        "full_name": "Test Client",
    }
    res_reg = client.post("/api/auth/register", json=reg_payload)
    assert res_reg.status_code in [200, 400]  # 400 if already exists

    # 2. Login via API
    res_login = client.post(
        "/api/auth/login",
        json={"username_or_email": "tester_clt", "password": "pass12345678"},
    )
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "token" in token_data
    token = token_data["token"]

    # 3. Unauthenticated request to /api/vaults should fail with 401
    res_unauth = client.get("/api/vaults")
    assert res_unauth.status_code == 401

    # 4. Authenticated request with Bearer token should succeed
    headers = {"Authorization": f"Bearer {token}"}
    res_auth = client.get("/api/vaults", headers=headers)
    assert res_auth.status_code == 200
    data = res_auth.json()
    assert "vaults" in data

    # 5. Check /api/auth/me
    res_me = client.get("/api/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["username"] == "tester_clt"
