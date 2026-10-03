"""Unit tests for Backend Configuration and Validation."""

import pytest

from app.config import Settings


def test_settings_default_values():
    """Verify settings defaults align with canonical PostgreSQL architecture."""
    settings = Settings()
    assert settings.ENVIRONMENT == "development"
    assert "postgresql+asyncpg://" in settings.DATABASE_URL
    assert settings.SVI_POLICY_STATUS == "PROVISIONAL_TRIAGE_POLICY"
    assert settings.PII_MASKING_ENABLED is True


def test_sqlite_rejection():
    """Verify that SQLite URLs are strictly rejected by configuration validation."""
    with pytest.raises(ValueError, match="DATABASE_URL must start with 'postgresql\\+asyncpg://'"):
        Settings(DATABASE_URL="sqlite:///test.db")


def test_mysql_rejection():
    """Verify that non-PostgreSQL URLs are strictly rejected."""
    with pytest.raises(ValueError, match="DATABASE_URL must start with 'postgresql\\+asyncpg://'"):
        Settings(DATABASE_URL="mysql://user:pass@localhost/db")
