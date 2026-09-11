"""
CodeAcademy Pro — Pruebas de integración (capa 2).

Qué prueban: la app completa en proceso —middleware, router, servicio, SQLAlchemy y
RLS reales— contra la base de pruebas migrada y sembrada con el seed real. Sin
servidor, sin puerto, sin mocks de base.

Qué NO prueban todavía (ver docs/architecture/TESTING.md): los flujos de negocio
completos (inscripción → pago → aprobación), el contrato de los 83 endpoints y el
comportamiento bajo carga. Esto es el cimiento: si el cimiento se rompe, todo lo
demás miente.
"""

import pytest

from tests.support import auth_headers, login

pytestmark = pytest.mark.integration


async def test_health_responde(api_client):
    response = await api_client.get("/health")
    assert response.status_code == 200


async def test_openapi_expone_el_contrato(api_client):
    """
    El contrato publicado tiene que seguir teniendo la misma superficie.

    Son dos números distintos: 66 rutas (paths) y 80 operaciones (path + método).
    Los pisos están un poco por debajo de los de hoy para que un refactor legítimo
    no rompa el test, pero si caen muy por debajo es que un router dejó de montarse.
    """
    response = await api_client.get("/openapi.json")
    assert response.status_code == 200

    paths = response.json()["paths"]
    operations = sum(len(methods) for methods in paths.values())

    assert len(paths) >= 60, f"el contrato se encogió: {len(paths)} rutas"
    assert operations >= 75, f"se perdieron operaciones: {operations}"
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/courses" in paths


async def test_login_demo_devuelve_token(api_client):
    token = await login(api_client, "admin")
    assert token


async def test_login_rechaza_password_incorrecta(api_client):
    response = await api_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@codeacademypro.com", "password": "PasswordIncorrecta1_"},
    )
    assert response.status_code == 401


async def test_users_me_devuelve_el_usuario_del_token(api_client, tokens):
    response = await api_client.get(
        "/api/v1/users/me", headers=auth_headers(tokens["admin"])
    )
    assert response.status_code == 200
    assert response.json()["email"] == "admin@codeacademypro.com"


async def test_sin_token_la_api_esta_cerrada(api_client):
    response = await api_client.get("/api/v1/users/me")
    assert response.status_code == 401


@pytest.mark.parametrize("role", ["teacher", "student"])
async def test_audit_logs_es_solo_para_admin(api_client, tokens, role):
    """RBAC de verdad: el rol equivocado no entra, no es que 'no vea datos'."""
    response = await api_client.get(
        "/api/v1/audit-logs", headers=auth_headers(tokens[role])
    )
    assert response.status_code == 403


async def test_admin_si_entra_a_audit_logs(api_client, tokens):
    response = await api_client.get(
        "/api/v1/audit-logs", headers=auth_headers(tokens["admin"])
    )
    assert response.status_code == 200
