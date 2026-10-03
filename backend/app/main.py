"""FastAPI Modular Monolith Entrypoint for SAMBAL Intelligence Layer.

Follows V3 Lean-Core Architecture:
- Next.js PWA Client
- FastAPI Modular Monolith
- Canonical PostgreSQL
- S3-compatible Object Storage
- PostgreSQL-backed Async Queue
- External / Government Provider Adapters
"""

import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.api.v1 import api_v1_router
from app.api.v1.health import router as health_router
from app.config import settings
from app.database import dispose_database
from app.errors import register_error_handlers
from app.logging import correlation_id_ctx, logger, setup_logging


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and graceful shutdown."""
    setup_logging(settings.LOG_LEVEL)
    logger.info(
        f"Starting {settings.PROJECT_NAME} v{settings.VERSION} "
        f"[env={settings.ENVIRONMENT}, debug={settings.DEBUG}]"
    )
    yield
    logger.info("Shutting down SAMBAL Backend...")
    await dispose_database()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Propagates or generates an X-Request-ID correlation header across requests."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = correlation_id_ctx.set(req_id)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = req_id
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Response-Time-Ms"] = str(duration_ms)

            # Avoid logging raw health check pings excessively
            if not request.url.path.startswith("/health"):
                logger.info(
                    f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)"
                )
            return response
        finally:
            correlation_id_ctx.reset(token)


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=(
            "Multilingual Trauma-Aware Intelligence & Response Layer for NHAA (14566) "
            "and Integrated Portal. Sponsoring Organization: MoSJE / DoSJE."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Register Middlewares
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register RFC 7807 Error Handlers
    register_error_handlers(app)

    # Mount Telemetry Health Endpoints at root and under api_v1
    app.include_router(health_router)
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_application()
