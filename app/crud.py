import logging
from sqlite3 import Connection
from typing import List, Optional

from . import models, schemas

logger = logging.getLogger(__name__)


def get_herd(db: Connection, skip: int = 0, limit: int = 100) -> List[models.Herd]:
    """Retrieve herds with pagination and proper error handling."""
    try:
        cursor = db.execute("SELECT id, name, location FROM herd LIMIT ? OFFSET ?", (limit, skip))
        rows = cursor.fetchall()
        herds = [models.Herd(id=row["id"], name=row["name"], location=row["location"]) for row in rows]
        logger.debug(f"Retrieved {len(herds)} herds (skip={skip}, limit={limit})")
        return herds
    except Exception as e:
        logger.error(f"Failed to retrieve herds: {e}")
        raise


def create_herd(db: Connection, herd: schemas.HerdCreate) -> models.Herd:
    """Create a new herd with transaction safety."""
    try:
        cursor = db.execute(
            "INSERT INTO herd (name, location) VALUES (?, ?)", (herd.name, herd.location)
        )
        db.commit()
        herd_id = cursor.lastrowid
        if herd_id is None:
            raise ValueError("Failed to create herd: no ID returned")
        
        new_herd = models.Herd(id=herd_id, name=herd.name, location=herd.location)
        logger.info(f"Created herd: {new_herd.name} at {new_herd.location}")
        return new_herd
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create herd: {e}")
        raise


def get_herd_by_id(db: Connection, herd_id: int) -> Optional[models.Herd]:
    """Retrieve a specific herd by ID."""
    try:
        cursor = db.execute("SELECT id, name, location FROM herd WHERE id = ?", (herd_id,))
        row = cursor.fetchone()
        if row:
            return models.Herd(id=row["id"], name=row["name"], location=row["location"])
        return None
    except Exception as e:
        logger.error(f"Failed to retrieve herd {herd_id}: {e}")
        raise


def delete_herd(db: Connection, herd_id: int) -> bool:
    """Delete a herd by ID."""
    try:
        cursor = db.execute("DELETE FROM herd WHERE id = ?", (herd_id,))
        db.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Deleted herd {herd_id}")
        else:
            logger.warning(f"Attempted to delete non-existent herd {herd_id}")
        return deleted
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete herd {herd_id}: {e}")
        raise
