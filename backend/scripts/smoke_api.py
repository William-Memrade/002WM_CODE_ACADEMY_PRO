#!/usr/bin/env python
"""
CodeAcademy Pro — Smoke test de la API (recorre todos los GET sin parámetros).

Para qué sirve: después de cada despliegue (local, Render, Supabase) responde en
30 segundos "¿la API está sana de punta a punta?" y detecta lo que rompe en runtime
y no en import-time — típicamente columnas o tablas que el ORM espera y la base no
tiene (ver scripts/check_schema_drift.py, que lo detecta antes de arrancar).

    python scripts/smoke_api.py                                    # localhost:8000
    python scripts/smoke_api.py --base-url https://mi-api.onrender.com

Usa los usuarios demo del seed. Sale con 1 si hay errores 5xx (bug de servidor);
los 4xx se listan como aviso porque muchos son RBAC esperado (401/403/404).
"""

from __future__ import annotations

import argparse
import sys

import httpx

DEMO_USERS = {
    "admin": ("admin@codeacademypro.com", "Admin123!"),
    "teacher": ("ana.garcia@codeacademypro.com", "Teacher123!"),
    "student": ("estudiante@codeacademypro.com", "Student123!"),
}
EXPECTED = {401, 403}  # RBAC: no es un fallo


def login(client: httpx.Client, email: str, password: str) -> str | None:
    try:
        response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    except httpx.HTTPError as exc:
        print(f"  ! no se pudo autenticar {email}: {exc}")
        return None
    if response.status_code != 200:
        print(f"  ! login {email} → {response.status_code} {response.text[:120]}")
        return None
    return response.json().get("access_token")


def collect_endpoints(client: httpx.Client) -> list[str]:
    schema = client.get("/openapi.json").json()
    endpoints = []
    for path, methods in sorted(schema.get("paths", {}).items()):
        operation = methods.get("get")
        if not operation or "{" in path:
            continue
        params = operation.get("parameters", [])
        if any(p.get("required") and p.get("in") == "query" for p in params):
            continue
        endpoints.append(path)
    return endpoints


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test de los GET de la API.")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    results: list[tuple[int, str, str]] = []
    servers_down = 0

    with httpx.Client(base_url=args.base_url, timeout=args.timeout) as client:
        try:
            health = client.get("/health")
        except httpx.HTTPError as exc:
            print(f"ERROR: la API no responde en {args.base_url} ({exc})")
            return 2
        print(f"Base: {args.base_url} · /health → {health.status_code}")

        tokens = {}
        for role, (email, password) in DEMO_USERS.items():
            token = login(client, email, password)
            if token:
                tokens[role] = token
        print(f"Sesiones obtenidas: {', '.join(tokens) or 'ninguna'}\n")

        endpoints = collect_endpoints(client)
        print(f"Recorriendo {len(endpoints)} endpoints GET sin parámetros obligatorios…\n")

        for path in endpoints:
            best: tuple[int, str] = (0, "")
            for role in ("admin", "teacher", "student"):
                token = tokens.get(role)
                if not token:
                    continue
                try:
                    response = client.get(path, headers={"Authorization": f"Bearer {token}"})
                except httpx.HTTPError as exc:
                    best = (0, f"error de transporte: {exc}")
                    break
                if response.status_code not in EXPECTED:
                    best = (response.status_code, response.text[:160].replace("\n", " "))
                    break
                best = (response.status_code, response.text[:160].replace("\n", " "))
            # Sin token (endpoints públicos)
            if best[0] == 0:
                response = client.get(path)
                best = (response.status_code, response.text[:160].replace("\n", " "))

            status, detail = best
            results.append((status, path, detail))
            if status >= 500 or status == 0:
                servers_down += 1
                print(f"  ✗ {status} {path}\n      {detail}")

    ok = [r for r in results if 200 <= r[0] < 400]
    denied = [r for r in results if r[0] in EXPECTED]
    client_err = [r for r in results if 400 <= r[0] < 500 and r[0] not in EXPECTED]

    print(
        f"\nResumen: {len(ok)} OK · {len(denied)} protegidos (401/403) · "
        f"{len(client_err)} 4xx · {servers_down} errores de servidor"
    )
    for status, path, detail in client_err:
        print(f"  · {status} {path} — {detail[:120]}")

    if servers_down:
        print("\nRESULTADO: hay errores 5xx → bug de servidor (revisar los logs del backend).")
        return 1
    print("\nRESULTADO: sin errores de servidor.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
