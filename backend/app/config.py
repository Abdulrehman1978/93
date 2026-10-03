"""Configuration and Environment Validation for SAMBAL Backend.

Uses Pydantic Settings with strict validation.
Ensures PostgreSQL is canonical and validates all operational boundaries.
"""

from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings validated from environment variables or .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment & Project Identity
    ENVIRONMENT: Literal["development", "testing", "staging", "production"] = "development"
    DEBUG: bool = False
    PROJECT_NAME: str = "SAMBAL Intelligence & Response Layer"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    # Canonical PostgreSQL (PostgreSQL is authoritative across all environments)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://sambal_user:sambal_secure_pass@localhost:5493/sambal_db",
        description="Canonical PostgreSQL connection URI using asyncpg driver",
    )
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_MAX_OVERFLOW: int = 20

    # S3-Compatible Object Storage (MinIO in local dev)
    S3_ENDPOINT_URL: str = "http://localhost:9093"
    S3_ACCESS_KEY: str = "sambal_minio_admin"
    S3_SECRET_KEY: str = "sambal_minio_secret_key_2026"
    S3_BUCKET_NAME: str = "sambal-audio-evidence"
    S3_REGION: str = "us-east-1"
    S3_SECURE: bool = False

    # Security & CORS
    SECRET_KEY: str = "sambal_insecure_development_secret_key_replace_in_production"
    ALLOWED_ORIGINS: list[str] | str = [
        "http://localhost:3000",
        "http://localhost:3093",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3093",
    ]

    # Telemetry & PII Protection
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    PII_MASKING_ENABLED: bool = True

    # Policy Baselines (Provisional Triage Policy; clinical finality requires formal validation)
    SVI_POLICY_STATUS: str = "PROVISIONAL_TRIAGE_POLICY"
    FOLLOW_UP_POLICY_VERSION: str = "v1.0-provisional"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Allow comma-separated strings or JSON arrays in .env."""
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                import json

                try:
                    return json.loads(stripped)  # type: ignore[no-any-return]
                except Exception:
                    pass
            return [i.strip() for i in stripped.split(",") if i.strip()]
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Ensure PostgreSQL is canonical and asyncpg driver is specified."""
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql+asyncpg://'. "
                "PostgreSQL is canonical across dev, test, CI, and production. "
                "SQLite is prohibited as a production or integration alternative."
            )
        return v


settings = Settings()
