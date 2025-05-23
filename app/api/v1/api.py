"""API v1 router configuration."""

from fastapi import APIRouter

from .endpoints import health, herd

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(herd.router, prefix="", tags=["herd"])
