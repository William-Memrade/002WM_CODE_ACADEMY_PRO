#!/usr/bin/env python
"""
CodeAcademy Pro — Compara los modelos SQLAlchemy contra la base real.

Por qué existe: la cadena de migraciones SQL no es la fuente de verdad del esquema
(el caso users.status lo demostró: el modelo y el código la usaban, ninguna
migración la creaba y 004 se caía). Este script refleja la base y la compara con
`Base.metadata` para decir, en segundos, si lo que hay en Postgres alcanza para
que el ORM funcione.

Uso (dentro del contenedor backend o con el venv, con DATABASE_URL seteada):

    python scripts/check_schema_drift.py             # informe + exit 1 si falta algo
    python scripts/check_schema_drift.py --extra     # muestra también lo que sobra
    python scripts/check_schema_drift.py --table users

Salida: tablas que faltan, columnas que el ORM espera y no existen (esto es lo que
rompe en runtime) y, con --extra, columnas que están en la base y ningún modelo usa
(normalmente residuo de refactors, no rompe nada).
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import pkgutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app.models as models_pkg  # noqa: E402
from app.models.base import Base  # noqa: E402
from apply_migrations import connect_kwargs_from_env  # noqa: E402


def load_all_models() -> None:
    """Importa todos los módulos de app/models para poblar Base.metadata."""
    importlib.import_module("app.models")
    for module in pkgutil.iter_modules(models_pkg.__path__):
        if module.name != "base":
            importlib.import_module(f"app.models.{module.name}")


async def reflect_columns(conn) -> dict[str, set[str]]:
    """{tabla: {columna, ...}} solo de tablas reales de public (no vistas)."""
    rows = await conn.fetch(
        """
        SELECT c.table_name, c.column_name
          FROM information_schema.columns c
          JOIN pg_tables t
            ON t.schemaname = c.table_schema AND t.tablename = c.table_name
         WHERE c.table_schema = 'public'
        """
    )
    tables: dict[str, set[str]] = {}
    for row in rows:
        tables.setdefault(row["table_name"], set()).add(row["column_name"])
    return tables


async def check(args: argparse.Namespace) -> int:
    import asyncpg

    load_all_models()
    orm_tables = {
        table.name: {column.name for column in table.columns}
        for table in Base.metadata.tables.values()
        if table.schema in (None, "public")
    }
    if args.table:
        orm_tables = {t: c for t, c in orm_tables.items() if t == args.table}
        if not orm_tables:
            sys.exit(f"ERROR: la tabla {args.table!r} no existe en los modelos.")

    conn = await asyncpg.connect(**connect_kwargs_from_env())
    try:
        db_tables = await reflect_columns(conn)
    finally:
        await conn.close()

    missing_tables: list[str] = []
    missing_columns: list[tuple[str, list[str]]] = []
    extra_columns: list[tuple[str, list[str]]] = []

    for table, columns in sorted(orm_tables.items()):
        if table not in db_tables:
            missing_tables.append(table)
            continue
        missing = sorted(columns - db_tables[table])
        if missing:
            missing_columns.append((table, missing))
        extra = sorted(
            db_tables[table] - columns - {"id", "created_at", "updated_at", "deleted_at"}
        )
        if extra:
            extra_columns.append((table, extra))

    print(f"Tablas en los modelos: {len(orm_tables)} | tablas en la base: {len(db_tables)}")

    if missing_tables:
        print(f"\n✗ FALTAN {len(missing_tables)} TABLAS:")
        for table in missing_tables:
            print(f"    - {table}")
    if missing_columns:
        total = sum(len(c) for _, c in missing_columns)
        print(f"\n✗ FALTAN {total} COLUMNAS (el ORM fallaría al consultarlas):")
        for table, columns in missing_columns:
            print(f"    - {table}: {', '.join(columns)}")
    if args.extra and extra_columns:
        print("\n· Columnas en la base que ningún modelo declara (no rompen nada):")
        for table, columns in extra_columns:
            print(f"    - {table}: {', '.join(columns)}")

    if missing_tables or missing_columns:
        print(
            "\nRESULTADO: esquema INCOMPLETO — falta una migración que cree lo anterior.\n"
            "           (pasó con users.status: lo usaba el modelo y ninguna migración lo creaba)"
        )
        return 1

    print("\nRESULTADO: esquema alineado con los modelos.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compara los modelos SQLAlchemy con las tablas reales de la base."
    )
    parser.add_argument("--extra", action="store_true", help="listar columnas residuales")
    parser.add_argument("--table", help="revisar solo una tabla")
    return asyncio.run(check(parser.parse_args()))


if __name__ == "__main__":
    sys.exit(main())
