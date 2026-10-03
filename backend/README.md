# SAMBAL Backend (FastAPI Modular Monolith)

Core service for SIH26093 — SAMBAL Intelligence & Response Layer.

## Development

```bash
# Create and activate virtualenv
uv venv --python 3.12 .venv
.venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format & Lint
ruff format .
ruff check .
mypy app
```
