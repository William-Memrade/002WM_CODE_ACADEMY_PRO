"""
CodeAcademy Pro — Notifications Router
In-app notifications for the current user.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.rls import get_rls_db
from app.middlewares.auth import get_current_user
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _notification_to_dict(n) -> dict:
    return {
        "id": str(n.id),
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "reference_type": n.reference_type,
        "reference_id": str(n.reference_id) if n.reference_id else None,
        "is_read": n.is_read,
        "read_at": n.read_at.isoformat() if n.read_at else None,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


@router.get("")
async def list_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """List notifications for the authenticated user."""
    svc = NotificationService(db)
    notifications = await svc.list_notifications(
        current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [_notification_to_dict(n) for n in notifications],
        "count": len(notifications),
    }


@router.get("/unread-count")
async def unread_count(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """Return the number of unread notifications."""
    svc = NotificationService(db)
    count = await svc.get_unread_count(current_user.id)
    return {"unread_count": count}


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """Mark a single notification as read."""
    svc = NotificationService(db)
    notification = await svc.mark_read(notification_id, current_user.id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    await db.commit()
    return _notification_to_dict(notification)


@router.patch("/mark-all-read")
async def mark_all_read(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """Mark all notifications for the user as read."""
    svc = NotificationService(db)
    updated = await svc.mark_all_read(current_user.id)
    await db.commit()
    return {"updated": updated}
