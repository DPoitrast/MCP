"""Herd service containing business logic with enhanced type safety."""

import logging
from sqlite3 import Connection
from typing import Dict, List, Optional, Union, Any

from ..core.config import settings
from ..exceptions import ResourceNotFoundError, ValidationError, BusinessLogicError
from .. import models
from ..repositories import HerdRepository
from ..schemas import HerdCreate, HerdUpdate, HerdList, Herd as HerdSchema
from ..utils.model_converters import convert_domain_to_schema, convert_domain_list_to_schema

logger = logging.getLogger(__name__)


class HerdService:
    """Enhanced service layer for herd business logic with comprehensive validation."""

    def __init__(self, repository: Optional[HerdRepository] = None) -> None:
        """Initialize the herd service with optional dependency injection."""
        self.repository = repository or HerdRepository()

    def validate_pagination(self, skip: int, limit: int) -> None:
        """Validate pagination parameters with enhanced error messages."""
        if skip < 0:
            raise ValidationError(
                field="skip", 
                message="Skip must be non-negative",
                value=skip,
                constraints=["skip >= 0"]
            )

        if limit <= 0:
            raise ValidationError(
                field="limit", 
                message="Limit must be positive",
                value=limit,
                constraints=["limit > 0"]
            )

        if limit > settings.max_query_limit:
            raise ValidationError(
                field="limit", 
                message=f"Limit cannot exceed {settings.max_query_limit}",
                value=limit,
                constraints=[f"limit <= {settings.max_query_limit}"]
            )

    def get_herds(self, db: Connection, skip: int = 0, limit: Optional[int] = None) -> HerdList:
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

    def get_herd_by_id(self, db: Connection, herd_id: int) -> HerdSchema:
        """Get a specific herd by ID with enhanced validation."""
        self._validate_herd_id(herd_id)

        domain_herd = self.repository.get_by_id(db, herd_id)
        if not domain_herd:
            raise ResourceNotFoundError("Herd", herd_id)

        # Convert domain model to Pydantic model
        pydantic_herd = convert_domain_to_schema(domain_herd, HerdSchema)

        logger.debug(f"Retrieved herd {herd_id}: {pydantic_herd.name}")
        return pydantic_herd

    def search_herds_by_name(self, db: Connection, name: str) -> List[HerdSchema]:
        """Search herds by name (partial match) with validation."""
        self._validate_search_term(name, "name")

        domain_herds = self.repository.get_by_name(db, name.strip())
        
        # Convert domain models to Pydantic models
        pydantic_herds = convert_domain_list_to_schema(domain_herds, HerdSchema)
        
        logger.debug(f"Found {len(pydantic_herds)} herds matching name '{name}'")
        return pydantic_herds

    def search_herds_by_location(self, db: Connection, location: str) -> List[HerdSchema]:
        """Search herds by location (partial match) with validation."""
        self._validate_search_term(location, "location")

        domain_herds = self.repository.get_by_location(db, location.strip())
        
        # Convert domain models to Pydantic models
        pydantic_herds = convert_domain_list_to_schema(domain_herds, HerdSchema)
        
        logger.debug(f"Found {len(pydantic_herds)} herds matching location '{location}'")
        return pydantic_herds

    def create_herd(self, db: Connection, herd_data: HerdCreate) -> HerdSchema:
        """Create a new herd with comprehensive validation."""
        self._validate_herd_creation(db, herd_data)

        try:
            domain_herd = self.repository.create(db, herd_data)
        except Exception as e:
            logger.error(f"Failed to create herd: {e}")
            raise BusinessLogicError(
                message="Failed to create herd due to database constraints",
                rule="unique_herd_name",
                context={"herd_name": herd_data.name}
            )
        
        # Convert domain model to Pydantic model
        pydantic_herd = convert_domain_to_schema(domain_herd, HerdSchema)
        
        logger.info(f"Created new herd: {pydantic_herd.name} at {pydantic_herd.location}")
        return pydantic_herd

    def update_herd(self, db: Connection, herd_id: int, herd_data: HerdUpdate) -> HerdSchema:
        """Update an existing herd with validation."""
        self._validate_herd_id(herd_id)

        # Check if herd exists
        if not self.repository.exists(db, herd_id):
            raise ResourceNotFoundError("Herd", herd_id)

        self._validate_herd_update(db, herd_id, herd_data)

        try:
            updated_domain_herd = self.repository.update(db, herd_id, herd_data)
            if not updated_domain_herd:
                raise ResourceNotFoundError("Herd", herd_id)
        except Exception as e:
            logger.error(f"Failed to update herd {herd_id}: {e}")
            raise BusinessLogicError(
                message="Failed to update herd due to database constraints",
                rule="unique_herd_name",
                context={"herd_id": herd_id, "herd_name": herd_data.name}
            )

        # Convert domain model to Pydantic model
        updated_herd = convert_domain_to_schema(updated_domain_herd, HerdSchema)

        logger.info(f"Updated herd {herd_id}: {updated_herd.name}")
        return updated_herd

    def delete_herd(self, db: Connection, herd_id: int) -> None:
        """Delete a herd by ID with validation."""
        self._validate_herd_id(herd_id)

        # Check if herd exists before attempting deletion
        if not self.repository.exists(db, herd_id):
            raise ResourceNotFoundError("Herd", herd_id)

        # Business rule: Check if herd can be deleted
        self._validate_herd_deletion(db, herd_id)

        deleted = self.repository.delete(db, herd_id)
        if not deleted:
            raise BusinessLogicError(
                message="Failed to delete herd",
                rule="herd_deletion_constraint",
                context={"herd_id": herd_id}
            )

        logger.info(f"Deleted herd {herd_id}")

    def get_herd_statistics(self, db: Connection) -> Dict[str, Any]:
        """Get comprehensive statistics about herds."""
        total_herds = self.repository.count(db)

        # Additional statistics
        stats = {
            "total_herds": total_herds,
            "max_query_limit": settings.max_query_limit,
            "default_query_limit": settings.default_query_limit,
            "has_herds": total_herds > 0,
        }

        # Add location-based statistics if we have herds
        if total_herds > 0:
            # This would require additional repository methods
            # stats["herds_by_location"] = self.repository.get_location_counts(db)
            pass

        logger.debug(f"Generated herd statistics: {stats}")
        return stats

    # Private validation methods
    def _validate_herd_id(self, herd_id: int) -> None:
        """Validate herd ID parameter."""
        if herd_id <= 0:
            raise ValidationError(
                field="herd_id", 
                message="Herd ID must be positive",
                value=herd_id,
                constraints=["herd_id > 0"]
            )

    def _validate_search_term(self, term: str, field_name: str) -> None:
        """Validate search term parameters."""
        if not term or not term.strip():
            raise ValidationError(
                field=field_name,
                message=f"Search {field_name} cannot be empty",
                value=term,
                constraints=["non-empty string"]
            )

        if len(term.strip()) < 2:
            raise ValidationError(
                field=field_name,
                message=f"Search {field_name} must be at least 2 characters",
                value=term,
                constraints=["length >= 2"]
            )

    def _validate_herd_creation(self, db: Connection, herd_data: HerdCreate) -> None:
        """Validate herd creation business rules."""
        # Check for duplicate names (if repository supports it)
        # This would require additional repository methods
        pass

    def _validate_herd_update(self, db: Connection, herd_id: int, herd_data: HerdUpdate) -> None:
        """Validate herd update business rules."""
        # Check for duplicate names when updating (if repository supports it)
        # This would require additional repository methods
        pass

    def _validate_herd_deletion(self, db: Connection, herd_id: int) -> None:
        """Validate herd deletion business rules."""
        # Example: Check if herd has dependent records
        # This would require additional repository methods or business rules
        pass
