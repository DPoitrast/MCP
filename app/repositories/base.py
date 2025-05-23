"""Base repository class with common CRUD operations."""

import logging
from abc import ABC, abstractmethod
from sqlite3 import Connection
from typing import Any, Dict, List, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseRepository(ABC):
    """Abstract base repository class."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    @abstractmethod
    def _row_to_model(self, row: Dict[str, Any]) -> T:
        """Convert database row to domain model."""
        pass
    
    def _execute_query(self, db: Connection, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dicts."""
        try:
            cursor = db.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Query execution failed: {query} with params {params} - {e}")
            raise
    
    def _execute_single(self, db: Connection, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and return single result or None."""
        try:
            cursor = db.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Single query execution failed: {query} with params {params} - {e}")
            raise
    
    def _execute_insert(self, db: Connection, query: str, params: tuple = ()) -> int:
        """Execute an insert query and return the new row ID."""
        try:
            cursor = db.execute(query, params)
            row_id = cursor.lastrowid
            if row_id is None:
                raise ValueError("Insert failed: no ID returned")
            return row_id
        except Exception as e:
            logger.error(f"Insert execution failed: {query} with params {params} - {e}")
            raise
    
    def _execute_update(self, db: Connection, query: str, params: tuple = ()) -> int:
        """Execute an update/delete query and return affected row count."""
        try:
            cursor = db.execute(query, params)
            return cursor.rowcount
        except Exception as e:
            logger.error(f"Update execution failed: {query} with params {params} - {e}")
            raise