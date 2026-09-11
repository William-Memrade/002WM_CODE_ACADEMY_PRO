"""
CodeAcademy Pro — Captcha Service
Verifies Google reCAPTCHA tokens against Google's siteverify endpoint.

When RECAPTCHA_ENABLED is False (development), verification is bypassed so the
flow can be exercised locally without keys. In staging/production, set
RECAPTCHA_ENABLED=true and RECAPTCHA_SECRET_KEY to enforce it.
"""

import httpx
import structlog

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify_captcha(token: str | None) -> bool:
    """
    Verify a Google reCAPTCHA token.

    Args:
        token: The reCAPTCHA response token returned by the client widget.

    Returns:
        True if the token is valid (or captcha is disabled), False otherwise.
    """
    if not settings.RECAPTCHA_ENABLED:
        # Dev mode: bypass captcha entirely.
        return True

    if not token:
        return False

    if not settings.RECAPTCHA_SECRET_KEY:
        logger.warning("captcha_enabled_but_no_secret_key")
        return False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                RECAPTCHA_VERIFY_URL,
                data={
                    "secret": settings.RECAPTCHA_SECRET_KEY,
                    "response": token,
                },
            )
        data = response.json()
    except Exception as exc:
        logger.error("captcha_verify_error", error=str(exc))
        return False

    success = bool(data.get("success"))
    if not success:
        logger.warning(
            "captcha_verify_failed",
            error_codes=data.get("error-codes", []),
        )
    return success