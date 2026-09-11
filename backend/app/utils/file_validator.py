"""
CodeAcademy Pro — File Validator
Validates uploaded files: MIME type, extension, size.
"""

import magic
from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings

settings = get_settings()

# ── Allowed Types ────────────────────────────────────────────────────────────

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
ALLOWED_DOCUMENT_EXTENSIONS = {"pdf"}
ALLOWED_VIDEO_EXTENSIONS = {"mp4", "webm"}

ALLOWED_IMAGE_MIMES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_DOCUMENT_MIMES = {"application/pdf"}
ALLOWED_VIDEO_MIMES = {"video/mp4", "video/webm"}

# All allowed for general uploads (payment proofs, avatars)
ALLOWED_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS
ALLOWED_MIMES = ALLOWED_IMAGE_MIMES | ALLOWED_DOCUMENT_MIMES

# All allowed including video (for recorded classes)
ALL_EXTENSIONS = ALLOWED_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS
ALL_MIMES = ALLOWED_MIMES | ALLOWED_VIDEO_MIMES

# ── Rejected Types ───────────────────────────────────────────────────────────

REJECTED_EXTENSIONS = {
    "exe", "sh", "bat", "cmd", "js", "php", "py", "rb", "pl",
    "zip", "tar", "gz", "rar", "7z", "msi", "dll", "so",
    "com", "vbs", "ps1", "jar", "war", "class",
}


async def validate_file(
    file: UploadFile,
    allowed_extensions: set[str] | None = None,
    allowed_mimes: set[str] | None = None,
    max_size_bytes: int | None = None,
) -> bool:
    """
    Validate an uploaded file.

    Args:
        file: The uploaded file
        allowed_extensions: Set of allowed extensions (default: images + pdf)
        allowed_mimes: Set of allowed MIME types (default: images + pdf)
        max_size_bytes: Maximum file size in bytes (default: from settings)

    Returns:
        True if valid

    Raises:
        HTTPException: If file is invalid
    """
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_EXTENSIONS
    if allowed_mimes is None:
        allowed_mimes = ALLOWED_MIMES
    if max_size_bytes is None:
        max_size_bytes = settings.max_upload_bytes

    # 1. Check filename exists
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename",
        )

    # 2. Check extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

    if ext in REJECTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{ext} is not allowed (security risk)",
        )

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension .{ext} is not allowed. Allowed: {', '.join(sorted(allowed_extensions))}",
        )

    # 3. Check real MIME type (magic bytes)
    content = await file.read(8192)
    await file.seek(0)

    real_mime = magic.from_buffer(content, mime=True)

    if real_mime not in allowed_mimes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File content type {real_mime} does not match allowed types",
        )

    # 4. Check file size
    if file.size and file.size > max_size_bytes:
        max_mb = max_size_bytes / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {max_mb:.0f}MB",
        )

    return True


async def validate_payment_proof(file: UploadFile) -> bool:
    """Validate a payment proof file (images + pdf, max 10MB)."""
    return await validate_file(
        file,
        allowed_extensions=ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS,
        allowed_mimes=ALLOWED_IMAGE_MIMES | ALLOWED_DOCUMENT_MIMES,
        max_size_bytes=settings.max_upload_bytes,
    )


async def validate_video(file: UploadFile) -> bool:
    """Validate a video file (mp4/webm, max 500MB)."""
    return await validate_file(
        file,
        allowed_extensions=ALLOWED_VIDEO_EXTENSIONS,
        allowed_mimes=ALLOWED_VIDEO_MIMES,
        max_size_bytes=settings.max_video_upload_bytes,
    )


async def validate_avatar(file: UploadFile) -> bool:
    """Validate an avatar image (images only, max 5MB)."""
    return await validate_file(
        file,
        allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
        allowed_mimes=ALLOWED_IMAGE_MIMES,
        max_size_bytes=5 * 1024 * 1024,
    )
