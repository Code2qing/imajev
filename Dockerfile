# syntax=docker/dockerfile:1
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Enable uv optimizations
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src:/app/scripts" \
    HF_HOME="/app/.cache/huggingface"

# Install necessary runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and lockfile for dependency caching
COPY pyproject.toml uv.lock* ./

# Install project dependencies with torch and serve extras
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --extra serve --extra torch || \
    uv sync --no-install-project --extra serve --extra torch

# Copy source code and scripts
COPY . /app

# Install project package into the venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra serve --extra torch

# Ensure virtualenv binaries are prioritized on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Create directories for persistent volumes
RUN mkdir -p /app/artifacts /app/adapters /app/.cache/huggingface && \
    chmod +x /app/docker-entrypoint.sh

EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://127.0.0.1:8765/v1/models || exit 1

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD []
