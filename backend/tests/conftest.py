"""
CodeAcademy Pro — Fixtures compartidas.

`configure_test_env()` corre en la primera línea, antes de que ningún test importe
módulos de la app: los settings son un singleton cacheado y el engine de SQLAlchemy
se construye en import-time, así que después ya es tarde.

Capas:
  - Pruebas unitarias (test_cors, test_security_headers, test_password_policy…):
    no necesitan nada de aquí, corren siempre.
  - Pruebas de integración (api_client / tokens): necesitan PostgreSQL y Redis. Si no
    están levantados se SALTAN con el comando exacto para levantarlos, no fallan.
"""

from __future__ import annotations

import httpx
import pytest
import pytest_asyncio

from tests import support

support.configure_test_env()


# ── Base de datos de pruebas ─────────────────────────────────────────────────

@pytest.fixture(scope="session")
def prepared_database() -> str:
    """Base `academy_test` creada, migrada y sembrada (una sola vez por corrida)."""
    return support.prepare_database()


# ── Cliente HTTP contra la app en proceso ────────────────────────────────────

@pytest_asyncio.fixture
async def api_client(prepared_database: str):
    """
    Cliente httpx contra la app ASGI en proceso (sin servidor ni puerto).

    Se envuelve la app completa —incluido el wrapper de security headers— porque
    es lo que realmente se despliega.

    El rate limiter se inicializa y se limpia por test. Los contadores viven en
    Redis (no en el objeto limiter), así que si no se vacía la base de test el
    quinto login de la corrida se lleva un 429 y el test falla por el orden en que
    se ejecutó, no por un bug. La base 15 está reservada para las pruebas.
    """
    import redis.asyncio as redis

    from app.middlewares.rate_limit import setup_rate_limiter, teardown_rate_limiter
    from main import app as asgi_app

    redis_client = redis.from_url(support.TEST_REDIS_URL, encoding="utf-8", decode_responses=True)
    await redis_client.flushdb()

    fastapi_app = getattr(asgi_app, "app", asgi_app)  # SecurityHeadersASGI envuelve la FastAPI
    await setup_rate_limiter(fastapi_app)
    transport = httpx.ASGITransport(app=asgi_app)
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client
    finally:
        # El engine de la app es un singleton de módulo CON pool: la primera conexión
        # queda atada al event loop del primer test y, cuando ese loop se cierra,
        # reutilizarla revienta con "RuntimeError: Event loop is closed". Devolver el
        # pool al final de cada test deja que el siguiente abra sus conexiones en su
        # propio loop. No es un parche al test: es la consecuencia de que la app
        # asuma una sola vida por proceso y pytest use un loop por test.
        from app.db.session import engine as app_engine

        await app_engine.dispose()
        await teardown_rate_limiter()
        await redis_client.aclose()


# ── Sesiones autenticadas ────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def tokens(api_client: httpx.AsyncClient) -> dict[str, str]:
    """Tokens de los tres roles demo: tokens["admin"|"teacher"|"student"]."""
    return {role: await support.login(api_client, role) for role in support.DEMO_USERS}


# ── Utillaje de montaje (conexión privilegiada) ──────────────────────────────

@pytest_asyncio.fixture
async def superuser_session(prepared_database: str):
    """
    Sesión contra la base de pruebas como superusuario (sin RLS).

    Para MONTAR y LIMPIAR datos que no tienen endpoint de alta (una inscripción, un pago
    pendiente) o para leer la verdad de la base sin que RLS la filtre. Los endpoints se
    ejercitan siempre por HTTP con el rol RLS real.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

    engine = create_async_engine(support.TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    try:
        async with factory() as session:
            yield session
            await session.rollback()
    finally:
        await engine.dispose()
