"""FastAPI application with clean architecture."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.api import api_router
from .core.config import settings
from .core.database import init_db
from .exceptions import MCPException

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    logger.info(f"Starting {settings.title} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    yield
    # Shutdown
    logger.info("Shutting down application")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Create FastAPI app
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        openapi_url=(
            f"{settings.api_v1_prefix}/openapi.json" if settings.debug else None
        ),
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Add global exception handlers
    @app.exception_handler(MCPException)
    async def mcp_exception_handler(request: Request, exc: MCPException):
        """Handle custom MCP exceptions."""
        logger.warning(f"MCP exception on {request.url}: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "detail": exc.message,
                "error_code": exc.error_code,
                "error_id": str(id(exc)), # Add unique error ID
                "type": "business_error",
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error_id": str(id(exc)),
                "type": "internal_error",
            },
        )

    # Lifespan events handled by lifespan context manager

    return app


# Create the app instance
app = create_application()
