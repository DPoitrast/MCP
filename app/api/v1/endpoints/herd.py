"""Herd API endpoints."""

import logging
from sqlite3 import Connection
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ....core.security import CurrentUser
from ....exceptions import HerdNotFoundError, ValidationError, DatabaseError
from ....schemas import Herd, HerdCreate, HerdUpdate, HerdList
from ....services import HerdService
from ...dependencies import Database, HerdServiceDep

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/herd", response_model=HerdList, tags=["herd"])
async def list_herds(
    skip: int = Query(0, ge=0, description="Number of herds to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of herds to return"),
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        result = herd_service.get_herds(db, skip, limit)
        logger.info(f"User {current_user.get('sub')} listed herds (skip={skip}, limit={limit})")
        return result
    except ValidationError as e:
        logger.warning(f"Validation error in list_herds: {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Database error in list_herds: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve herds")
    except Exception as e:
        logger.error(f"Unexpected error in list_herds: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/herd/stats", tags=["herd"])
async def get_herd_statistics(
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        stats = herd_service.get_herd_statistics(db)
        logger.info(f"User {current_user.get('sub')} retrieved herd statistics")
        return stats
    except DatabaseError as e:
        logger.error(f"Database error in get_herd_statistics: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve statistics")
    except Exception as e:
        logger.error(f"Unexpected error in get_herd_statistics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/herd/{herd_id}", response_model=Herd, tags=["herd"])
async def get_herd(
    herd_id: int,
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        herd = herd_service.get_herd_by_id(db, herd_id)
        logger.info(f"User {current_user.get('sub')} retrieved herd {herd_id}")
        return herd
    except ValidationError as e:
        logger.warning(f"Validation error in get_herd: {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except HerdNotFoundError as e:
        logger.warning(f"Herd not found: {e.message}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Database error in get_herd: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve herd")
    except Exception as e:
        logger.error(f"Unexpected error in get_herd: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/herd/search/name", response_model=List[Herd], tags=["herd"])
async def search_herds_by_name(
    name: str = Query(..., min_length=1, description="Name to search for"),
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        herds = herd_service.search_herds_by_name(db, name)
        logger.info(f"User {current_user.get('sub')} searched herds by name '{name}', found {len(herds)} results")
        return herds
    except ValidationError as e:
        logger.warning(f"Validation error in search_herds_by_name: {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Database error in search_herds_by_name: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search herds")
    except Exception as e:
        logger.error(f"Unexpected error in search_herds_by_name: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/herd/search/location", response_model=List[Herd], tags=["herd"])
async def search_herds_by_location(
    location: str = Query(..., min_length=1, description="Location to search for"),
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        herds = herd_service.search_herds_by_location(db, location)
        logger.info(f"User {current_user.get('sub')} searched herds by location '{location}', found {len(herds)} results")
        return herds
    except ValidationError as e:
        logger.warning(f"Validation error in search_herds_by_location: {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Database error in search_herds_by_location: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to search herds")
    except Exception as e:
        logger.error(f"Unexpected error in search_herds_by_location: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/herd", response_model=Herd, status_code=status.HTTP_201_CREATED, tags=["herd"])
async def create_herd(
    herd_data: HerdCreate,
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        herd = herd_service.create_herd(db, herd_data)
        logger.info(f"User {current_user.get('sub')} created herd {herd.id}: {herd.name}")
        return herd
    except ValidationError as e:
        logger.warning(f"Validation error in create_herd: {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Database error in create_herd: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create herd")
    except Exception as e:
        logger.error(f"Unexpected error in create_herd: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.put("/herd/{herd_id}", response_model=Herd, tags=["herd"])
async def update_herd(
    herd_id: int,
    herd_data: HerdUpdate,
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        herd = herd_service.update_herd(db, herd_id, herd_data)
        logger.info(f"User {current_user.get('sub')} updated herd {herd_id}")
        return herd
    except ValidationError as e:
        logger.warning(f"Validation error in update_herd: {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except HerdNotFoundError as e:
        logger.warning(f"Herd not found: {e.message}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Database error in update_herd: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update herd")
    except Exception as e:
        logger.error(f"Unexpected error in update_herd: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.delete("/herd/{herd_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["herd"])
async def delete_herd(
    herd_id: int,
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        herd_service.delete_herd(db, herd_id)
        logger.info(f"User {current_user.get('sub')} deleted herd {herd_id}")
    except ValidationError as e:
        logger.warning(f"Validation error in delete_herd: {e.message}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except HerdNotFoundError as e:
        logger.warning(f"Herd not found: {e.message}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except DatabaseError as e:
        logger.error(f"Database error in delete_herd: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete herd")
    except Exception as e:
        logger.error(f"Unexpected error in delete_herd: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/herd/stats", tags=["herd"])
async def get_herd_statistics(
    db: Connection = Depends(Database),
    herd_service: HerdService = Depends(HerdServiceDep),
    current_user: dict = CurrentUser
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
    try:
        stats = herd_service.get_herd_statistics(db)
        logger.info(f"User {current_user.get('sub')} retrieved herd statistics")
        return stats
    except DatabaseError as e:
        logger.error(f"Database error in get_herd_statistics: {e.message}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve statistics")
    except Exception as e:
        logger.error(f"Unexpected error in get_herd_statistics: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")