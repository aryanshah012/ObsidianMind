# ==============================================================================
# ObsidianMind - Production Multi-Stage Dockerfile (Ultra-Low Memory for 512MB RAM)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build React/Vite Frontend
# ------------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install --no-audit --prefer-offline

COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Production Python Backend & Runtime
# ------------------------------------------------------------------------------
FROM python:3.11-slim AS runner

# Prevent Python from writing .pyc, enable unbuffered output, configure low-memory defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    EMBEDDING_PROVIDER=google \
    EMBEDDING_MODEL=gemini-embedding-001 \
    LLM_PROVIDER=google \
    LLM_MODEL=gemini-3.5-flash-lite \
    MALLOC_ARENA_MAX=2

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-only PyTorch first to prevent CUDA 1.5GB OOM during pip install
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application backend, evaluation, and sample data
COPY app/ app/
COPY data/ data/
COPY eval/ eval/

# Copy built frontend assets into frontend/dist for FastAPI static mounting
COPY --from=frontend-builder /app/frontend/dist frontend/dist

# Expose server port
EXPOSE 8000

# Healthcheck endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/vaults || exit 1

# Start the full-stack server
CMD ["python", "app/main.py", "--server"]
