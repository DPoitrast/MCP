"""Herd API endpoints."""

import logging
from sqlite3 import Connection
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ....core.security import CurrentUser
from ....models.user import AuthenticatedUserModel
from ....schemas import Herd, HerdCreate, HerdUpdate, HerdList
from ....services import HerdService
# Removed handle_service_exceptions from imports
from ....utils.decorators import handle_not_found
from ...dependencies import Database, HerdServiceDep

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/herd", response_model=HerdList, tags=["herd"])
# @handle_service_exceptions("list_herds") # Removed decorator
async def list_herds(
    skip: int = Query(0, ge=0, description="Number of herds to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of herds to return"),
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: AuthenticatedUserModel = CurrentUser,
):
    """
    Get a paginated list of herds.

    Args:
        skip: Number of herds to skip (for pagination)
        limit: Maximum number of herds to return
        db: Database connection
        herd_service: Herd service instance
        current_user: Current authenticated user

    Returns:
        HerdList: Paginated list of herds with metadata
    """
    result = herd_service.get_herds(db, skip, limit)
    logger.info(
        f"User {current_user.username} listed herds (skip={skip}, limit={limit})"
    )
    return result


@router.get("/herd/stats", tags=["herd"])
# @handle_service_exceptions("get_herd_statistics") # Removed decorator
async def get_herd_statistics(
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: AuthenticatedUserModel = CurrentUser,
):
    """
    Get statistics about herds.

    Args:
        db: Database connection
        herd_service: Herd service instance
        current_user: Current authenticated user

    Returns:
        dict: Statistics about herds
    """
    stats = herd_service.get_herd_statistics(db)
    logger.info(f"User {current_user.username} retrieved herd statistics")
    return stats


@router.get("/herd/{herd_id}", response_model=Herd, tags=["herd"])
# @handle_service_exceptions("get_herd") # Removed decorator
@handle_not_found("Herd")
async def get_herd(
    herd_id: int,
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: AuthenticatedUserModel = CurrentUser,
):
    """
    Get a specific herd by ID.

    Args:
        herd_id: ID of the herd to retrieve
        db: Database connection
        herd_service: Herd service instance
        current_user: Current authenticated user

    Returns:
        Herd: The requested herd

    Raises:
        HTTPException: 404 if herd not found, 400 for invalid ID
    """
    herd = herd_service.get_herd_by_id(db, herd_id)
    logger.info(f"User {current_user.username} retrieved herd {herd_id}")
    return herd


@router.get("/herd/search/name", response_model=List[Herd], tags=["herd"])
# @handle_service_exceptions("search_herds_by_name") # Removed decorator
async def search_herds_by_name(
    name: str = Query(..., min_length=1, description="Name to search for"),
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: AuthenticatedUserModel = CurrentUser,
):
    """
    Search herds by name (partial match).

    Args:
        name: Name to search for
        db: Database connection
        herd_service: Herd service instance
        current_user: Current authenticated user

    Returns:
        List[Herd]: List of matching herds
    """
    herds = herd_service.search_herds_by_name(db, name)
    logger.info(
        f"User {current_user.username} searched herds by name '{name}', found {len(herds)} results"
    )
    return herds


@router.get("/herd/search/location", response_model=List[Herd], tags=["herd"])
# @handle_service_exceptions("search_herds_by_location") # Removed decorator
async def search_herds_by_location(
    location: str = Query(..., min_length=1, description="Location to search for"),
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: AuthenticatedUserModel = CurrentUser,
):
    """
    Search herds by location (partial match).

    Args:
        location: Location to search for
        db: Database connection
        herd_service: Herd service instance
        current_user: Current authenticated user

    Returns:
        List[Herd]: List of matching herds
    """
    herds = herd_service.search_herds_by_location(db, location)
    logger.info(
        f"User {current_user.username} searched herds by location '{location}', found {len(herds)} results"
    )
    return herds


@router.post(
    "/herd", response_model=Herd, status_code=status.HTTP_201_CREATED, tags=["herd"]
)
# @handle_service_exceptions("create_herd") # Removed decorator
async def create_herd(
    herd_data: HerdCreate,
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: AuthenticatedUserModel = CurrentUser,
):
    """
    Create a new herd.

    Args:
        herd_data: Herd data to create
        db: Database connection
        herd_service: Herd service instance
        current_user: Current authenticated user

    Returns:
        Herd: The created herd
    """
    herd = herd_service.create_herd(db, herd_data)
    logger.info(
        f"User {current_user.username} created herd {herd.id}: {herd.name}"
    )
    return herd


@router.put("/herd/{herd_id}", response_model=Herd, tags=["herd"])
# @handle_service_exceptions("update_herd") # Removed decorator
@handle_not_found("Herd")
async def update_herd(
    herd_id: int,
    herd_data: HerdUpdate,
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: AuthenticatedUserModel = CurrentUser,
):
    """
    Update an existing herd.

    Args:
        herd_id: ID of the herd to update
        herd_data: Updated herd data
        db: Database connection
        herd_service: Herd service instance
        current_user: Current authenticated user

    Returns:
        Herd: The updated herd

    Raises:
        HTTPException: 404 if herd not found, 400 for invalid data
    """
    herd = herd_service.update_herd(db, herd_id, herd_data)
    logger.info(f"User {current_user.username} updated herd {herd_id}")
    return herd


@router.delete("/herd/{herd_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["herd"])
# @handle_service_exceptions("delete_herd") # Removed decorator
@handle_not_found("Herd")
async def delete_herd(
    herd_id: int,
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: AuthenticatedUserModel = CurrentUser,
):
    """
    Delete a herd by ID.

    Args:
        herd_id: ID of the herd to delete
        db: Database connection
        herd_service: Herd service instance
        current_user: Current authenticated user

    Raises:
        HTTPException: 404 if herd not found, 400 for invalid ID
    """
    herd_service.delete_herd(db, herd_id)
    logger.info(f"User {current_user.username} deleted herd {herd_id}")
