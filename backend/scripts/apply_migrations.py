#!/usr/bin/env python
"""
CodeAcademy Pro — Aplicador de migraciones idempotente.

Por qué existe (y no se usa scripts/run_migrations.py):
  * run_migrations.py tiene la URL hardcodeada a localhost, importa psycopg2
    (que NO está en requirements.txt) y re-ejecuta 001..022 en cada corrida,
    así que falla en la 001 si las tablas ya existen.
  * Este script lee DATABASE_URL del entorno, usa asyncpg (ya en requirements),
    y lleva una tabla de control `schema_migrations` → cada archivo se aplica
    UNA sola vez, y se detecta si un archivo cambió después de aplicarse.

Uso (dentro del contenedor backend, con DATABASE_URL seteada):
    python scripts/apply_migrations.py            # aplica las pendientes
    python scripts/apply_migrations.py --status   # solo lista el estado
    python scripts/apply_migrations.py --baseline # marca las pendientes como
                                                  # aplicadas SIN ejecutarlas
                                                  # (BD preexistente)
    python scripts/apply_migrations.py --seed     # aplica pendientes + datos demo

`--baseline` es para una base que ya se inicializó con docker-entrypoint-initdb.d
(volumen de postgres creado por el compose viejo): el SQL ya corrió, pero no hay
registro, y volver a ejecutarlo reventaría.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import re
import ssl
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

BACKEND_DIR = Path(__file__).resolve().parent.parent
TRACKING_TABLE = "schema_migrations"
EXPLICIT_TX_RE = re.compile(r"^\s*(BEGIN|START\s+TRANSACTION)\b", re.IGNORECASE | re.MULTILINE)


def resolve_migrations_dir() -> Path:
    """
    Ubica las migraciones en los dos layouts que existen:

      * repo      → repo/database/migrations   (script en repo/backend/scripts/)
      * contenedor → /app/migrations            (el Dockerfile las copia ahí)

    `MIGRATIONS_DIR` en el entorno tiene prioridad sobre ambos.
    """
    candidates = []
    if os.environ.get("MIGRATIONS_DIR"):
        candidates.append(Path(os.environ["MIGRATIONS_DIR"]))
    candidates += [
        BACKEND_DIR.parent / "database" / "migrations",
        BACKEND_DIR / "migrations",
        BACKEND_DIR.parent / "migrations",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    tried = "\n  ".join(str(c) for c in candidates)
    sys.exit(f"ERROR: no se encontró el directorio de migraciones. Probados:\n  {tried}")


MIGRATIONS_DIR = None  # se resuelve en main() para poder informar el error completo


# ── Conexión ──────────────────────────────────────────────────────────────────

def connect_kwargs_from_env() -> dict:
    """Traduce DATABASE_URL (formato SQLAlchemy) a kwargs de asyncpg."""
    raw = os.environ.get("DATABASE_URL", "").strip()
    if not raw:
        sys.exit("ERROR: falta DATABASE_URL en el entorno.")

    dsn = raw.replace("postgresql+asyncpg://", "postgresql://", 1)
    parts = urlsplit(dsn)
    if not parts.hostname:
        sys.exit(f"ERROR: DATABASE_URL inválida: {raw!r}")

    query = parse_qs(parts.query)
    kwargs: dict = {
        "host": parts.hostname,
        "port": parts.port or 5432,
        "user": unquote(parts.username or "postgres"),
        "password": unquote(parts.password or ""),
        "database": (parts.path or "/postgres").lstrip("/") or "postgres",
        "timeout": 60,
    }

    # SSL (Supabase exige TLS). Semántica libpq: require = cifra sin verificar.
    sslmode = (query.get("sslmode") or [os.environ.get("PGSSLMODE", "")])[0]
    if sslmode in {"require", "allow", "prefer"}:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs["ssl"] = ctx
    elif sslmode in {"verify-ca", "verify-full"}:
        kwargs["ssl"] = ssl.create_default_context()

    return kwargs


def checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ── Migraciones ───────────────────────────────────────────────────────────────

async def apply(args: argparse.Namespace) -> int:
    import asyncpg

    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        sys.exit(f"ERROR: no hay archivos .sql en {MIGRATIONS_DIR}")

    conn = await asyncpg.connect(**connect_kwargs_from_env())
    try:
        created = not await conn.fetchval(
            "SELECT to_regclass($1) IS NOT NULL", f"public.{TRACKING_TABLE}"
        )
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TRACKING_TABLE} (
                filename   VARCHAR(255) PRIMARY KEY,
                checksum   VARCHAR(64)  NOT NULL,
                applied_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
            )
            """
        )

        applied = {
            row["filename"]: row["checksum"]
            for row in await conn.fetch(f"SELECT filename, checksum FROM {TRACKING_TABLE}")
        }
        pending = [f for f in files if f.name not in applied]

        if args.status:
            print(f"Tabla de control: {TRACKING_TABLE} ({len(applied)} registros)")
            for f in files:
                mark = "aplicada" if f.name in applied else "PENDIENTE"
                print(f"  [{mark:9}] {f.name}")
            return 0

        # BD preexistente sin registro de control: pedir --baseline explícito.
        if created and not applied:
            users_exists = await conn.fetchval("SELECT to_regclass('public.users') IS NOT NULL")
            if users_exists and not args.baseline:
                print(
                    "ERROR: la base ya tiene tablas (public.users existe) y no hay registro\n"
                    "       en schema_migrations. Si esa base se creó con\n"
                    "       docker-entrypoint-initdb.d, corré con --baseline para marcar\n"
                    "       las migraciones como aplicadas sin re-ejecutarlas.\n"
                    "       Si es una base nueva, revisá manualmente antes de continuar.",
                    file=sys.stderr,
                )
                return 2

        if args.baseline:
            if not pending:
                print("Nada que marcar: todas las migraciones ya están registradas.")
                return 0
            for f in pending:
                text = f.read_text(encoding="utf-8")
                await conn.execute(
                    f"INSERT INTO {TRACKING_TABLE} (filename, checksum) VALUES ($1, $2)",
                    f.name,
                    checksum(text),
                )
                print(f"  marcada sin ejecutar: {f.name}")
            print(f"Baseline listo: {len(pending)} migraciones marcadas como aplicadas.")
            return 0

        if not pending:
            print("No hay migraciones pendientes.")
        for f in pending:
            text = f.read_text(encoding="utf-8")
            print(f"→ {f.name}", flush=True)
            if EXPLICIT_TX_RE.search(text):
                # El archivo trae su propio BEGIN/COMMIT: no anidar transacción.
                await conn.execute(text)
            else:
                async with conn.transaction():
                    await conn.execute(text)
            await conn.execute(
                f"INSERT INTO {TRACKING_TABLE} (filename, checksum) VALUES ($1, $2)",
                f.name,
                checksum(text),
            )
            print("  ok")

        # Archivos aplicados que cambiaron después (drift).
        for f in files:
            if f.name in applied:
                current = checksum(f.read_text(encoding="utf-8"))
                if current != applied[f.name]:
                    print(f"  AVISO: {f.name} cambió después de aplicarse (checksum distinto)")

        if args.seed:
            print("\n→ Ejecutando seed de datos demo (scripts/seed_data.py)…", flush=True)
            result = subprocess.run(
                [sys.executable, "scripts/seed_data.py"],
                cwd=BACKEND_DIR,
                env=os.environ.copy(),
            )
            if result.returncode != 0:
                print("ERROR: el seed falló.", file=sys.stderr)
                return result.returncode

        print("\nMigraciones al día.")
        return 0
    finally:
        await conn.close()


def main() -> int:
    global MIGRATIONS_DIR
    MIGRATIONS_DIR = resolve_migrations_dir()

    parser = argparse.ArgumentParser(description="Aplica las migraciones SQL de CodeAcademy Pro (idempotente).")
    parser.add_argument("--status", action="store_true", help="solo mostrar el estado de cada migración")
    parser.add_argument("--baseline", action="store_true", help="marcar las pendientes como aplicadas sin ejecutarlas")
    parser.add_argument("--seed", action="store_true", help="ejecutar también scripts/seed_data.py")
    args = parser.parse_args()
    return asyncio.run(apply(args))


if __name__ == "__main__":
    sys.exit(main())
