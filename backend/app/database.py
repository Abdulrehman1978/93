"""Canonical PostgreSQL Database Connection & Health Verification.

PostgreSQL 16+ is authoritative across development integration, migrations,
database testing, E2E, CI, staging, and production.
SQLite is prohibited as a production or integration alternative.
"""

import time
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.logging import logger

# Create Canonical Async Engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Async Session Factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database sessions."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def check_database_health() -> tuple[bool, float | None, str | None]:
    """Execute a lightweight SELECT 1 query to verify PostgreSQL connectivity and latency."""
    start_time = time.perf_counter()
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return True, latency_ms, "PostgreSQL connection operational"
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.warning(f"Database health check failed: {exc}")
        return False, latency_ms, "Database connection unavailable"


async def dispose_database() -> None:
    """Safely dispose database connection pool on shutdown."""
    await engine.dispose()
    logger.info("Canonical PostgreSQL connection pool closed.")
