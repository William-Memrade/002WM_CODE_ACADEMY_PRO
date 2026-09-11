#!/usr/bin/env python
"""
Run payment_settings migration only.
"""
import psycopg2
from pathlib import Path

DB_URL = "postgresql://postgres:password@localhost:5432/academy_db"
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

# Read and execute the migration
migration_file = Path(__file__).parent.parent.parent / "database" / "migrations" / "008_payment_settings.sql"
with open(migration_file, "r") as f:
    migration_sql = f.read()

try:
    cursor.execute(migration_sql)
    conn.commit()
    print("✓ Migration 008_payment_settings.sql executed successfully!")
except psycopg2.Error as e:
    print(f"Database error: {e}")
finally:
    cursor.close()
    conn.close()
