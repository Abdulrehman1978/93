FROM python:3.12-slim

WORKDIR /app

# Install curl for Docker healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, reliable package installations
COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

# Copy dependency manifests
COPY pyproject.toml README.md ./

# Install dependencies in system environment
RUN uv pip install --system -e .

# Copy application source
COPY app/ ./app/

# Expose backend port
EXPOSE 8000

# Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
