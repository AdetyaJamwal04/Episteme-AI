# ==============================================================================
# VeriFact — Multi-Stage Production Dockerfile
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build & Dependency Resolution
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast deterministic dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency manifests
COPY pyproject.toml uv.lock ./

# Install Python dependencies into virtual environment
ENV UV_COMPILE_BYTECODE=1
RUN uv sync --frozen --no-dev --no-install-project

# ------------------------------------------------------------------------------
# Stage 2: Production Runtime
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user
RUN groupadd -r verifact && useradd -r -g verifact -d /app verifact

# Copy installed virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application source code
COPY --chown=verifact:verifact . /app

# Create cache directory for ML models
RUN mkdir -p /home/verifact/.cache/huggingface && chown -R verifact:verifact /home/verifact/.cache

# Switch to non-root user
USER verifact

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default launch command: FastAPI production server
CMD ["python", "-m", "uvicorn", "verifact.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
