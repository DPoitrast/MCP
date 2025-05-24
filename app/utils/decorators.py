"""Common decorators for API endpoints."""

import logging
from functools import wraps
from typing import Callable, Any

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def handle_service_exceptions(endpoint_name: str = "endpoint"):
    """
    Decorator to handle common service exceptions in API endpoints.
    
    Args:
        endpoint_name: Name of the endpoint for logging purposes
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except ValueError as e:
                logger.warning(f"{endpoint_name} - Validation error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
            except KeyError as e:
                logger.warning(f"{endpoint_name} - Missing required field: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {e}"
                )
            except Exception as e:
                logger.error(f"{endpoint_name} - Unexpected error: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                )
        return wrapper
    return decorator


def handle_not_found(resource_name: str = "Resource"):
    """
    Decorator to handle resource not found cases.
    
    Args:
        resource_name: Name of the resource for error messages
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            result = await func(*args, **kwargs)
            if result is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{resource_name} not found"
                )
            return result
        return wrapper
    return decorator