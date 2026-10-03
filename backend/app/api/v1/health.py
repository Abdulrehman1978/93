"""Health, Readiness, and Liveness Telemetry Endpoints.

Provides Kubernetes/Docker-compatible health probes with dependency status
for canonical PostgreSQL and S3-compatible object storage.
"""

import datetime
import time
from typing import Any, Literal

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from app.config import settings
from app.database import check_database_health
from app.storage import check_storage_health

router = APIRouter()

# Record service process start time
START_TIME = time.time()


class DependencyHealth(BaseModel):
    """Health status of an external dependency."""

    status: Literal["healthy", "degraded", "unreachable"]
    latency_ms: float | None = None
    details: str | None = None


class HealthResponse(BaseModel):
    """Standardized health check response matching shared contracts."""

    status: Literal["ok", "degraded", "unhealthy"]
    service: str
    version: str
    timestamp: str
    uptime_seconds: float = Field(ge=0.0)
    dependencies: dict[str, DependencyHealth]


@router.get(
    "/health/live",
    response_model=dict[str, Any],
    summary="Liveness Probe",
    description="Returns 200 OK as long as the FastAPI process is responsive.",
)
async def liveness_probe() -> dict[str, Any]:
    """Basic liveness check."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
    }


@router.get(
    "/health/ready",
    response_model=HealthResponse,
    summary="Readiness Probe",
    description="Evaluates operational health of canonical PostgreSQL and S3 storage.",
)
async def readiness_probe(response: Response) -> HealthResponse:
    """Readiness check validating required infrastructure dependencies."""
    now_iso = datetime.datetime.now(datetime.UTC).isoformat()
    uptime = round(time.time() - START_TIME, 2)

    # Check PostgreSQL
    db_ok, db_latency, db_details = await check_database_health()
    db_dep = DependencyHealth(
        status="healthy" if db_ok else "unreachable",
        latency_ms=db_latency,
        details=db_details,
    )

    # Check S3 Storage
    s3_ok, s3_latency, s3_details = await check_storage_health()
    s3_dep = DependencyHealth(
        status="healthy" if s3_ok else "unreachable",
        latency_ms=s3_latency,
        details=s3_details,
    )

    dependencies = {
        "postgresql": db_dep,
        "s3_storage": s3_dep,
    }

    # PostgreSQL is canonical and mandatory for operational readiness
    if not db_ok:
        overall_status: Literal["ok", "degraded", "unhealthy"] = "unhealthy"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif not s3_ok:
        overall_status = "degraded"
        response.status_code = status.HTTP_200_OK
    else:
        overall_status = "ok"
        response.status_code = status.HTTP_200_OK

    return HealthResponse(
        status=overall_status,
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=now_iso,
        uptime_seconds=uptime,
        dependencies=dependencies,
    )
