"""
CodeAcademy Pro — Security Headers Tests
Validates SecurityHeadersASGI + SecurityHeadersMiddleware behavior
and Settings HSTS validation.

Run with:
    pytest tests/test_security_headers.py -v
"""

import os
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.middlewares.security_headers import (
    SecurityHeadersASGI,
    SecurityHeadersMiddleware,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_BASE_ENV = {
    "JWT_SECRET": "test-secret-key",
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost:5432/test_db",
}


def _make_settings(**overrides):
    from app.core.config import Settings

    env = {**_BASE_ENV, **overrides}
    with patch.dict(os.environ, env, clear=False):
        return Settings(**env)


def _make_app(*, asgi_kwargs=None, middleware_kwargs=None):
    """
    Build a minimal FastAPI app with both security header layers.

    asgi_kwargs: passed to SecurityHeadersASGI (universal headers).
    middleware_kwargs: passed to SecurityHeadersMiddleware (path logic).
    """
    inner_app = FastAPI()

    mw_kw = middleware_kwargs or {}
    inner_app.add_middleware(SecurityHeadersMiddleware, **mw_kw)

    @inner_app.get("/test")
    async def _test():
        return {"ok": True}

    @inner_app.get("/api/v1/auth/login")
    async def _login():
        return {"token": "xxx"}

    @inner_app.get("/api/v1/payments/list")
    async def _payments():
        return {"items": []}

    @inner_app.get("/api/v1/users/me")
    async def _me():
        return {"id": "1"}

    @inner_app.get("/api/v1/audit/log")
    async def _audit():
        return {"entries": []}

    @inner_app.get("/api/v1/admin/settings")
    async def _admin():
        return {"settings": {}}

    @inner_app.get("/health")
    async def _health():
        return {"status": "ok"}

    @inner_app.get("/api/v1/courses")
    async def _courses():
        return {"items": []}

    @inner_app.get("/boom")
    async def _boom():
        raise RuntimeError("unhandled server error")

    asgi_kw = asgi_kwargs or {}
    wrapped = SecurityHeadersASGI(inner_app, **asgi_kw)
    return wrapped


# ---------------------------------------------------------------------------
# 1. Settings Validation Tests
# ---------------------------------------------------------------------------

class TestSettingsValidation:
    """Verify HSTS fail-fast validation in Settings."""

    def test_hsts_blocked_in_development(self):
        with pytest.raises(ValidationError, match="HSTS"):
            _make_settings(ENVIRONMENT="development", HSTS_ENABLED="true")

    def test_hsts_allowed_in_staging(self):
        s = _make_settings(
            ENVIRONMENT="staging",
            HSTS_ENABLED="true",
            CORS_ORIGINS="https://staging.example.com",
        )
        assert s.HSTS_ENABLED is True

    def test_hsts_allowed_in_production(self):
        s = _make_settings(
            ENVIRONMENT="production",
            HSTS_ENABLED="true",
            CORS_ORIGINS="https://example.com",
        )
        assert s.HSTS_ENABLED is True

    def test_hsts_disabled_by_default(self):
        s = _make_settings(ENVIRONMENT="development", CORS_ORIGINS="http://localhost:3000")
        assert s.HSTS_ENABLED is False

    def test_preload_requires_include_subdomains(self):
        with pytest.raises(ValidationError, match="HSTS_PRELOAD"):
            _make_settings(
                ENVIRONMENT="production",
                HSTS_ENABLED="true",
                HSTS_PRELOAD="true",
                HSTS_INCLUDE_SUBDOMAINS="false",
                CORS_ORIGINS="https://example.com",
            )

    def test_preload_allowed_with_include_subdomains(self):
        s = _make_settings(
            ENVIRONMENT="production",
            HSTS_ENABLED="true",
            HSTS_PRELOAD="true",
            HSTS_INCLUDE_SUBDOMAINS="true",
            CORS_ORIGINS="https://example.com",
        )
        assert s.HSTS_PRELOAD is True

    def test_security_headers_enabled_by_default(self):
        s = _make_settings(ENVIRONMENT="development", CORS_ORIGINS="http://localhost:3000")
        assert s.SECURITY_HEADERS_ENABLED is True


# ---------------------------------------------------------------------------
# 2. Fixed Headers Tests (via ASGI wrapper)
# ---------------------------------------------------------------------------

class TestFixedHeaders:
    """Verify headers that are always present regardless of environment."""

    @pytest.fixture()
    def client(self):
        return TestClient(_make_app(), raise_server_exceptions=False)

    def test_x_content_type_options(self, client):
        r = client.get("/test")
        assert r.headers["x-content-type-options"] == "nosniff"

    def test_x_frame_options(self, client):
        r = client.get("/test")
        assert r.headers["x-frame-options"] == "DENY"

    def test_referrer_policy(self, client):
        r = client.get("/test")
        assert r.headers["referrer-policy"] == "strict-origin-when-cross-origin"

    def test_permissions_policy(self, client):
        r = client.get("/test")
        pp = r.headers["permissions-policy"]
        assert "camera=()" in pp
        assert "microphone=()" in pp
        assert "geolocation=()" in pp
        assert "payment=()" in pp

    def test_no_coop_header(self, client):
        """COOP is NOT included in this phase per design."""
        r = client.get("/test")
        assert "cross-origin-opener-policy" not in r.headers

    def test_no_corp_header(self, client):
        """CORP is NOT included in this phase per design."""
        r = client.get("/test")
        assert "cross-origin-resource-policy" not in r.headers

    def test_no_coep_header(self, client):
        """COEP is NOT included per design."""
        r = client.get("/test")
        assert "cross-origin-embedder-policy" not in r.headers


# ---------------------------------------------------------------------------
# 3. Enabled/Disabled Toggle
# ---------------------------------------------------------------------------

class TestEnabledToggle:
    """Verify SECURITY_HEADERS_ENABLED master switch."""

    def test_headers_present_when_enabled(self):
        client = TestClient(_make_app(asgi_kwargs={"enabled": True}))
        r = client.get("/test")
        assert "x-content-type-options" in r.headers
        assert "x-frame-options" in r.headers
        assert "content-security-policy" in r.headers

    def test_headers_absent_when_disabled(self):
        client = TestClient(
            _make_app(
                asgi_kwargs={"enabled": False},
                middleware_kwargs={"enabled": False},
            )
        )
        r = client.get("/test")
        assert "x-content-type-options" not in r.headers
        assert "x-frame-options" not in r.headers
        assert "content-security-policy" not in r.headers


# ---------------------------------------------------------------------------
# 4. CSP Tests
# ---------------------------------------------------------------------------

class TestCSP:
    """Verify Content-Security-Policy varies by environment."""

    def test_csp_dev_permissive(self):
        client = TestClient(_make_app(asgi_kwargs={"debug": True}))
        r = client.get("/test")
        csp = r.headers["content-security-policy"]
        assert "default-src 'self'" in csp
        assert "'unsafe-inline'" in csp
        assert "frame-ancestors 'none'" in csp
        assert "base-uri 'self'" in csp
        assert "form-action 'self'" in csp

    def test_csp_dev_allows_swagger_cdn(self):
        """FastAPI serves Swagger from cdn.jsdelivr.net — CSP must allow it."""
        client = TestClient(_make_app(asgi_kwargs={"debug": True}))
        r = client.get("/test")
        csp = r.headers["content-security-policy"]
        assert "cdn.jsdelivr.net" in csp

    def test_csp_dev_allows_swagger_favicon(self):
        """FastAPI Swagger favicon comes from fastapi.tiangolo.com."""
        client = TestClient(_make_app(asgi_kwargs={"debug": True}))
        r = client.get("/test")
        csp = r.headers["content-security-policy"]
        assert "fastapi.tiangolo.com" in csp

    def test_csp_prod_strict(self):
        client = TestClient(_make_app(asgi_kwargs={"debug": False}))
        r = client.get("/test")
        csp = r.headers["content-security-policy"]
        assert "default-src 'none'" in csp
        assert "'unsafe-inline'" not in csp
        assert "frame-ancestors 'none'" in csp
        assert "base-uri 'none'" in csp
        assert "form-action 'none'" in csp

    def test_csp_prod_no_localhost(self):
        client = TestClient(_make_app(asgi_kwargs={"debug": False}))
        r = client.get("/test")
        assert "localhost" not in r.headers["content-security-policy"]

    def test_csp_prod_no_wildcard(self):
        client = TestClient(_make_app(asgi_kwargs={"debug": False}))
        r = client.get("/test")
        csp = r.headers["content-security-policy"]
        assert " * " not in f" {csp} "
        assert "'*'" not in csp

    def test_csp_report_only_header_name(self):
        client = TestClient(_make_app(asgi_kwargs={"csp_report_only": True}))
        r = client.get("/test")
        assert "content-security-policy-report-only" in r.headers
        assert "content-security-policy" not in r.headers

    def test_csp_enforcing_header_name(self):
        client = TestClient(_make_app(asgi_kwargs={"csp_report_only": False}))
        r = client.get("/test")
        assert "content-security-policy" in r.headers

    def test_csp_report_uri_included(self):
        uri = "https://sentry.io/api/123/csp-report/"
        client = TestClient(_make_app(asgi_kwargs={"csp_report_uri": uri}))
        r = client.get("/test")
        csp = r.headers["content-security-policy"]
        assert f"report-uri {uri}" in csp

    def test_csp_no_report_uri_when_empty(self):
        client = TestClient(_make_app(asgi_kwargs={"csp_report_uri": ""}))
        r = client.get("/test")
        assert "report-uri" not in r.headers["content-security-policy"]


# ---------------------------------------------------------------------------
# 5. HSTS Tests
# ---------------------------------------------------------------------------

class TestHSTS:
    """Verify Strict-Transport-Security behavior."""

    def test_hsts_present_when_enabled(self):
        client = TestClient(_make_app(asgi_kwargs={"hsts_enabled": True}))
        r = client.get("/test")
        assert "strict-transport-security" in r.headers

    def test_hsts_absent_when_disabled(self):
        client = TestClient(_make_app(asgi_kwargs={"hsts_enabled": False}))
        r = client.get("/test")
        assert "strict-transport-security" not in r.headers

    def test_hsts_default_max_age(self):
        client = TestClient(_make_app(asgi_kwargs={"hsts_enabled": True}))
        r = client.get("/test")
        assert "max-age=31536000" in r.headers["strict-transport-security"]

    def test_hsts_custom_max_age(self):
        client = TestClient(_make_app(asgi_kwargs={"hsts_enabled": True, "hsts_max_age": 86400}))
        r = client.get("/test")
        assert "max-age=86400" in r.headers["strict-transport-security"]

    def test_hsts_include_subdomains(self):
        client = TestClient(_make_app(asgi_kwargs={"hsts_enabled": True, "hsts_include_subdomains": True}))
        r = client.get("/test")
        assert "includeSubDomains" in r.headers["strict-transport-security"]

    def test_hsts_no_include_subdomains(self):
        client = TestClient(_make_app(asgi_kwargs={"hsts_enabled": True, "hsts_include_subdomains": False}))
        r = client.get("/test")
        assert "includeSubDomains" not in r.headers["strict-transport-security"]

    def test_hsts_preload(self):
        client = TestClient(_make_app(asgi_kwargs={"hsts_enabled": True, "hsts_preload": True}))
        r = client.get("/test")
        assert "preload" in r.headers["strict-transport-security"]

    def test_hsts_no_preload_by_default(self):
        client = TestClient(_make_app(asgi_kwargs={"hsts_enabled": True}))
        r = client.get("/test")
        assert "preload" not in r.headers["strict-transport-security"]


# ---------------------------------------------------------------------------
# 6. Cache-Control Tests (via BaseHTTPMiddleware)
# ---------------------------------------------------------------------------

class TestCacheControl:
    """Verify Cache-Control: no-store + Pragma + Expires on sensitive endpoints."""

    @pytest.fixture()
    def client(self):
        return TestClient(_make_app())

    def test_auth_endpoint_no_store(self, client):
        r = client.get("/api/v1/auth/login")
        assert r.headers["cache-control"] == "no-store"
        assert r.headers["pragma"] == "no-cache"
        assert r.headers["expires"] == "0"

    def test_payments_endpoint_no_store(self, client):
        r = client.get("/api/v1/payments/list")
        assert r.headers["cache-control"] == "no-store"

    def test_users_endpoint_no_store(self, client):
        r = client.get("/api/v1/users/me")
        assert r.headers["cache-control"] == "no-store"

    def test_audit_endpoint_no_store(self, client):
        r = client.get("/api/v1/audit/log")
        assert r.headers["cache-control"] == "no-store"

    def test_admin_endpoint_no_store(self, client):
        r = client.get("/api/v1/admin/settings")
        assert r.headers["cache-control"] == "no-store"

    def test_health_no_cache_control(self, client):
        r = client.get("/health")
        assert "cache-control" not in r.headers

    def test_public_endpoint_no_cache_control(self, client):
        r = client.get("/test")
        assert "cache-control" not in r.headers

    def test_courses_catalog_no_cache_control(self, client):
        r = client.get("/api/v1/courses")
        assert "cache-control" not in r.headers


# ---------------------------------------------------------------------------
# 7. Error Response Coverage (critical: 500, 404, 405)
# ---------------------------------------------------------------------------

class TestErrorCoverage:
    """Verify security headers appear on ALL error responses."""

    @pytest.fixture()
    def client(self):
        return TestClient(_make_app(), raise_server_exceptions=False)

    def test_404_has_security_headers(self, client):
        r = client.get("/nonexistent-path")
        assert r.status_code == 404
        assert r.headers["x-content-type-options"] == "nosniff"
        assert r.headers["x-frame-options"] == "DENY"
        assert "content-security-policy" in r.headers

    def test_405_has_security_headers(self, client):
        r = client.delete("/test")
        assert r.status_code == 405
        assert r.headers["x-content-type-options"] == "nosniff"
        assert "content-security-policy" in r.headers

    def test_500_has_security_headers(self, client):
        """
        Critical test: unhandled exceptions generate responses via
        Starlette's ServerErrorMiddleware, which is OUTSIDE normal
        middleware stack. The ASGI wrapper ensures coverage.
        """
        r = client.get("/boom")
        assert r.status_code == 500
        assert r.headers["x-content-type-options"] == "nosniff"
        assert r.headers["x-frame-options"] == "DENY"
        assert "content-security-policy" in r.headers
