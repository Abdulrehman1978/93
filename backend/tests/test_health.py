"""Unit and API tests for Health & Telemetry endpoints.

Verifies RFC 7807 problem details and proves zero infrastructure-detail leakage in readiness probes.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.database import check_database_health
from app.storage import check_storage_health


@pytest.mark.asyncio
async def test_liveness_probe(client: AsyncClient):
    """Verify /health/live returns 200 with service metadata."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "SAMBAL" in data["service"]
    assert "timestamp" in data
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_readiness_probe_healthy(client: AsyncClient):
    """Verify /health/ready returns 200 when PostgreSQL and S3 are healthy."""
    with (
        patch("app.api.v1.health.check_database_health", new_callable=AsyncMock) as mock_db,
        patch("app.api.v1.health.check_storage_health", new_callable=AsyncMock) as mock_s3,
    ):
        mock_db.return_value = (True, 4.2, "PostgreSQL connection operational")
        mock_s3.return_value = (True, 8.5, "Storage operational (configured bucket verified)")

        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["dependencies"]["postgresql"]["status"] == "healthy"
        assert data["dependencies"]["s3_storage"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_probe_db_failure(client: AsyncClient):
    """Verify /health/ready returns 503 when canonical PostgreSQL is down."""
    with (
        patch("app.api.v1.health.check_database_health", new_callable=AsyncMock) as mock_db,
        patch("app.api.v1.health.check_storage_health", new_callable=AsyncMock) as mock_s3,
    ):
        mock_db.return_value = (False, None, "Database connection unavailable")
        mock_s3.return_value = (True, 5.1, "Storage operational (configured bucket verified)")

        response = await client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["postgresql"]["status"] == "unreachable"
        assert data["dependencies"]["postgresql"]["details"] == "Database connection unavailable"


@pytest.mark.asyncio
async def test_readiness_probe_storage_failure_degraded(client: AsyncClient):
    """Verify /health/ready returns 200 degraded when PostgreSQL is healthy but S3 is unreachable."""
    with (
        patch("app.api.v1.health.check_database_health", new_callable=AsyncMock) as mock_db,
        patch("app.api.v1.health.check_storage_health", new_callable=AsyncMock) as mock_s3,
    ):
        mock_db.return_value = (True, 3.1, "PostgreSQL connection operational")
        mock_s3.return_value = (False, None, "Storage service unreachable")

        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["dependencies"]["postgresql"]["status"] == "healthy"
        assert data["dependencies"]["s3_storage"]["status"] == "unreachable"


@pytest.mark.asyncio
async def test_readiness_probe_does_not_leak_database_credentials():
    """Verify database health check does not expose connection strings, passwords, or hostnames."""
    sensitive_db_error = (
        "connection to server at 'db-internal.private.vpc' (10.0.4.12), port 5432 failed: "
        "FATAL: password authentication failed for user 'sambal_prod_user' "
        "(password: 'SUPER_SECRET_LEAKY_PASSWORD_12345')"
    )
    mock_engine = MagicMock()
    mock_engine.connect.side_effect = Exception(sensitive_db_error)
    with patch("app.database.engine", mock_engine):
        ok, latency_ms, details = await check_database_health()
        assert ok is False
        assert details == "Database connection unavailable"
        assert "SUPER_SECRET_LEAKY_PASSWORD_12345" not in details
        assert "db-internal.private.vpc" not in details
        assert "10.0.4.12" not in details
        assert "FATAL" not in details


@pytest.mark.asyncio
async def test_readiness_probe_does_not_leak_storage_credentials():
    """Verify storage health check does not expose internal endpoints, tokens, or secret keys."""
    sensitive_s3_error = (
        "Could not connect to the endpoint URL: "
        "'https://s3-internal-vault.secure.cloud:9093/?X-Amz-Security-Token=SECRET_TOKEN_XYZ987'"
    )
    with patch("app.storage._sync_check_storage", side_effect=Exception(sensitive_s3_error)):
        ok, latency_ms, details = await check_storage_health()
        assert ok is False
        assert details == "Storage service unavailable"
        assert "SECRET_TOKEN_XYZ987" not in details
        assert "s3-internal-vault" not in details


@pytest.mark.asyncio
async def test_404_rfc7807_problem_details(client: AsyncClient):
    """Verify non-existent routes return RFC 7807 problem+json response."""
    response = await client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404
    assert "application/problem+json" in response.headers["Content-Type"]
    data = response.json()
    assert data["title"] == "Not Found"
    assert data["status"] == 404
    assert "request_id" in data
    assert "timestamp" in data
