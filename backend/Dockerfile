FROM python:3.12-slim

WORKDIR /app

# Install curl for Docker healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, reliable, reproducible package installations
COPY --from=ghcr.io/astral-sh/uv:0.12.17 /uv /bin/uv

# Copy dependency manifests and authoritative frozen lock
COPY pyproject.toml uv.lock README.md ./

# Install dependencies from frozen lock without installing project yet (layer caching)
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source
COPY app/ ./app/

# Install the application package from frozen lock
RUN uv sync --frozen --no-dev

# Ensure virtual environment binaries are on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Expose backend port
EXPOSE 8000

# Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
