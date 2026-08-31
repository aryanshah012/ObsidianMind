"""
FastAPI Backend Server for ObsidianMind.
Exposes REST endpoints for authentication, multi-vault workspace management,
1-click demo indexing, agentic chat with LangGraph, and diagnostics with
strict per-user data isolation.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Query, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.config import settings
from app.models.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import auth_service
from app.services.rag_service import RAGService

app = FastAPI(
    title="ObsidianMind API",
    version="1.0.0",
    description="Backend REST API for ObsidianMind AI Knowledge Assistant with Multi-User & Multi-Vault Isolation",
)

# Enable CORS for Vite frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# User-scoped RAG service cache
user_rag_services: Dict[str, RAGService] = {}

security = HTTPBearer(auto_error=False)


async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> UserResponse:
    """Validate Bearer JWT token and return authenticated user profile."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = auth_service.decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.get_user_by_id(payload["sub"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_rag_service_for_user(
    user_id: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    top_k: Optional[int] = None,
    score_threshold: Optional[float] = None,
    vault_id: Optional[str] = None,
) -> RAGService:
    """Retrieve or initialize a user-isolated RAG service instance."""
    # If custom API key or provider is specified, instantiate freshly
    if api_key or provider:
        return RAGService(
            user_id=user_id,
            llm_provider=provider or settings.LLM_PROVIDER,
            llm_model=model or settings.LLM_MODEL,
            api_key=api_key,
            top_k=top_k or settings.RETRIEVER_TOP_K,
            score_threshold=score_threshold if score_threshold is not None else settings.RETRIEVER_SCORE_THRESHOLD,
            vault_id=vault_id,
        )

    cached_service = user_rag_services.get(user_id)
    if cached_service is None:
        try:
            cached_service = RAGService(
                user_id=user_id,
                llm_provider=provider or settings.LLM_PROVIDER,
                llm_model=model or settings.LLM_MODEL,
                api_key=api_key,
                top_k=top_k or settings.RETRIEVER_TOP_K,
                score_threshold=score_threshold if score_threshold is not None else settings.RETRIEVER_SCORE_THRESHOLD,
                vault_id=vault_id,
            )
        except Exception:
            cached_service = RAGService(
                user_id=user_id,
                llm_provider="mock",
                top_k=top_k or settings.RETRIEVER_TOP_K,
                score_threshold=score_threshold if score_threshold is not None else settings.RETRIEVER_SCORE_THRESHOLD,
                vault_id=vault_id,
            )
        user_rag_services[user_id] = cached_service
    elif vault_id:
        cached_service.switch_vault(vault_id)

    return cached_service


# Request & Response Schemas
class CreateVaultRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=60, description="Workspace name")
    description: str = Field(default="", max_length=200, description="Workspace purpose")
    icon: str = Field(default="Folder", description="Lucide icon name")
    color: str = Field(default="#2E7D6A", description="Accent color hex")


class ChatRequest(BaseModel):
    query: str = Field(..., description="User question")
    chat_history: List[Dict[str, str]] = Field(default_factory=list, description="Previous messages")
    doc_filter: Optional[List[str]] = Field(default=None, description="Optional list of document sources to filter retrieval")
    vault_id: Optional[str] = Field(default=None, description="Target workspace vault ID")
    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    top_k: Optional[int] = None
    score_threshold: Optional[float] = None


class SetApiKeyRequest(BaseModel):
    provider: str = "google"
    api_key: str


class ChatResponse(BaseModel):
    query: str
    answer: str
    route: str
    route_reasoning: str
    sources: List[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    has_relevant_context: bool
    execution_trace: List[str]
    latency_sec: float
    error: Optional[str] = None
    vault_id: Optional[str] = None


# -------------------------------------------------------------
# Endpoints: Authentication
# -------------------------------------------------------------

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(req: UserRegisterRequest):
    """Register a new user, allocate isolated storage, and return JWT token."""
    try:
        user = auth_service.register_user(req)
        token = auth_service.create_access_token(user)
        return TokenResponse(
            success=True,
            token=token,
            user=user,
            message="Account created successfully!",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(req: UserLoginRequest):
    """Authenticate user credentials and issue signed JWT token."""
    user = auth_service.authenticate_user(req.username_or_email, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password.",
        )
    token = auth_service.create_access_token(user)
    return TokenResponse(
        success=True,
        token=token,
        user=user,
        message=f"Welcome back, {user.full_name or user.username}!",
    )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """Retrieve authenticated user profile."""
    return current_user


@app.post("/api/auth/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """Acknowledge logout and invalidate local user service cache."""
    user_rag_services.pop(current_user.id, None)
    return {"success": True, "message": "Signed out successfully."}


# -------------------------------------------------------------
# Endpoints: Multi-Vault Workspace Management (User Isolated)
# -------------------------------------------------------------

@app.get("/api/vaults")
async def list_vaults(current_user: UserResponse = Depends(get_current_user)):
    """List all registered knowledge vaults for current user."""
    service = get_rag_service_for_user(user_id=current_user.id)
    return {"vaults": service.list_vaults()}


@app.post("/api/vaults")
async def create_vault(
    req: CreateVaultRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Create a new workspace vault with isolated vector collection for current user."""
    service = get_rag_service_for_user(user_id=current_user.id)
    new_vault = service.create_vault(
        name=req.name,
        description=req.description,
        icon=req.icon,
        color=req.color,
    )
    return {
        "success": True,
        "message": f"Workspace '{new_vault.name}' created successfully!",
        "vault": new_vault.model_dump(),
        "vaults": service.list_vaults(),
    }


@app.post("/api/vaults/{vault_id}/select")
async def select_vault(
    vault_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """Switch active knowledge workspace for current user."""
    service = get_rag_service_for_user(user_id=current_user.id)
    success = service.switch_vault(vault_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Vault '{vault_id}' not found.")
    return {
        "success": True,
        "active_vault_id": vault_id,
        "stats": service.get_stats(vault_id),
        "vaults": service.list_vaults(),
    }


@app.delete("/api/vaults/{vault_id}")
async def delete_vault(
    vault_id: str,
    current_user: UserResponse = Depends(get_current_user),
):
    """Delete a workspace vault and its ChromaDB collection for current user."""
    service = get_rag_service_for_user(user_id=current_user.id)
    target = service.vault_manager.get_vault(vault_id)
    if not target:
        raise HTTPException(status_code=404, detail="Vault not found.")
    if target.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default Primary Vault.")

    success = service.delete_vault(vault_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete vault.")
    return {
        "success": True,
        "message": f"Workspace '{target.name}' deleted.",
        "vaults": service.list_vaults(),
        "active_vault_id": service.vault_manager.active_vault_id,
    }


@app.get("/api/stats")
async def get_stats(
    vault_id: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    """Return knowledge base status and vector database statistics for user workspace."""
    service = get_rag_service_for_user(user_id=current_user.id, vault_id=vault_id)
    return service.get_stats(vault_id=vault_id)


@app.post("/api/settings/api-key")
async def save_api_key(
    req: SetApiKeyRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Save an API key to the active environment and .env file."""
    prov = req.provider.lower()
    key = req.api_key.strip()
    if prov == "google":
        os.environ["GOOGLE_API_KEY"] = key
    elif prov == "openai":
        os.environ["OPENAI_API_KEY"] = key
    elif prov == "groq":
        os.environ["GROQ_API_KEY"] = key

    # Also persist into .env file
    env_file = root_dir / ".env"
    lines = []
    if env_file.exists():
        lines = env_file.read_text().splitlines()

    key_var = f"{prov.upper()}_API_KEY"
    new_lines = [l for l in lines if not l.startswith(f"{key_var}=")]
    new_lines.append(f"{key_var}={key}")
    env_file.write_text("\n".join(new_lines) + "\n")

    # Clear user cached services so they re-initialize with new keys
    user_rag_services.clear()

    return {"success": True, "message": f"{prov.title()} API key saved successfully!"}


@app.get("/api/notes")
async def get_indexed_notes(
    vault_id: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    """List all currently indexed notes for current user's active or target workspace."""
    service = get_rag_service_for_user(user_id=current_user.id, vault_id=vault_id)
    vid = vault_id or service.vault_manager.active_vault_id
    vault_storage = service.get_vault_storage_dir(vid)

    notes = []
    vault_files = [
        p for p in sorted(vault_storage.rglob("*"))
        if p.is_file() and p.suffix.lower() in [".md", ".pdf", ".txt"]
    ]

    for p in vault_files:
        try:
            rel = str(p.relative_to(vault_storage))
        except ValueError:
            rel = p.name
        size_kb = round(max(0.1, p.stat().st_size / 1024), 1)
        folder = str(p.parent.relative_to(vault_storage)) if p.parent != vault_storage else "Root"
        notes.append({
            "source": rel,
            "title": p.stem.replace("_", " ").replace("-", " ").title(),
            "folder": folder,
            "doc_type": "pdf" if p.suffix.lower() == ".pdf" else "md",
            "size_kb": size_kb,
            "size_str": f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb / 1024, 1)} MB",
            "chunks_count": max(1, int(size_kb / 2)),
            "last_modified": p.stat().st_mtime,
        })

    return {"notes": notes, "vault_id": vid}


@app.get("/api/notes/content")
async def get_note_content(
    source: str,
    vault_id: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    """Retrieve raw content of a user's indexed note for preview."""
    service = get_rag_service_for_user(user_id=current_user.id, vault_id=vault_id)
    vid = vault_id or service.vault_manager.active_vault_id
    vault_storage = service.get_vault_storage_dir(vid)

    target_file = vault_storage / source
    if not target_file.exists() or not target_file.is_file():
        raise HTTPException(status_code=404, detail=f"Note '{source}' not found in your workspace.")

    if target_file.suffix.lower() == ".pdf":
        return {
            "source": source,
            "title": target_file.stem,
            "doc_type": "pdf",
            "content": f"PDF Document: {target_file.name} ({round(target_file.stat().st_size / 1024, 1)} KB)\nVector chunks extracted and indexed in your private ChromaDB collection.",
        }

    try:
        text = target_file.read_text(encoding="utf-8", errors="replace")
        return {
            "source": source,
            "title": target_file.stem,
            "doc_type": "md",
            "content": text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read note: {e}")


@app.post("/api/sample-vault")
async def load_sample_vault(
    vault_id: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    """1-Click instant demo vault indexing into user's private workspace."""
    service = get_rag_service_for_user(user_id=current_user.id, vault_id=vault_id)
    try:
        result = service.load_sample_vault(vault_id=vault_id)
        return {
            "success": True,
            "message": f"Successfully indexed sample vault into {service.vault_manager.get_active_vault().name}!",
            "total_notes": result.total_notes_found,
            "total_chunks": result.total_chunks_created,
            "processed_files": result.processed_files,
            "skipped_files": result.skipped_files,
            "errors": result.errors,
            "stats": service.get_stats(vault_id=vault_id),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample vault: {str(e)}")


@app.post("/api/upload")
async def upload_documents(
    files: Optional[List[UploadFile]] = File(None),
    file: Optional[UploadFile] = File(None),
    vault_id: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    """Upload and index multiple files into user's target workspace."""
    upload_list: List[UploadFile] = []
    if files:
        upload_list.extend(files)
    if file:
        upload_list.append(file)

    if not upload_list:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    service = get_rag_service_for_user(user_id=current_user.id, vault_id=vault_id)
    total_notes_processed = 0
    total_chunks_processed = 0
    processed_filenames = []
    errors = []

    allowed_extensions = [".zip", ".pdf", ".md", ".markdown", ".txt"]

    for uploaded_file in upload_list:
        filename = uploaded_file.filename or "unknown"
        suffix = Path(filename).suffix.lower()

        if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
            errors.append(f"Unsupported file type for {filename}. Skipped.")
            continue

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(uploaded_file.file, tmp)
            tmp_path = Path(tmp.name)

        try:
            if suffix == ".zip":
                result = service.ingest_zip_vault(tmp_path, vault_id=vault_id)
                total_notes_processed += result.total_notes_found
                total_chunks_processed += result.total_chunks_created
                processed_filenames.append(filename)
            elif suffix == ".pdf":
                result = service.ingest_pdf_file(
                    tmp_path,
                    clear_existing=False,
                    override_filename=filename,
                    vault_id=vault_id,
                )
                total_notes_processed += 1
                total_chunks_processed += result.total_chunks_created
                processed_filenames.append(filename)
            else:
                result = service.ingest_markdown_file(
                    tmp_path,
                    clear_existing=False,
                    override_filename=filename,
                    vault_id=vault_id,
                )
                total_notes_processed += 1
                total_chunks_processed += result.total_chunks_created
                processed_filenames.append(filename)
        except Exception as e:
            errors.append(f"Error processing {filename}: {str(e)}")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    return {
        "success": len(processed_filenames) > 0,
        "message": f"Successfully indexed {len(processed_filenames)} file(s) ({total_chunks_processed} chunks created).",
        "processed_files": processed_filenames,
        "total_notes": total_notes_processed,
        "total_chunks": total_chunks_processed,
        "errors": errors,
        "stats": service.get_stats(vault_id=vault_id),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Process query through LangGraph router and grounded RAG workflow for user."""
    service = get_rag_service_for_user(
        user_id=current_user.id,
        provider=request.provider,
        model=request.model,
        api_key=request.api_key,
        top_k=request.top_k,
        score_threshold=request.score_threshold,
        vault_id=request.vault_id,
    )

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        response_data = service.ask(
            query=request.query,
            chat_history=request.chat_history,
            doc_filter=request.doc_filter,
            vault_id=request.vault_id,
        )
        return ChatResponse(**response_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing RAG query: {str(e)}")


@app.post("/api/reset")
async def reset_database(
    vault_id: Optional[str] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
):
    """Clear all vector embeddings for user's active or target workspace."""
    service = get_rag_service_for_user(user_id=current_user.id, vault_id=vault_id)
    service.clear_vault(vault_id=vault_id)
    return {
        "success": True,
        "message": "Knowledge base vector store cleared for this workspace.",
        "stats": service.get_stats(vault_id=vault_id),
    }


# Serve static frontend build if present
frontend_dist = root_dir / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api.server:app", host="0.0.0.0", port=8000, reload=True)
