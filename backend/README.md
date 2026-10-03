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

# PostgreSQL database commands (DATABASE_URL must point to PostgreSQL 16.15+)
db-migrate
db-seed
db-check
db-drift
db-test

# Reset only a disposable development/testing database; refuses other environments
db-reset

# Format & Lint
ruff format .
ruff check .
mypy app
```
