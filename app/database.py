import os
import sqlite3
from contextlib import contextmanager


def get_db_path() -> str:
    """Return the path to the SQLite database."""
    return os.environ.get("DATABASE_PATH", "mcp.db")


def init_db() -> None:
    """Create database tables if they do not exist."""
    with sqlite3.connect(get_db_path()) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS herd (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, location TEXT)"
        )


@contextmanager
def get_db():
    """Yield a SQLite connection using the configured database path."""
    conn = sqlite3.connect(get_db_path())
    try:
        yield conn
    finally:
        conn.close()
