"""
CodeAcademy Pro — Security Headers Middleware
Injects HTTP security headers into every response.
Headers are environment-aware: development is permissive (Swagger),
staging/production are strict.

Architecture:
    Two layers work together to ensure complete coverage:

    1. SecurityHeadersASGI (pure ASGI wrapper)
       → Wraps the ENTIRE application including Starlette's ServerErrorMiddleware.
       → Injects headers at the ASGI protocol level into every response,
         including unhandled 500 errors that bypass BaseHTTPMiddleware.

    2. SecurityHeadersMiddleware (BaseHTTPMiddleware)
       → Handles request-path-dependent logic (Cache-Control, Server removal)
         that requires access to the Request object.
       → Only covers responses that pass through the normal middleware stack
         (200, 404, 405, HTTPException, etc. — NOT unhandled 500s).

NOTE: This middleware does NOT replace authentication, CORS, RBAC, or RLS.
Security headers instruct the browser how to treat responses — they are a
defense-in-depth layer, not a primary access control mechanism.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

# Paths whose responses must never be cached by shared proxies or browsers.
_SENSITIVE_PATH_PREFIXES = (
    "/api/v1/auth/",
    "/api/v1/users/",
    "/api/v1/payments/",
    "/api/v1/audit/",
    "/api/v1/admin/",
)


def build_csp(*, debug: bool, report_uri: str) -> str:
    """
    Build the Content-Security-Policy directive string.

    Development (debug=True):
        Permissive policy that allows Swagger UI and ReDoc to function.
        FastAPI serves Swagger UI from cdn.jsdelivr.net (JS + CSS) and
        loads a favicon from fastapi.tiangolo.com. Both Swagger and ReDoc
        inject inline styles, so 'unsafe-inline' is required in style-src.
        Swagger UI also needs 'unsafe-inline' in script-src for its
        initialization script.

    Staging / Production (debug=False):
        Strict policy for an API that only serves JSON. No scripts, styles,
        images, or fonts should ever be loaded by the browser from an API
        response, so default-src 'none' blocks everything.
    """
    if debug:
        directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
            "img-src 'self' data: https://fastapi.tiangolo.com",
            "font-src 'self' https://fonts.gstatic.com",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
    else:
        directives = [
            "default-src 'none'",
            "frame-ancestors 'none'",
            "base-uri 'none'",
            "form-action 'none'",
        ]

    if report_uri:
        directives.append(f"report-uri {report_uri}")

    return "; ".join(directives)


class SecurityHeadersASGI:
    """
    Pure ASGI wrapper that injects security headers into EVERY HTTP response.

    This wraps the entire FastAPI application (including Starlette's
    ServerErrorMiddleware) so that even unhandled 500 errors carry
    security headers. It operates at the ASGI protocol level by
    intercepting ``http.response.start`` messages.

    Usage in main.py::

        app.wsgi_app = SecurityHeadersASGI(app, ...)
        # or: application = SecurityHeadersASGI(app, ...)

    Headers injected unconditionally:
        - X-Content-Type-Options: nosniff
        - X-Frame-Options: DENY
        - Referrer-Policy: strict-origin-when-cross-origin
        - Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
        - Content-Security-Policy (or Report-Only variant)
        - Strict-Transport-Security (when HSTS enabled)
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        enabled: bool = True,
        debug: bool = False,
        hsts_enabled: bool = False,
        hsts_max_age: int = 31536000,
        hsts_include_subdomains: bool = True,
        hsts_preload: bool = False,
        csp_report_only: bool = False,
        csp_report_uri: str = "",
    ):
        self.app = app
        self._enabled = enabled

        # Pre-compute all header bytes at startup (zero per-request cost)
        csp_value = build_csp(debug=debug, report_uri=csp_report_uri)
        csp_header_name = (
            "content-security-policy-report-only"
            if csp_report_only
            else "content-security-policy"
        )

        self._headers: list[tuple[bytes, bytes]] = [
            (b"x-content-type-options", b"nosniff"),
            (b"x-frame-options", b"DENY"),
            (b"referrer-policy", b"strict-origin-when-cross-origin"),
            (b"permissions-policy", b"camera=(), microphone=(), geolocation=(), payment=()"),
            (csp_header_name.encode(), csp_value.encode()),
        ]

        if hsts_enabled:
            hsts_value = f"max-age={hsts_max_age}"
            if hsts_include_subdomains:
                hsts_value += "; includeSubDomains"
            if hsts_preload:
                # NOTE: preload requires domain validation at https://hstspreload.org
                # and should only be enabled after verifying all subdomains support HTTPS.
                hsts_value += "; preload"
            self._headers.append((b"strict-transport-security", hsts_value.encode()))

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not self._enabled:
            await self.app(scope, receive, send)
            return

        headers_to_add = self._headers

        async def inject_headers(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                existing_names = {h[0].lower() for h in headers}
                for name, value in headers_to_add:
                    if name not in existing_names:
                        headers.append((name, value))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, inject_headers)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Request-aware security headers logic (Cache-Control, Server removal).

    This middleware handles logic that requires access to the request path.
    It runs INSIDE the normal middleware stack, so it does NOT cover
    unhandled 500 errors. The SecurityHeadersASGI wrapper above handles
    the universal headers for those cases.

    Middleware execution order (Starlette: last registered = outermost):
        SecurityHeaders → CorrelationID → CORS → QueryProfiling → GZip → Handler
    """

    def __init__(
        self,
        app: ASGIApp,
        *,
        enabled: bool = True,
        environment: str = "development",
    ):
        super().__init__(app)
        self._enabled = enabled
        self._env = environment

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        if not self._enabled:
            return response

        # ── Server header removal (staging/production) ───────────────
        # Best-effort: Uvicorn or a reverse proxy may re-add this header
        # after the middleware runs. Complete removal may require proxy
        # configuration (e.g., Nginx: server_tokens off; proxy_hide_header Server;).
        if self._env != "development":
            if "server" in response.headers:
                del response.headers["server"]

        # ── Cache-Control for sensitive endpoints ────────────────────
        path = request.url.path
        if any(path.startswith(p) for p in _SENSITIVE_PATH_PREFIXES):
            if "cache-control" not in response.headers:
                response.headers["Cache-Control"] = "no-store"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"

        return response
