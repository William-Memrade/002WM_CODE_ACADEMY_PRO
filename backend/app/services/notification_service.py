"""
CodeAcademy Pro — Notification Service
In-app notifications + email enqueueing for admins.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func as sa_func, select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.user import User, UserRole, Role


class NotificationService:
    """Business logic for user notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        type: str,
        reference_type: str | None = None,
        reference_id: UUID | None = None,
    ) -> Notification:
        """Create a single in-app notification."""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type,
            reference_type=reference_type,
            reference_id=reference_id,
            is_read=False,
            read_at=None,
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def list_notifications(
        self,
        user_id: UUID,
        *,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Notification]:
        """List notifications for a user, newest first."""
        query = sa_select(Notification).where(
            Notification.user_id == user_id,
        )
        if unread_only:
            query = query.where(Notification.is_read.is_(False))
        query = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: UUID) -> int:
        """Return the number of unread notifications for a user."""
        result = await self.db.execute(
            sa_select(sa_func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        return result.scalar() or 0

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification | None:
        """Mark a notification as read (only if it belongs to the user)."""
        result = await self.db.execute(
            sa_select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()
        if not notification:
            return None
        notification.is_read = True
        notification.read_at = datetime.now(timezone.utc)
        return notification

    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all unread notifications for a user as read. Returns affected count."""
        result = await self.db.execute(
            sa_select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
        )
        notifications = result.scalars().all()
        now = datetime.now(timezone.utc)
        for notification in notifications:
            notification.is_read = True
            notification.read_at = now
        return len(notifications)

    async def list_admin_user_ids(self) -> list[UUID]:
        """Return IDs of all users with the admin role."""
        result = await self.db.execute(
            sa_select(User.id)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(Role.name == "admin")
            .distinct()
        )
        return [row[0] for row in result.all()]

    async def notify_admins_course_needs_class(
        self,
        course_id: UUID,
        course_title: str,
    ) -> None:
        """
        Notify every admin (in-app + email) that a course has reached 5 active
        enrollments but has no active classes yet.
        """
        admin_ids = await self.list_admin_user_ids()
        if not admin_ids:
            return

        title = f"Curso '{course_title}' necesita una clase"
        message = (
            f"El curso '{course_title}' ya tiene 5 inscripciones activas y no tiene "
            "ninguna clase activa. Creá una clase y asigná a los estudiantes."
        )

        for admin_id in admin_ids:
            await self.create_notification(
                user_id=admin_id,
                title=title,
                message=message,
                type="admin_alert",
                reference_type="course",
                reference_id=course_id,
            )

        # Enqueue emails to admins via ARQ
        try:
            from app.services.background_jobs import enqueue_job

            for admin_id in admin_ids:
                # Fetch admin email inside the loop; avoid loading the whole list at once.
                user_result = await self.db.execute(
                    sa_select(User.email).where(User.id == admin_id)
                )
                email = user_result.scalar_one_or_none()
                if email:
                    await enqueue_job(
                        "send_email_job",
                        email,
                        "admin_alert_course_needs_class",
                        {
                            "first_name": "Administrador",
                            "course_title": course_title,
                            "course_id": str(course_id),
                        },
                    )
        except Exception:
            # Email enqueueing must not break the payment approval flow.
            # The in-app notifications are already created.
            pass


async def notify_admins_course_needs_class(
    db: AsyncSession,
    course_id: UUID,
    course_title: str,
) -> None:
    """Convenience standalone helper."""
    svc = NotificationService(db)
    await svc.notify_admins_course_needs_class(course_id, course_title)
