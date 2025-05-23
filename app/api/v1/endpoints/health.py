"""Health check endpoints."""

import logging
from fastapi import APIRouter, HTTPException, status

from ....core.database import check_db_health

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring service status.
    
    Returns:
        dict: Health status information
    
    Raises:
        HTTPException: 503 if service is unhealthy
    """
    try:
        db_healthy = check_db_health()
        
        if not db_healthy:
            logger.error("Health check failed: database not accessible")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unavailable - database connection failed"
            )
        
        health_status = {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
        
        logger.debug("Health check passed")
        return health_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed with unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


@router.get("/health/database", tags=["health"])
async def database_health_check():
    """
    Detailed database health check.
    
    Returns:
        dict: Database health information
    """
    try:
        db_healthy = check_db_health()
        
        return {
            "database_connected": db_healthy,
            "status": "healthy" if db_healthy else "unhealthy"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "database_connected": False,
            "status": "unhealthy",
            "error": str(e)
        }