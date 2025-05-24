"""API v1 router configuration."""

from fastapi import APIRouter

from .endpoints import health, herd, auth, mcp

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="", tags=["health"])
api_router.include_router(herd.router, prefix="", tags=["herd"])
api_router.include_router(auth.router, prefix="", tags=["authentication"])
api_router.include_router(mcp.router, prefix="", tags=["mcp"])
