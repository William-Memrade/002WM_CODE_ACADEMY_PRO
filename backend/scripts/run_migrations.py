#!/usr/bin/env python
"""
Run all database migrations in order.
"""
import psycopg2
import re
from pathlib import Path


def run_migrations():
    """
    Run all database migrations in order.
    """
    db_url = "postgresql://postgres:password@localhost:5432/academy_db"

    # Parse connection params
    match = re.match(r"postgresql://(\w+):(\w+)@([\w.]+):(\d+)/(\w+)", db_url)
    if not match:
        print("Invalid DATABASE_URL format")
        return False

    user, pwd, host, port, dbname = match.groups()

    try:
        conn = psycopg2.connect(
            user=user,
            password=pwd,
            host=host,
            port=int(port),
            dbname=dbname
        )
        cursor = conn.cursor()

        # Run all migrations in order
        migration_dir = Path(__file__).parent.parent.parent / "database" / "migrations"
        for f in sorted(migration_dir.glob("*.sql")):
            print(f"Running: {f.name}")
            with open(f, "r") as sql_file:
                cursor.execute(sql_file.read())
            conn.commit()
            print(f"  ✓ OK")

        cursor.close()
        conn.close()
        print("\n✓ All migrations completed successfully!")
        return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    SUCCESS = run_migrations()
    exit(0 if SUCCESS else 1)
