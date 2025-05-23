"""Herd repository for data access operations."""

import logging
from sqlite3 import Connection
from typing import Dict, List, Optional, Any

from .base import BaseRepository
from ..models import Herd
from ..schemas import HerdCreate, HerdUpdate
from ..exceptions import HerdNotFoundError

logger = logging.getLogger(__name__)


class HerdRepository(BaseRepository):
    """Repository for herd data access operations."""

    def __init__(self):
        super().__init__("herd")

    def _row_to_model(self, row: Dict[str, Any]) -> Herd:
        """Convert database row to Herd model."""
        return Herd(
            id=row["id"],
            name=row["name"],
            location=row["location"],
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def get_all(self, db: Connection, skip: int = 0, limit: int = 100) -> List[Herd]:
        """Retrieve herds with pagination."""
        query = """
            SELECT id, name, location, created_at, updated_at 
            FROM herd 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """
        rows = self._execute_query(db, query, (limit, skip))
        herds = [self._row_to_model(row) for row in rows]
        logger.debug(f"Retrieved {len(herds)} herds (skip={skip}, limit={limit})")
        return herds

    def get_by_id(self, db: Connection, herd_id: int) -> Optional[Herd]:
        """Retrieve a specific herd by ID."""
        query = """
            SELECT id, name, location, created_at, updated_at 
            FROM herd 
            WHERE id = ?
        """
        row = self._execute_single(db, query, (herd_id,))
        return self._row_to_model(row) if row else None

    def get_by_name(self, db: Connection, name: str) -> List[Herd]:
        """Retrieve herds by name (partial match)."""
        query = """
            SELECT id, name, location, created_at, updated_at 
            FROM herd 
            WHERE name LIKE ? 
            ORDER BY name
        """
        rows = self._execute_query(db, query, (f"%{name}%",))
        return [self._row_to_model(row) for row in rows]

    def get_by_location(self, db: Connection, location: str) -> List[Herd]:
        """Retrieve herds by location (partial match)."""
        query = """
            SELECT id, name, location, created_at, updated_at 
            FROM herd 
            WHERE location LIKE ? 
            ORDER BY location, name
        """
        rows = self._execute_query(db, query, (f"%{location}%",))
        return [self._row_to_model(row) for row in rows]

    def create(self, db: Connection, herd_data: HerdCreate) -> Herd:
        """Create a new herd."""
        query = """
            INSERT INTO herd (name, location) 
            VALUES (?, ?)
        """
        herd_id = self._execute_insert(db, query, (herd_data.name, herd_data.location))

        # Retrieve the created herd
        created_herd = self.get_by_id(db, herd_id)
        if not created_herd:
            raise ValueError("Failed to retrieve created herd")

        logger.info(
            f"Created herd {herd_id}: {created_herd.name} at {created_herd.location}"
        )
        return created_herd

    def update(
        self, db: Connection, herd_id: int, herd_data: HerdUpdate
    ) -> Optional[Herd]:
        """Update an existing herd."""
        # Build dynamic update query
        update_fields = []
        params = []

        if herd_data.name is not None:
            update_fields.append("name = ?")
            params.append(herd_data.name)

        if herd_data.location is not None:
            update_fields.append("location = ?")
            params.append(herd_data.location)

        if not update_fields:
            # No fields to update, return existing herd
            return self.get_by_id(db, herd_id)

        query = f"""
            UPDATE herd 
            SET {', '.join(update_fields)}
            WHERE id = ?
        """
        params.append(herd_id)

        affected_rows = self._execute_update(db, query, tuple(params))
        if affected_rows == 0:
            return None

        # Retrieve the updated herd
        updated_herd = self.get_by_id(db, herd_id)
        logger.info(f"Updated herd {herd_id}")
        return updated_herd

    def delete(self, db: Connection, herd_id: int) -> bool:
        """Delete a herd by ID."""
        query = "DELETE FROM herd WHERE id = ?"
        affected_rows = self._execute_update(db, query, (herd_id,))
        deleted = affected_rows > 0

        if deleted:
            logger.info(f"Deleted herd {herd_id}")
        else:
            logger.warning(f"Attempted to delete non-existent herd {herd_id}")

        return deleted

    def count(self, db: Connection) -> int:
        """Get total count of herds."""
        query = "SELECT COUNT(*) as count FROM herd"
        row = self._execute_single(db, query)
        return row["count"] if row else 0

    def exists(self, db: Connection, herd_id: int) -> bool:
        """Check if a herd exists by ID."""
        query = "SELECT 1 FROM herd WHERE id = ? LIMIT 1"
        row = self._execute_single(db, query, (herd_id,))
        return row is not None
