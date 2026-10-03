"""API v1 Router Package."""

from fastapi import APIRouter

from app.api.v1.channel import router as channel_router
from app.api.v1.health import router as health_router
from app.api.v1.security import router as security_router

api_v1_router = APIRouter()
api_v1_router.include_router(health_router, tags=["Health & Telemetry"])
api_v1_router.include_router(security_router)
api_v1_router.include_router(channel_router)
