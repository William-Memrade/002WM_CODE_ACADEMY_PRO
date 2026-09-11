"""
CodeAcademy Pro — Infraestructura común de las pruebas.

Por qué un módulo aparte y no todo dentro de conftest.py:

1. El entorno tiene que quedar fijado ANTES de importar cualquier módulo de la app
   (`get_settings()` es un singleton cacheado y el engine de SQLAlchemy se crea en
   import-time). conftest.py llama a `configure_test_env()` en su primera línea.
2. `test_rls.py` necesita la misma URL de base que las pruebas de integración, sin
   depender de conftest (que pytest importa, pero no es un módulo cómodo de importar).

La base de pruebas es SIEMPRE una base aparte (por defecto `academy_test`), creada
desde cero con el migrador real y el seed real. Nunca se apunta a la base de
desarrollo ni a la de producción: los tests escriben.

Variables de entorno reconocidas:
    TEST_ADMIN_DATABASE_URL  conexión de superusuario (crear/migrar la base)
    TEST_DB_NAME             nombre de la base de pruebas (default academy_test)
    TEST_REDIS_URL           Redis del rate limiter (default db 15, aislada)
    TEST_DB_RESET=1          tira el schema public y rehace todo desde cero
"""

from __future__ import annotations

import asyncio
import os
import socket
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

BACKEND_DIR = Path(__file__).resolve().parent.parent

# ── Servicios ─────────────────────────────────────────────────────────────────
# Por defecto, los mismos que publica docker/docker-compose.yml: postgres en 5433
# (5432 queda libre para un postgres local) y redis sin publicar → el de las
# pruebas se levanta aparte. Ver docs/architecture/TESTING.md.
TEST_ADMIN_DATABASE_URL = os.getenv(
    "TEST_ADMIN_DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5433/postgres",
)
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "academy_test")
TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://localhost:6379/15")

# Rol restringido por RLS. La contraseña la fija la migración 009 (es un rol de
# desarrollo/documentación, no un secreto): database/migrations/009_rls_role_and_functions.sql
RLS_ROLE = "academy_app"
RLS_ROLE_PASSWORD = "academy_app_secure_pwd"

# Credenciales de los usuarios demo que crea backend/scripts/seed_data.py.
# Son datos de prueba; si algún día dejan de serlo, esto pasa a variables de entorno.
DEMO_USERS: dict[str, tuple[str, str]] = {
    "admin": ("admin@codeacademypro.com", "Admin123!"),
    "teacher": ("ana.garcia@codeacademypro.com", "Teacher123!"),
    "student": ("estudiante@codeacademypro.com", "Student123!"),
}

JWT_SECRET_FOR_TESTS = "jwt-secret-solo-para-pruebas-no-usar-en-produccion"


# ── Sesiones autenticadas (helpers, no fixtures: sirven en cualquier capa) ───

async def login(client, role: str) -> str:
    """Devuelve un access token para uno de los usuarios demo del seed."""
    email, password = DEMO_USERS[role]
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": password}
    )
    assert response.status_code == 200, (
        f"login de {role} falló: {response.status_code} {response.text[:200]}"
    )
    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _rewrite(url: str, *, db: str | None = None, user: str | None = None, password: str | None = None) -> str:
    """Reescribe base/usuario/contraseña de una URL conservando host y puerto."""
    parts = urlsplit(url)
    if user is not None:
        netloc = f"{user}:{password}@"
        netloc += parts.hostname or ""
        if parts.port:
            netloc += f":{parts.port}"
    else:
        netloc = parts.netloc
    return urlunsplit((parts.scheme, netloc, f"/{db}" if db else parts.path, "", ""))


# Superusuario: crea la base y corre migraciones + seed.
TEST_DATABASE_URL = _rewrite(TEST_ADMIN_DATABASE_URL, db=TEST_DB_NAME)
# Rol RLS: es el que usa la app bajo prueba (así las pruebas ejercitan las políticas).
TEST_RLS_DATABASE_URL = _rewrite(
    TEST_ADMIN_DATABASE_URL, db=TEST_DB_NAME, user=RLS_ROLE, password=RLS_ROLE_PASSWORD
)


def configure_test_env() -> None:
    """
    Fija el entorno de las pruebas.

    Asignación directa (no setdefault) a propósito: si el shell tiene una
    DATABASE_URL exportada apuntando a otro lado, las pruebas escribirían ahí.
    Para apuntar a otro host/puerto se usan las variables TEST_*.
    """
    os.environ["ENVIRONMENT"] = "test"
    os.environ["JWT_SECRET"] = JWT_SECRET_FOR_TESTS
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["DATABASE_RLS_URL"] = TEST_RLS_DATABASE_URL
    os.environ["REDIS_URL"] = TEST_REDIS_URL
    os.environ["CORS_ORIGINS"] = "http://localhost:3000"
    os.environ["RECAPTCHA_ENABLED"] = "false"
    os.environ["SECURITY_HEADERS_ENABLED"] = "true"
    os.environ["HSTS_ENABLED"] = "false"
    os.environ["LOG_LEVEL"] = "WARNING"


# ── Disponibilidad de servicios ───────────────────────────────────────────────

def _tcp_reachable(host: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _service_endpoint(url: str) -> tuple[str, int]:
    parts = urlsplit(url)
    default_port = 5432 if parts.scheme.startswith("postgresql") else 6379
    return parts.hostname or "localhost", parts.port or default_port


def missing_services() -> list[str]:
    """Nombres de los servicios que no responden (vacío = todo listo)."""
    missing = []
    for label, url in (("PostgreSQL", TEST_ADMIN_DATABASE_URL), ("Redis", TEST_REDIS_URL)):
        host, port = _service_endpoint(url)
        if not _tcp_reachable(host, port):
            missing.append(f"{label} ({host}:{port})")
    return missing


SKIP_REASON = (
    "Capa de integración: falta {missing}. Levantá los servicios con:\n"
    '  wsl -e bash -lc "docker compose -f docker/docker-compose.yml up -d postgres redis"\n'
    '  wsl -e bash -lc "docker run -d --rm --name ca-test-redis -p 6379:6379 redis:7-alpine"'
)


def require_services() -> None:
    """Salta el test (no lo falla) si los servicios de la capa de integración no están."""
    import pytest

    missing = missing_services()
    if missing:
        pytest.skip(SKIP_REASON.format(missing=" y ".join(missing)))


# ── Preparación de la base ────────────────────────────────────────────────────

async def _ensure_database_exists() -> bool:
    """Crea la base de pruebas si no existe. Devuelve True si la creó."""
    import asyncpg

    dsn = TEST_ADMIN_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn)
    try:
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB_NAME)
        if exists:
            return False
        await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
        return True
    finally:
        await conn.close()


async def _drop_public_schema() -> None:
    """Escape hatch (TEST_DB_RESET=1): deja la base como recién creada."""
    import asyncpg

    dsn = TEST_DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute("DROP SCHEMA IF EXISTS public CASCADE")
        await conn.execute("CREATE SCHEMA public")
    finally:
        await conn.close()


def _run_migrations() -> None:
    """
    Aplica migraciones + seed con el migrador real.

    `--seed-if-empty` y no `--seed`: si ya hay usuarios, no vuelve a sembrar, así la
    suite es idempotente y no va llenando la base de cursos duplicados en cada corrida.
    DATABASE_RLS_URL se fuerza a la de superusuario a propósito: el seed crea usuarios,
    roles y cursos y en el compose corre privilegiado (servicio `migrate`).
    """
    env = {**os.environ, "DATABASE_URL": TEST_DATABASE_URL, "DATABASE_RLS_URL": TEST_DATABASE_URL}
    result = subprocess.run(
        [sys.executable, "scripts/apply_migrations.py", "--seed-if-empty"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "No se pudo preparar la base de pruebas "
            f"(apply_migrations.py salió con {result.returncode}):\n{result.stdout}\n{result.stderr}"
        )


def prepare_database() -> str:
    """Deja la base de pruebas creada, migrada y sembrada. Devuelve su URL."""
    require_services()

    created = asyncio.run(_ensure_database_exists())
    if not created and os.getenv("TEST_DB_RESET") == "1":
        asyncio.run(_drop_public_schema())

    _run_migrations()
    return TEST_DATABASE_URL

