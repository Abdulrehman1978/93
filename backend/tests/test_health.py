"""Unit and API tests for Health & Telemetry endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


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
        mock_s3.return_value = (True, 8.5, "S3 storage operational")

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
        mock_db.return_value = (False, None, "Connection refused")
        mock_s3.return_value = (True, 5.1, "S3 storage operational")

        response = await client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["dependencies"]["postgresql"]["status"] == "unreachable"


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
