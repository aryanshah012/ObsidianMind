# ==============================================================================
# ObsidianMind - Production Multi-Stage Dockerfile (Ultra-Fast CPU Optimized)
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

# Prevent Python from writing .pyc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install minimal system dependencies (curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-only PyTorch first (avoids massive 1.5GB CUDA GPU wheel)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python requirements
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
