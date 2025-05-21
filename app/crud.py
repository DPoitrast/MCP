from sqlite3 import Connection

from . import models, schemas


def get_herd(db: Connection, skip: int = 0, limit: int = 100):
    cursor = db.execute("SELECT id, name, location FROM herd LIMIT ? OFFSET ?", (limit, skip))
    rows = cursor.fetchall()
    return [models.Herd(id=row[0], name=row[1], location=row[2]) for row in rows]


def create_herd(db: Connection, herd: schemas.HerdCreate):
    cursor = db.execute(
        "INSERT INTO herd (name, location) VALUES (?, ?)", (herd.name, herd.location)
    )
    db.commit()
    herd_id = cursor.lastrowid
    return models.Herd(id=herd_id, name=herd.name, location=herd.location)
