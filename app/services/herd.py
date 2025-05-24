"""Herd service containing business logic."""

import logging
from sqlite3 import Connection
from typing import List, Optional

from ..core.config import settings
from ..exceptions import HerdNotFoundError, ValidationError
from .. import models
from ..repositories import HerdRepository
from ..schemas import HerdCreate, HerdUpdate, HerdList, Herd as HerdSchema
from ..utils.model_converters import convert_domain_to_schema, convert_domain_list_to_schema

logger = logging.getLogger(__name__)


class HerdService:
    """Service layer for herd business logic."""

    def __init__(self):
        self.repository = HerdRepository()

    def validate_pagination(self, skip: int, limit: int) -> None:
        """Validate pagination parameters."""
        if skip < 0:
            raise ValidationError("skip", "Skip must be non-negative")

        if limit <= 0:
            raise ValidationError("limit", "Limit must be positive")

        if limit > settings.max_query_limit:
            raise ValidationError(
                "limit", f"Limit cannot exceed {settings.max_query_limit}"
            )

    def get_herds(self, db: Connection, skip: int = 0, limit: int = None) -> HerdList:
        """Get paginated list of herds with total count."""
        if limit is None:
            limit = settings.default_query_limit

        self.validate_pagination(skip, limit)

        # Get herds and total count
        domain_herds = self.repository.get_all(db, skip, limit)
        total = self.repository.count(db)

        # Convert domain models to Pydantic models
        pydantic_herds = convert_domain_list_to_schema(domain_herds, HerdSchema)

        logger.info(
            f"Retrieved {len(pydantic_herds)} herds (skip={skip}, limit={limit}, total={total})"
        )

        return HerdList(items=pydantic_herds, total=total, skip=skip, limit=limit)

    def get_herd_by_id(self, db: Connection, herd_id: int):
        """Get a specific herd by ID."""
        if herd_id <= 0:
            raise ValidationError("herd_id", "Herd ID must be positive")

        domain_herd = self.repository.get_by_id(db, herd_id)
        if not domain_herd:
            raise HerdNotFoundError(herd_id)

        # Convert domain model to Pydantic model
        pydantic_herd = convert_domain_to_schema(domain_herd, HerdSchema)

        logger.debug(f"Retrieved herd {herd_id}: {pydantic_herd.name}")
        return pydantic_herd

    def search_herds_by_name(self, db: Connection, name: str):
        """Search herds by name (partial match)."""
        if not name or not name.strip():
            raise ValidationError("name", "Search name cannot be empty")

        domain_herds = self.repository.get_by_name(db, name.strip())
        
        # Convert domain models to Pydantic models
        pydantic_herds = convert_domain_list_to_schema(domain_herds, HerdSchema)
        
        logger.debug(f"Found {len(pydantic_herds)} herds matching name '{name}'")
        return pydantic_herds

    def search_herds_by_location(self, db: Connection, location: str):
        """Search herds by location (partial match)."""
        if not location or not location.strip():
            raise ValidationError("location", "Search location cannot be empty")

        domain_herds = self.repository.get_by_location(db, location.strip())
        
        # Convert domain models to Pydantic models
        pydantic_herds = convert_domain_list_to_schema(domain_herds, HerdSchema)
        
        logger.debug(f"Found {len(pydantic_herds)} herds matching location '{location}'")
        return pydantic_herds

    def create_herd(self, db: Connection, herd_data: HerdCreate):
        """Create a new herd."""
        # Additional business logic validation could go here
        # For example, check for duplicate names, validate location format, etc.

        domain_herd = self.repository.create(db, herd_data)
        
        # Convert domain model to Pydantic model
        pydantic_herd = convert_domain_to_schema(domain_herd, HerdSchema)
        
        logger.info(f"Created new herd: {pydantic_herd.name} at {pydantic_herd.location}")
        return pydantic_herd

    def update_herd(self, db: Connection, herd_id: int, herd_data: HerdUpdate):
        """Update an existing herd."""
        if herd_id <= 0:
            raise ValidationError("herd_id", "Herd ID must be positive")

        # Check if herd exists
        if not self.repository.exists(db, herd_id):
            raise HerdNotFoundError(herd_id)

        # Additional business logic validation could go here
        # For example, check for conflicts with other herds, etc.

        updated_domain_herd = self.repository.update(db, herd_id, herd_data)
        if not updated_domain_herd:
            raise HerdNotFoundError(herd_id)

        # Convert domain model to Pydantic model
        updated_herd = convert_domain_to_schema(updated_domain_herd, HerdSchema)

        logger.info(f"Updated herd {herd_id}: {updated_herd.name}")
        return updated_herd

    def delete_herd(self, db: Connection, herd_id: int) -> None:
        """Delete a herd by ID."""
        if herd_id <= 0:
            raise ValidationError("herd_id", "Herd ID must be positive")

        # Check if herd exists before attempting deletion
        if not self.repository.exists(db, herd_id):
            raise HerdNotFoundError(herd_id)

        deleted = self.repository.delete(db, herd_id)
        if not deleted:
            raise HerdNotFoundError(herd_id)

        logger.info(f"Deleted herd {herd_id}")

    def get_herd_statistics(self, db: Connection) -> dict:
        """Get statistics about herds."""
        total_herds = self.repository.count(db)

        # Could add more statistics here like:
        # - Herds by location
        # - Creation trends
        # - etc.

        return {
            "total_herds": total_herds,
            "max_query_limit": settings.max_query_limit,
            "default_query_limit": settings.default_query_limit,
        }
