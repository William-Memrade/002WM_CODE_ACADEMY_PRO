"""Notifications router."""
from fastapi import APIRouter, Depends
from app.middlewares.auth import get_current_user
from app.db.rls import get_rls_db

router = APIRouter()

@router.get("/")
async def list_notifications(current_user=Depends(get_current_user)):
    """Get user notifications."""
    return {"items": []}

@router.patch("/{notification_id}/read")
async def mark_read(notification_id: str, current_user=Depends(get_current_user)):
    """Mark notification as read."""
    return {}

@router.patch("/read-all")
async def mark_all_read(current_user=Depends(get_current_user)):
    """Mark all notifications as read."""
    return {}

@router.get("/unread-count")
async def unread_count(current_user=Depends(get_current_user)):
    """Get unread notification count."""
    return {"count": 0}
