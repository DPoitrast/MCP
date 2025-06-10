"""FastAPI application with clean architecture."""

import logging
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
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

    # Add CORS middleware with enhanced configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else settings.cors.allowed_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )

    # Include API router
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    # Add enhanced global exception handlers
    @app.exception_handler(MCPException)
    async def mcp_exception_handler(request: Request, exc: MCPException):
        """Handle custom MCP exceptions with structured logging."""
        # Log with structured data
        logger.warning(
            f"MCP exception on {request.url.path}",
            extra={
                "error_data": exc.to_dict(),
                "request_url": str(request.url),
                "request_method": request.method,
                "client_ip": request.client.host if request.client else None
            }
        )
        
        # Determine HTTP status code based on error category
        status_code_map = {
            "validation": 422,
            "authentication": 401,
            "authorization": 403,
            "business_logic": 400,
            "external_service": 503,
            "database": 500,
            "configuration": 500,
            "system": 500
        }
        
        status_code = status_code_map.get(exc.category.value, 400)
        
        return JSONResponse(
            status_code=status_code,
            content={
                "detail": exc.user_message,
                "error_code": exc.error_code,
                "error_id": exc.error_id,
                "category": exc.category.value,
                "severity": exc.severity.value,
                "timestamp": exc.timestamp,
                "type": "business_error",
                **({"details": exc.details} if settings.debug else {})
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions with enhanced logging."""
        from uuid import uuid4
        error_id = str(uuid4())
        
        # Enhanced error logging
        logger.error(
            f"Unhandled exception on {request.url.path}",
            extra={
                "error_id": error_id,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "request_url": str(request.url),
                "request_method": request.method,
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
            exc_info=True
        )
        
        # Don't expose internal errors in production
        detail = "Internal server error" if settings.is_production else str(exc)
        
        return JSONResponse(
            status_code=500,
            content={
                "detail": detail,
                "error_id": error_id,
                "type": "internal_error",
                "timestamp": datetime.utcnow().isoformat(),
                **({"traceback": traceback.format_exc()} if settings.debug else {})
            },
        )

    # Lifespan events handled by lifespan context manager

    return app


# Create the app instance
app = create_application()
