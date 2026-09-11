#!/usr/bin/env python
"""
CodeAcademy Pro — Bootstrap de la base en el arranque del contenedor.

Por qué existe:
  En Render el *pre-deploy command* (el hook pensado para migraciones) solo está
  disponible en servicios de pago, y los cron jobs / background workers tampoco
  existen en el plan free. La forma de que "deploy = base al día" sin pasos
  manuales es hacerlo en el arranque del contenedor del API.

Qué hace, según la variable BOOTSTRAP_DB:

  off           (default) no toca la base. Es lo correcto en local: ahí manda el
                servicio `migrate` del docker-compose, que corre antes que el API.
  migrate       aplica las migraciones pendientes.
  seed          siembra los datos demo SOLO si public.users está vacía.
  migrate+seed  migraciones + lo anterior.

Propiedades que lo hacen seguro de repetir (arranque, cold start de Render,
restart manual):

  * apply_migrations.py es idempotente y lleva la tabla de control
    schema_migrations; solo ejecuta lo que falta.
  * Corre bajo un pg_advisory_lock, así que dos instancias que arranquen a la vez
    (deploy solapado, CI + contenedor) se serializan.
  * El seed (python scripts/seed_data.py) también es idempotente, y acá encima se
    ejecuta solo con la tabla de usuarios vacía: en un restart normal no siembra
    nada.

Si el bootstrap falla, este script sale con código != 0 y el contenedor NO
arranca. Eso es a propósito: mejor un deploy fallido y visible (con la versión
anterior todavía sirviendo) que un API en pie con la base a medias.

Uso local (probar el mismo camino que usará Render):

    BOOTSTRAP_DB=migrate+seed DATABASE_URL='postgresql+asyncpg://...' \
        python scripts/bootstrap_db.py
"""

from __future__ import annotations

import os
import subprocess
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VALID_MODES = ("off", "migrate", "seed", "migrate+seed")


def main() -> int:
    mode = (os.environ.get("BOOTSTRAP_DB") or "off").strip().lower()

    if mode in ("", "off", "none", "false", "0"):
        print("[bootstrap_db] BOOTSTRAP_DB=off → no se toca la base.", flush=True)
        return 0

    if mode not in VALID_MODES:
        print(
            f"[bootstrap_db] ERROR: BOOTSTRAP_DB={mode!r} no es válido. "
            f"Valores: {', '.join(VALID_MODES)} (o vacío para desactivarlo).",
            file=sys.stderr,
        )
        return 2

    if not os.environ.get("DATABASE_URL"):
        print("[bootstrap_db] ERROR: falta DATABASE_URL en el entorno.", file=sys.stderr)
        return 2

    args = [sys.executable, "scripts/apply_migrations.py"]
    # mode == "migrate": sin flags extra → aplica lo pendiente y no siembra.
    if mode in ("seed", "migrate+seed"):
        args.append("--seed-if-empty")

    print(f"[bootstrap_db] BOOTSTRAP_DB={mode} → {' '.join(args[1:]) or 'aplicar migraciones'}…", flush=True)
    result = subprocess.run(args, cwd=BACKEND_DIR, env=os.environ.copy())
    if result.returncode != 0:
        print(
            f"[bootstrap_db] FALLÓ (código {result.returncode}). El contenedor no arranca; "
            "revisá el error de arriba.",
            file=sys.stderr,
        )
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
