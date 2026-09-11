"""
CodeAcademy Pro — Backend Configuration
Centralized configuration using Pydantic Settings.
All values loaded from environment variables.
"""

import logging
from functools import lru_cache
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── App ──────────────────────────────────────────────────────────────
    APP_NAME: str = "CodeAcademy Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # ── JWT ──────────────────────────────────────────────────────────────
    JWT_SECRET: str = Field(..., description="Secret key for JWT signing")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string (superuser, for migrations)")
    DATABASE_RLS_URL: str = Field(
        default="",
        description="PostgreSQL connection string for RLS-enforced app role. Falls back to DATABASE_URL if empty.",
    )
    DB_POOL_SIZE: int = 5  # Increase to 15-20 in production via env var
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_TIMEOUT: int = 30

    # ── Supabase ─────────────────────────────────────────────────────────
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # ── Redis ────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Storage (S3-compatible) ──────────────────────────────────────────
    STORAGE_BUCKET: str = "academy-storage"
    STORAGE_SECRET: str = ""
    STORAGE_REGION: str = "us-east-1"
    STORAGE_ENDPOINT: str = ""  # For S3-compatible providers

    # ── Email (SMTP) ─────────────────────────────────────────────────────
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025  # Mailhog default
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@codeacademypro.com"
    SMTP_FROM_NAME: str = "CodeAcademy Pro"
    SMTP_USE_TLS: bool = False

    # ── Security ─────────────────────────────────────────────────────────
    MASTER_SERVICE_SECRET: str = ""  # For inter-service HMAC signing
    RATE_LIMIT_PER_MINUTE: int = 100
    MAX_UPLOAD_MB: int = 10
    MAX_VIDEO_UPLOAD_MB: int = 500
    CORS_ORIGINS: str = "http://localhost:3000"  # Comma-separated
    CORS_MAX_AGE: int = 600  # Preflight cache in seconds (600=dev, 3600=staging, 86400=prod)
    SECURITY_HEADERS_ENABLED: bool = True  # Master switch for security headers middleware
    HSTS_ENABLED: bool = False  # Only enable behind real HTTPS termination
    HSTS_MAX_AGE: int = 31536000  # 1 year in seconds (31536000)
    HSTS_INCLUDE_SUBDOMAINS: bool = True  # Add includeSubDomains to HSTS
    HSTS_PRELOAD: bool = False  # Add preload to HSTS (requires hstspreload.org validation)
    CSP_REPORT_ONLY: bool = False  # Use Report-Only CSP header instead of enforcing
    CSP_REPORT_URI: str = ""  # URI for CSP violation reports (e.g., Sentry)

    # ── reCAPTCHA (bot protection) ─────────────────────────────────────────
    RECAPTCHA_ENABLED: bool = False  # Master switch; when False, captcha is bypassed in dev
    RECAPTCHA_SECRET_KEY: str = ""  # Server-side secret (Google reCAPTCHA v2)
    RECAPTCHA_MIN_SCORE: float = 0.5  # Minimum score for v3 (reserved)

    # ── Observability ────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""  # Optional Sentry integration

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Parse CORS_ORIGINS into a deduplicated, normalized list.

        Processing steps:
        1. Split by comma and strip whitespace
        2. Remove trailing slashes (CORS origins must not have paths)
        3. Deduplicate preserving insertion order
        4. Filter out empty strings
        """
        raw = self.CORS_ORIGINS.split(",")
        seen: set[str] = set()
        result: list[str] = []
        for item in raw:
            origin = item.strip().rstrip("/")
            if not origin or origin in seen:
                continue
            seen.add(origin)
            result.append(origin)
        return result

    @property
    def cors_expose_headers(self) -> list[str]:
        """Response headers the browser is allowed to read via JavaScript."""
        headers = ["X-Request-ID"]
        if self.ENVIRONMENT == "development":
            headers += ["X-Query-Count", "X-DB-Time-Ms"]
        return headers

    @model_validator(mode="after")
    def validate_cors_security(self) -> "Settings":
        """
        Fail-fast CORS validation at startup.

        Rules enforced per origin:
        - Must have http:// or https:// scheme
        - Must have a hostname
        - Must not contain paths, query strings, or fragments
        - staging/production: no wildcard, no localhost/127.0.0.1/0.0.0.0, HTTPS only
        - development: warn if empty
        """
        _logger = logging.getLogger("app.core.config")
        origins = self.cors_origins_list
        env = self.ENVIRONMENT

        # ── Empty check ──────────────────────────────────────────────
        if not origins:
            if env in ("production", "staging"):
                raise ValueError(
                    f"CORS_ORIGINS cannot be empty in {env}. "
                    "Specify at least one allowed origin."
                )
            _logger.warning(
                "CORS_ORIGINS is empty — no cross-origin requests will "
                "be allowed. Set CORS_ORIGINS in your .env file."
            )
            return self

        # ── Per-origin validation ────────────────────────────────────
        for origin in origins:
            # Wildcard
            if origin == "*":
                if env in ("production", "staging"):
                    raise ValueError(
                        f"CORS_ORIGINS='*' is not allowed in {env}. "
                        "Specify explicit origins."
                    )
                continue  # valid in development

            parsed = urlparse(origin)

            # Scheme
            if parsed.scheme not in ("http", "https"):
                raise ValueError(
                    f"Invalid CORS origin '{origin}' — "
                    "scheme must be http or https."
                )

            # Host
            if not parsed.netloc:
                raise ValueError(
                    f"Invalid CORS origin '{origin}' — missing hostname."
                )

            # No path / query / fragment
            if parsed.path not in ("", "/"):
                raise ValueError(
                    f"CORS origin must not include a path: '{origin}'. "
                    "Use only scheme://host[:port]."
                )
            if parsed.query:
                raise ValueError(
                    f"CORS origin must not include query params: '{origin}'."
                )
            if parsed.fragment:
                raise ValueError(
                    f"CORS origin must not include a fragment: '{origin}'."
                )

            # ── staging / production restrictions ────────────────────
            hostname = parsed.hostname or ""

            if env in ("production", "staging"):
                if hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
                    raise ValueError(
                        f"Local origin '{origin}' is not allowed in "
                        f"{env}. Use a real domain with HTTPS."
                    )
                if parsed.scheme != "https":
                    raise ValueError(
                        f"HTTP origin '{origin}' is not allowed in "
                        f"{env}. All origins must use HTTPS."
                    )

        return self

    @model_validator(mode="after")
    def validate_hsts_security(self) -> "Settings":
        """
        Prevent HSTS from being enabled in development.
        Prevent preload without includeSubDomains (HSTS spec requirement).
        """
        if self.HSTS_ENABLED and self.ENVIRONMENT == "development":
            raise ValueError(
                "HSTS_ENABLED must not be True in development. "
                "HSTS forces HTTPS, which breaks local HTTP development."
            )
        if self.HSTS_PRELOAD and not self.HSTS_INCLUDE_SUBDOMAINS:
            raise ValueError(
                "HSTS_PRELOAD requires HSTS_INCLUDE_SUBDOMAINS=True. "
                "The preload list specification mandates includeSubDomains."
            )
        return self

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_MB * 1024 * 1024

    @property
    def max_video_upload_bytes(self) -> int:
        return self.MAX_VIDEO_UPLOAD_MB * 1024 * 1024

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance (singleton)."""
    return Settings()
