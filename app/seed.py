from .core.database import get_db, init_db


def seed():
    """Seed the database with initial data."""
    init_db()
    with get_db() as db:
        count = db.execute("SELECT COUNT(*) FROM herd").fetchone()[0]
        if count == 0:
            db.execute(
                "INSERT INTO herd (name, location) VALUES (?, ?)",
                ("Alpha Farm", "Wisconsin"),
            )
            db.execute(
                "INSERT INTO herd (name, location) VALUES (?, ?)",
                ("Beta Farm", "California"),
            )
            print("Database seeded with initial data")
        else:
            print(f"Database already contains {count} herds")


if __name__ == "__main__":
    seed()
