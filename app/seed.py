from .database import get_db, init_db
from . import models


def seed():
    init_db()
    with get_db() as db:
        count = db.execute("SELECT COUNT(*) FROM herd").fetchone()[0]
        if count == 0:
            db.execute("INSERT INTO herd (name, location) VALUES (?, ?)", ("Alpha Farm", "Wisconsin"))
            db.execute("INSERT INTO herd (name, location) VALUES (?, ?)", ("Beta Farm", "California"))
            db.commit()


if __name__ == "__main__":
    seed()
