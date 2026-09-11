"""
CodeAcademy Pro — Input Sanitizer
Sanitization and validation utilities for user inputs.
"""

import re

import bleach

# ── Validation Patterns ──────────────────────────────────────────────────────

PATTERNS = {
    "email": re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$"),
    "username": re.compile(r"^[a-zA-Z0-9_]{3,30}$"),
    "name": re.compile(r"^[a-zA-ZÀ-ÿ\s]{2,120}$"),
    "text_general": re.compile(r"^[^<>]{1,2000}$", re.DOTALL),
    "slug": re.compile(r"^[a-z0-9-]{3,120}$"),
    "uuid": re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"),
    "url": re.compile(r"^https?://[^\s]+$"),
    "allowed_file": re.compile(r"^.*\.(jpg|jpeg|png|webp|pdf)$", re.IGNORECASE),
}

# ── Attack Detection Patterns ────────────────────────────────────────────────

ATTACK_PATTERNS = {
    "sql_injection": re.compile(
        r"(\b)(SELECT|INSERT|DELETE|DROP|UPDATE|UNION|ALTER)(\b)", re.IGNORECASE
    ),
    "script_tag": re.compile(r"<script.*?>", re.IGNORECASE),
    "sql_comment": re.compile(r"(--|#|/\*)"),
    "or_1_equal_1": re.compile(r"(\bor\b|\band\b).*=.*", re.IGNORECASE),
    "dangerous_chars": re.compile(r"[<>{};]"),
}

# ── Sanitization Functions ───────────────────────────────────────────────────


def sanitize_text(text: str) -> str:
    """Remove all HTML tags, keep only plain text."""
    if not text:
        return text
    return bleach.clean(text, tags=[], strip=True).strip()


def sanitize_html(text: str) -> str:
    """Allow safe HTML tags for rich text content."""
    allowed_tags = ["p", "br", "strong", "em", "b", "i", "ul", "ol", "li", "a", "code", "pre"]
    allowed_attrs = {"a": ["href", "title"]}
    return bleach.clean(
        text, tags=allowed_tags, attributes=allowed_attrs, strip=True
    ).strip()


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename, removing dangerous characters."""
    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "").replace("..", "")
    # Keep only safe characters
    filename = re.sub(r"[^\w\s\-.]", "", filename)
    return filename.strip()


# ── Validation Functions ─────────────────────────────────────────────────────


def is_valid(pattern_name: str, value: str) -> bool:
    """Check if a value matches a named validation pattern."""
    pattern = PATTERNS.get(pattern_name)
    if not pattern:
        raise ValueError(f"Unknown pattern: {pattern_name}")
    return bool(pattern.match(value))


def detect_attack(text: str) -> str | None:
    """
    Check text for common attack patterns.
    Returns the attack type if detected, None if clean.
    """
    for attack_type, pattern in ATTACK_PATTERNS.items():
        if pattern.search(text):
            return attack_type
    return None


def validate_max_length(text: str, max_length: int = 2000) -> str:
    """Enforce maximum length on text input."""
    if len(text) > max_length:
        return text[:max_length]
    return text


def generate_slug(text: str) -> str:
    """Generate a URL-safe slug from text."""
    slug = text.lower().strip()
    slug = re.sub(r"[àáâãäå]", "a", slug)
    slug = re.sub(r"[èéêë]", "e", slug)
    slug = re.sub(r"[ìíîï]", "i", slug)
    slug = re.sub(r"[òóôõö]", "o", slug)
    slug = re.sub(r"[ùúûü]", "u", slug)
    slug = re.sub(r"[ñ]", "n", slug)
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug[:120].strip("-")
