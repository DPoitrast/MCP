import sqlite3
from contextlib import contextmanager

DATABASE_PATH = "mcp.db"


def init_db():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS herd (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, location TEXT)"
        )


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()
