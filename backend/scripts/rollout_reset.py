"""
CodeAcademy Pro — Database Rollout Reset
Elimina TODOS los registros y crea solo el usuario admin.
Usa conexion directa con el superusuario postgres.
Uso: python scripts/rollout_reset.py
"""

import os
import sys
import asyncio
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password
import bcrypt

# ── Conexion directa con superusuario (no RLS) ──────────────────────────
DB_URL = "postgresql+asyncpg://postgres:password@localhost:5432/academy_db"

TABLES_TO_TRUNCATE = [
    "attendance_records",
    "background_jobs",
    "content_versions",
    "email_queue",
    "payment_proofs",
    "payments",
    "enrollments",
    "recorded_classes",
    "live_classes",
    "lessons",
    "modules",
    "course_classes",
    "courses",
    "categories",
    "user_roles",
    "students",
    "teachers",
    "audit_logs",
    "feature_flags",
    "system_settings",
    "payment_settings",
    "users",
    "roles",
]

ROLES = [
    ("admin", "System Administrator"),
    ("teacher", "Instructor"),
    ("student", "Platform Student"),
    ("user", "Registered User (no specific role)"),
    ("coordinator", "Program Coordinator"),
]


async def rollout_reset():
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    engine_async = create_async_engine(DB_URL)
    session_factory = async_sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as conn:
        # ── 1. Truncate all tables ─────────────────────────────────────
        print("Truncando todas las tablas...")
        for table in TABLES_TO_TRUNCATE:
            await conn.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
        print("[OK] Todas las tablas vacias.\n")

        # ── 2. Re-create roles ─────────────────────────────────────────
        print("Creando roles...")
        role_ids = {}
        for role_name, role_desc in ROLES:
            rid = uuid.uuid4()
            result = await conn.execute(
                text(
                    "INSERT INTO roles (id, name, description) VALUES (:id, :name, :desc) "
                    "ON CONFLICT (name) DO NOTHING "
                    "RETURNING id"
                ),
                {"id": rid, "name": role_name, "desc": role_desc},
            )
            row = result.fetchone()
            if row:
                role_ids[role_name] = row[0]
            else:
                id_result = await conn.execute(
                    text("SELECT id FROM roles WHERE name = :name"),
                    {"name": role_name},
                )
                role_ids[role_name] = id_result.scalar_one()
        print(f"[OK] {len(ROLES)} roles creados.")

        # ── 3. Create Admin User ───────────────────────────────────────
        print("\nCreando usuario Admin...")
        pwd_hash = hash_password("Admin123!")
        admin_id = uuid.uuid4()
        await conn.execute(
            text("""
                INSERT INTO users (id, email, username, password_hash, first_name, last_name, status, is_blocked, email_verified)
                VALUES (:id, :email, :username, :pwd, :first, :last, 'active', false, true)
            """),
            {
                "id": admin_id,
                "email": "admin@codeacademypro.com",
                "username": "admin",
                "pwd": pwd_hash,
                "first": "Admin",
                "last": "Sistema",
            },
        )

        await conn.execute(
            text("INSERT INTO user_roles (id, user_id, role_id) VALUES (:id, :uid, :rid)"),
            {"id": uuid.uuid4(), "uid": admin_id, "rid": role_ids["admin"]},
        )
        print("[OK] Admin creado: admin@codeacademypro.com / Admin123!")

        # ── 4. System Settings defaults ───────────────────────────────
        print("\nInsertando configuraciones del sistema...")
        settings_defaults = [
            ("default_currency", "USD"),
            ("global_max_students_per_class", "100"),
        ]
        for key, value in settings_defaults:
            await conn.execute(
                text(
                    "INSERT INTO system_settings (id, key, value, is_public) VALUES (:id, :key, :value, false) "
                    "ON CONFLICT (key) DO NOTHING"
                ),
                {"id": uuid.uuid4(), "key": key, "value": value},
            )
        print("[OK] Configuraciones del sistema listas.")

        await conn.commit()

    await engine_async.dispose()

    print("\n" + "=" * 50)
    print("Rollout completado - Base de datos limpia")
    print("  Admin: admin@codeacademypro.com")
    print("  Pass:  Admin123!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(rollout_reset())
