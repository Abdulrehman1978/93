"""Unit tests for Backend Configuration and Validation.

Tests are strictly environment-independent and verify production fail-fast rules.
"""

import pytest

from app.config import Settings


def test_settings_explicit_development():
    """Verify settings when explicitly initialized in development."""
    settings = Settings(
        ENVIRONMENT="development",
        DATABASE_URL="postgresql+asyncpg://sambal_user:sambal_secure_pass@localhost:5493/sambal_db",
    )
    assert settings.ENVIRONMENT == "development"
    assert "postgresql+asyncpg://" in settings.DATABASE_URL
    assert settings.SVI_POLICY_STATUS == "PROVISIONAL_TRIAGE_POLICY"
    assert settings.PII_MASKING_ENABLED is True


def test_settings_default_environment_controlled(monkeypatch: pytest.MonkeyPatch):
    """Verify default environment is 'development' when ambient process variables are neutralized."""
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    settings = Settings(_env_file=None)
    assert settings.ENVIRONMENT == "development"
    assert "postgresql+asyncpg://" in settings.DATABASE_URL


def test_settings_testing_environment():
    """Verify settings behave predictably under testing environment."""
    settings = Settings(ENVIRONMENT="testing")
    assert settings.ENVIRONMENT == "testing"


def test_sqlite_rejection():
    """Verify that SQLite URLs are strictly rejected by configuration validation."""
    with pytest.raises(ValueError, match="DATABASE_URL must start with 'postgresql\\+asyncpg://'"):
        Settings(DATABASE_URL="sqlite:///test.db")


def test_mysql_rejection():
    """Verify that non-PostgreSQL URLs are strictly rejected."""
    with pytest.raises(ValueError, match="DATABASE_URL must start with 'postgresql\\+asyncpg://'"):
        Settings(DATABASE_URL="mysql://user:pass@localhost/db")


def test_production_debug_mode_rejection():
    """Verify DEBUG=True is strictly rejected in production."""
    with pytest.raises(ValueError, match="DEBUG mode must be False"):
        Settings(
            ENVIRONMENT="production",
            DEBUG=True,
            SECRET_KEY="x" * 32,
            DATABASE_URL="postgresql+asyncpg://user:pass@db.govcloud.internal:5432/db",
            S3_ENDPOINT_URL="https://s3.ap-south-1.amazonaws.com",
            S3_ACCESS_KEY="prod-access-key",
            S3_SECRET_KEY="prod-secret-key",
        )


def test_production_default_secret_key_rejection():
    """Verify default insecure dev secret key is strictly rejected in production."""
    with pytest.raises(
        ValueError, match="Insecure or default development SECRET_KEY is strictly rejected"
    ):
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="sambal_insecure_development_secret_key_replace_in_production",
            DATABASE_URL="postgresql+asyncpg://user:pass@db.govcloud.internal:5432/db",
            S3_ENDPOINT_URL="https://s3.ap-south-1.amazonaws.com",
            S3_ACCESS_KEY="prod-access-key",
            S3_SECRET_KEY="prod-secret-key",
        )


def test_production_short_secret_key_rejection():
    """Verify short secret key is strictly rejected in production."""
    with pytest.raises(ValueError, match="at least 32 characters"):
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="too-short-secret",
            DATABASE_URL="postgresql+asyncpg://user:pass@db.govcloud.internal:5432/db",
            S3_ENDPOINT_URL="https://s3.ap-south-1.amazonaws.com",
            S3_ACCESS_KEY="prod-access-key",
            S3_SECRET_KEY="prod-secret-key",
        )


def test_production_localhost_database_rejection():
    """Verify localhost database URL is strictly rejected in production."""
    with pytest.raises(ValueError, match="Inappropriate localhost DATABASE_URL"):
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="x" * 32,
            DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db",
            S3_ENDPOINT_URL="https://s3.ap-south-1.amazonaws.com",
            S3_ACCESS_KEY="prod-access-key",
            S3_SECRET_KEY="prod-secret-key",
        )


def test_production_dev_database_password_rejection():
    """Verify development database password is strictly rejected in production."""
    with pytest.raises(ValueError, match="Default development database credentials"):
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="x" * 32,
            DATABASE_URL="postgresql+asyncpg://user:sambal_secure_pass@db.internal:5432/db",
            S3_ENDPOINT_URL="https://s3.ap-south-1.amazonaws.com",
            S3_ACCESS_KEY="prod-access-key",
            S3_SECRET_KEY="prod-secret-key",
        )


def test_production_localhost_s3_rejection():
    """Verify localhost S3 endpoint is strictly rejected in production."""
    with pytest.raises(ValueError, match="Inappropriate localhost S3_ENDPOINT_URL"):
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="x" * 32,
            DATABASE_URL="postgresql+asyncpg://user:strong_prod_pass@db.internal:5432/db",
            S3_ENDPOINT_URL="http://localhost:9093",
            S3_ACCESS_KEY="prod-access-key",
            S3_SECRET_KEY="prod-secret-key",
        )


def test_production_default_minio_credentials_rejection():
    """Verify default MinIO credentials are strictly rejected in production."""
    with pytest.raises(ValueError, match="Default development MinIO credentials"):
        Settings(
            ENVIRONMENT="production",
            DEBUG=False,
            SECRET_KEY="x" * 32,
            DATABASE_URL="postgresql+asyncpg://user:strong_prod_pass@db.internal:5432/db",
            S3_ENDPOINT_URL="https://s3.ap-south-1.amazonaws.com",
            S3_ACCESS_KEY="sambal_minio_admin",
            S3_SECRET_KEY="sambal_minio_secret_key_2026",
        )


def test_production_valid_configuration_success():
    """Verify a valid production configuration passes all fail-fast checks."""
    settings = Settings(
        ENVIRONMENT="production",
        DEBUG=False,
        SECRET_KEY="a_strong_cryptographic_production_secret_key_2026",
        DATABASE_URL="postgresql+asyncpg://sambal_prod:strong_prod_db_pass_2026@db.internal:5432/sambal_prod_db",
        S3_ENDPOINT_URL="https://s3.ap-south-1.amazonaws.com",
        S3_ACCESS_KEY="AKIA_PROD_VERIFIED_KEY",
        S3_SECRET_KEY="PROD_VERIFIED_SECRET_KEY_NOT_DEV_VALUE",
        S3_BUCKET_NAME="sambal-production-evidence",
        FIELD_ENCRYPTION_KEY="MTExMTExMTExMTExMTExMTExMTExMTExMTExMTExMQ==",
    )
    assert settings.ENVIRONMENT == "production"
    assert settings.DEBUG is False


def test_oidc_algorithm_configuration_is_limited_to_rsa_jwks_support():
    with pytest.raises(ValueError, match="non-empty subset of RS256, RS384, RS512"):
        Settings(OIDC_ALLOWED_ALGORITHMS=["ES256"])
