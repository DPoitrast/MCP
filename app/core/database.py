"""Database configuration and connection management."""

import logging
import sqlite3
from contextlib import contextmanager
from typing import Generator

from .config import settings
from ..exceptions import DatabaseError

logger = logging.getLogger(__name__)


def get_db_path() -> str:
    """Return the path to the SQLite database."""
    return settings.database_path


def init_db() -> None:
    """Create database tables if they do not exist."""
    try:
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS herd (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL CHECK(length(name) > 0),
                    location TEXT NOT NULL CHECK(length(location) > 0),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_herd_name ON herd(name)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_herd_location ON herd(location)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_herd_created_at ON herd(created_at)"
            )

            # Create trigger to update updated_at timestamp
            conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS update_herd_timestamp 
                AFTER UPDATE ON herd
                BEGIN
                    UPDATE herd SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END
                """
            )

            conn.commit()
            logger.info("Database tables and indexes created successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise DatabaseError("initialization", e)


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection with proper error handling and transactions."""
    conn = None
    try:
        conn = sqlite3.connect(
            get_db_path(), timeout=settings.connection_timeout, check_same_thread=False
        )
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")  # Better concurrency
        conn.row_factory = sqlite3.Row

        # Start transaction
        conn.execute("BEGIN")
        yield conn
        conn.commit()

    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise DatabaseError("operation", e)
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in database operation: {e}")
        raise DatabaseError("unexpected", e)
    finally:
        if conn:
            conn.close()


def check_db_health() -> bool:
    """Check if database is accessible and responsive."""
    try:
        with get_db() as db:
            db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
