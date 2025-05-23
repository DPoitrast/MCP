import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Generator

logger = logging.getLogger(__name__)


def get_db_path() -> str:
    """Return the path to the SQLite database."""
    return os.environ.get("DATABASE_PATH", "mcp.db")


def init_db() -> None:
    """Create database tables if they do not exist."""
    try:
        with sqlite3.connect(get_db_path()) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute(
                "CREATE TABLE IF NOT EXISTS herd (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, location TEXT NOT NULL)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_herd_name ON herd(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_herd_location ON herd(location)")
            conn.commit()
            logger.info("Database tables and indexes created successfully")
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection with proper error handling and transactions."""
    conn = None
    try:
        conn = sqlite3.connect(get_db_path(), timeout=30.0)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error in database operation: {e}")
        raise
    finally:
        if conn:
            conn.close()
