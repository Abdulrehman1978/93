"""Configuration and Environment Validation for SAMBAL Backend.

Uses Pydantic Settings with strict validation.
Ensures PostgreSQL is canonical and validates all operational boundaries.
"""

from typing import Literal

from pydantic import Field, field_validator, model_validator
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

    # Provider-neutral OIDC/OAuth verification boundary. A concrete production
    # provider remains deployment configuration, never a domain-model import.
    OIDC_PROVIDER_CODE: str = "unconfigured"
    OIDC_ISSUER: str | None = None
    OIDC_AUDIENCE: str | None = None
    OIDC_JWKS_URI: str | None = None
    OIDC_ALLOWED_ALGORITHMS: list[str] | str = ["RS256"]
    OIDC_CLOCK_SKEW_SECONDS: int = 30
    OIDC_JWKS_CACHE_SECONDS: int = 300

    # Application-level AEAD key material. Production must inject a real secret
    # from a KMS/HSM/Vault/secure mounted secret, never source or database data.
    FIELD_ENCRYPTION_KEY: str | None = None
    FIELD_ENCRYPTION_KEY_ID: str = "DEV-KEY-1"
    FIELD_ENCRYPTION_KEYS_JSON: str | None = None

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

    @field_validator("OIDC_ALLOWED_ALGORITHMS", mode="before")
    @classmethod
    def assemble_oidc_algorithms(cls, v: str | list[str]) -> list[str]:
        """Allow a comma-separated approved JWT algorithm list."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
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

    @model_validator(mode="after")
    def validate_production_boundaries(self) -> "Settings":
        """Strict fail-fast validation rejecting insecure development defaults in staging/production."""
        if self.ENVIRONMENT in ("staging", "production"):
            if self.DEBUG:
                raise ValueError("DEBUG mode must be False in staging and production environments.")

            # Validate SECRET_KEY strength and prohibit dev defaults
            if (
                not self.SECRET_KEY
                or len(self.SECRET_KEY) < 32
                or "insecure" in self.SECRET_KEY.lower()
                or "replace_in_production" in self.SECRET_KEY.lower()
                or self.SECRET_KEY in ("changeme", "secret", "password", "sambal_secret")
            ):
                raise ValueError(
                    "Insecure or default development SECRET_KEY is strictly rejected in staging/production. "
                    "A cryptographically strong secret of at least 32 characters must be provided."
                )

            # Validate PostgreSQL host and credentials
            if "localhost" in self.DATABASE_URL or "127.0.0.1" in self.DATABASE_URL:
                raise ValueError(
                    "Inappropriate localhost DATABASE_URL rejected in staging/production. "
                    "Production must reference dedicated managed PostgreSQL infrastructure."
                )
            if "sambal_secure_pass" in self.DATABASE_URL:
                raise ValueError(
                    "Default development database credentials (sambal_secure_pass) rejected in staging/production."
                )

            # Validate S3 storage host and credentials
            if "localhost" in self.S3_ENDPOINT_URL or "127.0.0.1" in self.S3_ENDPOINT_URL:
                raise ValueError(
                    "Inappropriate localhost S3_ENDPOINT_URL rejected in staging/production. "
                    "Production must reference resilient S3-compatible cloud storage."
                )
            if (
                self.S3_ACCESS_KEY == "sambal_minio_admin"
                or self.S3_SECRET_KEY == "sambal_minio_secret_key_2026"
            ):
                raise ValueError(
                    "Default development MinIO credentials rejected in staging/production."
                )

            if "*" in self.ALLOWED_ORIGINS:
                raise ValueError("Wildcard CORS origins are rejected in staging/production.")

            if self.FIELD_ENCRYPTION_KEY is None and self.FIELD_ENCRYPTION_KEYS_JSON is None:
                raise ValueError(
                    "Production requires field-encryption key material from an external secret provider."
                )

            configured_oidc = (
                self.OIDC_ISSUER,
                self.OIDC_AUDIENCE,
                self.OIDC_JWKS_URI,
            )
            if any(configured_oidc) and not all(configured_oidc):
                raise ValueError("OIDC issuer, audience, and JWKS URI must be configured together.")
            if self.OIDC_ISSUER and any(
                value in self.OIDC_ISSUER.lower() for value in ("localhost", "127.0.0.1")
            ):
                raise ValueError("Development localhost OIDC issuers are rejected in production.")

        return self


settings = Settings()
