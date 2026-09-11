"""
CodeAcademy Pro — CORS Tests
Validates CORS middleware behavior and Settings CORS validation rules.

Two test categories:
1. Settings validation — tests that the model_validator in Settings correctly
   rejects insecure CORS configurations at startup (no running server needed).
2. Middleware behavior — tests that CORSMiddleware responds with the correct
   headers for allowed/denied origins using FastAPI TestClient.

Run with:
    pytest tests/test_cors.py -v
"""

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from pydantic import ValidationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Minimum env vars required to instantiate Settings (JWT_SECRET, DATABASE_URL)
_BASE_ENV = {
    "JWT_SECRET": "test-secret-key-for-cors-tests",
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test_db",
}


def _make_settings(**overrides):
    """
    Create a Settings instance with the given overrides.

    Uses os.environ patching to avoid leaking into other tests.
    lru_cache on get_settings is bypassed by importing Settings directly.
    """
    from app.core.config import Settings

    env = {**_BASE_ENV, **overrides}
    with patch.dict(os.environ, env, clear=False):
        return Settings(**env)


def _make_test_app(origins: list[str], environment: str = "development"):
    """
    Build a minimal FastAPI app with CORSMiddleware matching main.py config,
    but without DB/Redis dependencies.
    """
    app = FastAPI()

    expose = ["X-Request-ID"]
    if environment == "development":
        expose += ["X-Query-Count", "X-DB-Time-Ms"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=expose,
        max_age=600,
    )

    @app.get("/test")
    async def _test():
        return {"ok": True}

    return app


# ---------------------------------------------------------------------------
# 1. Settings Validation Tests
# ---------------------------------------------------------------------------

class TestCORSSettingsValidation:
    """Verify that Settings.validate_cors_security enforces security rules."""

    # ── development: permissive ──────────────────────────────────────────

    def test_dev_allows_localhost(self):
        """Development allows http://localhost:3000."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="http://localhost:3000",
        )
        assert "http://localhost:3000" in s.cors_origins_list

    def test_dev_allows_127(self):
        """Development allows http://127.0.0.1:3000."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="http://127.0.0.1:3000",
        )
        assert "http://127.0.0.1:3000" in s.cors_origins_list

    def test_dev_allows_wildcard(self):
        """Development allows wildcard '*'."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="*",
        )
        assert "*" in s.cors_origins_list

    def test_dev_warns_on_empty(self):
        """Development does NOT raise on empty CORS_ORIGINS (just warns)."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="",
        )
        assert s.cors_origins_list == []

    # ── production: strict ───────────────────────────────────────────────

    def test_production_rejects_empty(self):
        """Production raises if CORS_ORIGINS is empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            _make_settings(ENVIRONMENT="production", CORS_ORIGINS="")

    def test_production_rejects_wildcard(self):
        """Production raises if CORS_ORIGINS contains '*'."""
        with pytest.raises(ValidationError, match="not allowed"):
            _make_settings(ENVIRONMENT="production", CORS_ORIGINS="*")

    def test_production_rejects_localhost(self):
        """Production raises if CORS_ORIGINS contains localhost."""
        with pytest.raises(ValidationError, match="Local origin"):
            _make_settings(
                ENVIRONMENT="production",
                CORS_ORIGINS="http://localhost:3000",
            )

    def test_production_rejects_127(self):
        """Production raises if CORS_ORIGINS contains 127.0.0.1."""
        with pytest.raises(ValidationError, match="Local origin"):
            _make_settings(
                ENVIRONMENT="production",
                CORS_ORIGINS="https://127.0.0.1:3000",
            )

    def test_production_rejects_0000(self):
        """Production raises if CORS_ORIGINS contains 0.0.0.0."""
        with pytest.raises(ValidationError, match="Local origin"):
            _make_settings(
                ENVIRONMENT="production",
                CORS_ORIGINS="https://0.0.0.0:8000",
            )

    def test_production_rejects_http(self):
        """Production raises if any origin uses http:// instead of https://."""
        with pytest.raises(ValidationError, match="HTTP origin"):
            _make_settings(
                ENVIRONMENT="production",
                CORS_ORIGINS="http://codeacademypro.com",
            )

    def test_production_accepts_https(self):
        """Production accepts valid HTTPS origins."""
        s = _make_settings(
            ENVIRONMENT="production",
            CORS_ORIGINS="https://codeacademypro.com,https://www.codeacademypro.com",
        )
        assert s.cors_origins_list == [
            "https://codeacademypro.com",
            "https://www.codeacademypro.com",
        ]

    # ── staging: same restrictions as production ─────────────────────────

    def test_staging_rejects_wildcard(self):
        """Staging raises if CORS_ORIGINS contains '*'."""
        with pytest.raises(ValidationError, match="not allowed"):
            _make_settings(ENVIRONMENT="staging", CORS_ORIGINS="*")

    def test_staging_rejects_localhost(self):
        """Staging raises if CORS_ORIGINS contains localhost."""
        with pytest.raises(ValidationError, match="Local origin"):
            _make_settings(
                ENVIRONMENT="staging",
                CORS_ORIGINS="http://localhost:3000",
            )

    def test_staging_rejects_http(self):
        """Staging raises if any origin uses http://."""
        with pytest.raises(ValidationError, match="HTTP origin"):
            _make_settings(
                ENVIRONMENT="staging",
                CORS_ORIGINS="http://staging.codeacademypro.com",
            )

    def test_staging_rejects_empty(self):
        """Staging raises if CORS_ORIGINS is empty."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            _make_settings(ENVIRONMENT="staging", CORS_ORIGINS="")

    # ── origin format validation (all environments) ──────────────────────

    def test_rejects_origin_with_path(self):
        """Any environment rejects origins with a path component."""
        with pytest.raises(ValidationError, match="path"):
            _make_settings(
                ENVIRONMENT="development",
                CORS_ORIGINS="http://localhost:3000/app",
            )

    def test_rejects_origin_with_query(self):
        """Any environment rejects origins with query parameters."""
        with pytest.raises(ValidationError, match="query"):
            _make_settings(
                ENVIRONMENT="development",
                CORS_ORIGINS="http://localhost:3000?x=1",
            )

    def test_rejects_origin_with_fragment(self):
        """Any environment rejects origins with a fragment."""
        with pytest.raises(ValidationError, match="fragment"):
            _make_settings(
                ENVIRONMENT="development",
                CORS_ORIGINS="http://localhost:3000#section",
            )

    def test_rejects_invalid_scheme(self):
        """Any environment rejects origins without http/https scheme."""
        with pytest.raises(ValidationError, match="scheme"):
            _make_settings(
                ENVIRONMENT="development",
                CORS_ORIGINS="ftp://files.example.com",
            )

    # ── parsing robustness ───────────────────────────────────────────────

    def test_deduplicates_origins(self):
        """Duplicate origins are removed preserving order."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="http://localhost:3000,http://localhost:3000",
        )
        assert s.cors_origins_list == ["http://localhost:3000"]

    def test_strips_whitespace(self):
        """Whitespace around origins is stripped."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="  http://localhost:3000 , http://127.0.0.1:3000  ",
        )
        assert s.cors_origins_list == [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    def test_strips_trailing_slash(self):
        """Trailing slashes are normalized away."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="http://localhost:3000/",
        )
        assert s.cors_origins_list == ["http://localhost:3000"]

    def test_ignores_empty_entries(self):
        """Empty entries from extra commas are ignored."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS=",http://localhost:3000,,",
        )
        assert s.cors_origins_list == ["http://localhost:3000"]


# ---------------------------------------------------------------------------
# 2. Settings Properties Tests
# ---------------------------------------------------------------------------

class TestCORSProperties:
    """Verify cors_expose_headers and CORS_MAX_AGE behavior."""

    def test_expose_headers_development(self):
        """Development includes profiling headers."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="http://localhost:3000",
        )
        assert "X-Request-ID" in s.cors_expose_headers
        assert "X-Query-Count" in s.cors_expose_headers
        assert "X-DB-Time-Ms" in s.cors_expose_headers

    def test_expose_headers_production(self):
        """Production only exposes X-Request-ID."""
        s = _make_settings(
            ENVIRONMENT="production",
            CORS_ORIGINS="https://codeacademypro.com",
        )
        assert s.cors_expose_headers == ["X-Request-ID"]

    def test_expose_headers_staging(self):
        """Staging only exposes X-Request-ID."""
        s = _make_settings(
            ENVIRONMENT="staging",
            CORS_ORIGINS="https://staging.codeacademypro.com",
        )
        assert s.cors_expose_headers == ["X-Request-ID"]

    def test_default_max_age(self):
        """Default CORS_MAX_AGE is 600."""
        s = _make_settings(
            ENVIRONMENT="development",
            CORS_ORIGINS="http://localhost:3000",
        )
        assert s.CORS_MAX_AGE == 600


# ---------------------------------------------------------------------------
# 3. Middleware Behavior Tests
# ---------------------------------------------------------------------------

class TestCORSMiddleware:
    """Verify the actual HTTP behavior of CORSMiddleware."""

    # ── Allowed origin ───────────────────────────────────────────────────

    def test_allowed_origin_gets_cors_header(self):
        """Request from allowed origin receives Access-Control-Allow-Origin."""
        app = _make_test_app(["http://localhost:3000"])
        client = TestClient(app)
        resp = client.get("/test", headers={"Origin": "http://localhost:3000"})
        assert resp.status_code == 200
        assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_disallowed_origin_no_cors_header(self):
        """Request from disallowed origin does NOT receive CORS headers."""
        app = _make_test_app(["http://localhost:3000"])
        client = TestClient(app)
        resp = client.get("/test", headers={"Origin": "http://evil.com"})
        assert resp.status_code == 200
        assert "access-control-allow-origin" not in resp.headers

    # ── Preflight (OPTIONS) ──────────────────────────────────────────────

    def test_preflight_allowed_origin(self):
        """Preflight from allowed origin returns CORS approval."""
        app = _make_test_app(["http://localhost:3000"])
        client = TestClient(app)
        resp = client.options(
            "/test",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization, Content-Type",
            },
        )
        assert resp.status_code == 200
        assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"
        assert "POST" in resp.headers["access-control-allow-methods"]
        assert "authorization" in resp.headers["access-control-allow-headers"].lower()
        assert "content-type" in resp.headers["access-control-allow-headers"].lower()

    def test_preflight_disallowed_origin(self):
        """Preflight from disallowed origin does NOT return CORS approval."""
        app = _make_test_app(["http://localhost:3000"])
        client = TestClient(app)
        resp = client.options(
            "/test",
            headers={
                "Origin": "http://evil.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Authorization",
            },
        )
        assert "access-control-allow-origin" not in resp.headers

    # ── expose_headers ───────────────────────────────────────────────────

    def test_x_request_id_exposed(self):
        """X-Request-ID is in Access-Control-Expose-Headers."""
        app = _make_test_app(["http://localhost:3000"], environment="production")
        client = TestClient(app)
        resp = client.get("/test", headers={"Origin": "http://localhost:3000"})
        expose = resp.headers.get("access-control-expose-headers", "")
        assert "X-Request-ID" in expose

    def test_profiling_headers_exposed_in_dev(self):
        """Profiling headers are exposed only in development."""
        app = _make_test_app(["http://localhost:3000"], environment="development")
        client = TestClient(app)
        resp = client.get("/test", headers={"Origin": "http://localhost:3000"})
        expose = resp.headers.get("access-control-expose-headers", "")
        assert "X-Query-Count" in expose
        assert "X-DB-Time-Ms" in expose

    def test_profiling_headers_not_exposed_in_prod(self):
        """Profiling headers are NOT exposed in production."""
        app = _make_test_app(["http://localhost:3000"], environment="production")
        client = TestClient(app)
        resp = client.get("/test", headers={"Origin": "http://localhost:3000"})
        expose = resp.headers.get("access-control-expose-headers", "")
        assert "X-Query-Count" not in expose
        assert "X-DB-Time-Ms" not in expose

    # ── credentials ──────────────────────────────────────────────────────

    def test_credentials_not_allowed(self):
        """access-control-allow-credentials should NOT be 'true'."""
        app = _make_test_app(["http://localhost:3000"])
        client = TestClient(app)
        resp = client.get("/test", headers={"Origin": "http://localhost:3000"})
        # When allow_credentials=False, Starlette does not send the header
        creds = resp.headers.get("access-control-allow-credentials")
        assert creds != "true"
