#!/usr/bin/env python
"""
Assign student role to users without any role.
Ensures test users can submit payment proofs.
"""
import psycopg2
from pathlib import Path

db_url = "postgresql://postgres:password@localhost:5432/academy_db"
conn = psycopg2.connect(db_url)
cursor = conn.cursor()

try:
    # Get or create student role
    cursor.execute("SELECT id FROM roles WHERE name = 'student' LIMIT 1")
    result = cursor.fetchone()
    if not result:
        print("✗ Student role not found. Please run seed migrations first.")
        cursor.close()
        conn.close()
        exit(1)
    
    student_role_id = result[0]
    print(f"✓ Found student role: {student_role_id}")
    
    # Find users without roles
    cursor.execute("""
        SELECT u.id, u.email, u.username FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM user_roles ur WHERE ur.user_id = u.id
        )
        AND u.deleted_at IS NULL
    """)
    
    users_without_roles = cursor.fetchall()
    
    if not users_without_roles:
        print("✓ All users already have roles.")
        cursor.close()
        conn.close()
        exit(0)
    
    print(f"✓ Found {len(users_without_roles)} users without roles:")
    for user_id, email, username in users_without_roles:
        print(f"  - {username} ({email})")
    
    # Assign student role to all users without roles
    for user_id, email, username in users_without_roles:
        cursor.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
            (user_id, student_role_id)
        )
        print(f"  ✓ Assigned student role to {username}")
    
    conn.commit()
    print("\n✓ All users now have the student role assigned!")
    
except psycopg2.Error as e:
    print(f"✗ Database error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
