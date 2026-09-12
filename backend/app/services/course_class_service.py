"""
CodeAcademy Pro — Course Class Service
Business logic for course classes and attendance.
"""

import re
import uuid
from datetime import datetime, time, timezone
from uuid import UUID

from sqlalchemy import func as sa_func, select as sa_select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course_class import CourseClass, AttendanceRecord
from app.models.system import SystemSetting
from app.repositories.course_class_repository import CourseClassRepository, AttendanceRepository
from app.core.error_handlers import DuplicateError


def slugify(text: str) -> str:
    """Generate a URL-safe slug from text."""
    text = text.lower().strip()
    text = re.sub(r"[áàäâ]", "a", text)
    text = re.sub(r"[éèëê]", "e", text)
    text = re.sub(r"[íìïî]", "i", text)
    text = re.sub(r"[óòöô]", "o", text)
    text = re.sub(r"[úùüû]", "u", text)
    text = re.sub(r"[ñ]", "n", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


_WEEKDAY_LABELS = {
    "mon": "Lunes",
    "tue": "Martes",
    "wed": "Miércoles",
    "thu": "Jueves",
    "fri": "Viernes",
    "sat": "Sábado",
    "sun": "Domingo",
}

_WEEKDAY_MAP_EN = {
    "monday": "mon",
    "tuesday": "tue",
    "wednesday": "wed",
    "thursday": "thu",
    "friday": "fri",
    "saturday": "sat",
    "sunday": "sun",
}


_DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _format_time(t: time | None) -> str:
    """Format time in 12-hour Spanish format with AM/PM (for schedule_info)."""
    if t is None:
        return ""
    hour = t.hour
    minute = t.minute
    ampm = "AM" if hour < 12 else "PM"
    hour12 = hour % 12
    if hour12 == 0:
        hour12 = 12
    return f"{hour12}:{minute:02d} {ampm}"


def _format_time_24h(t: time | None) -> str | None:
    """Format time in 24-hour HH:MM format for API responses."""
    if t is None:
        return None
    return t.strftime("%H:%M")


def _generate_schedule_info(days_of_week: list[str], start_time: time | None, end_time: time | None) -> str | None:
    """Auto-generate human-readable schedule_info from structured fields.

    Examples:
      - Lunes a Viernes de 7:00 AM a 10:00 AM
      - Lunes, Miércoles y Viernes de 6:00 PM a 8:00 PM
      - Martes de 5:00 PM a 7:00 PM
    """
    if not days_of_week:
        return None

    order = {d: i for i, d in enumerate(_DAY_ORDER)}
    sorted_days = sorted(days_of_week, key=lambda d: order.get(d, 99))

    # Find consecutive runs
    runs: list[list[str]] = []
    current_run = [sorted_days[0]]
    for day in sorted_days[1:]:
        prev_idx = order[current_run[-1]]
        curr_idx = order[day]
        if curr_idx == prev_idx + 1:
            current_run.append(day)
        else:
            runs.append(current_run)
            current_run = [day]
    runs.append(current_run)

    # Format each run
    run_strs: list[str] = []
    for run in runs:
        labels = [_WEEKDAY_LABELS.get(d, d) for d in run]
        if len(run) == 1:
            run_strs.append(labels[0])
        else:
            run_strs.append(f"{labels[0]} a {labels[-1]}")

    if len(run_strs) == 1:
        days_str = run_strs[0]
    else:
        days_str = ", ".join(run_strs[:-1]) + " y " + run_strs[-1]

    time_str = ""
    if start_time and end_time:
        time_str = f" de {_format_time(start_time)} a {_format_time(end_time)}"
    elif start_time:
        time_str = f" de {_format_time(start_time)}"

    return f"{days_str}{time_str}"


def _get_today_weekday() -> str:
    """Return today's weekday code in the model's format."""
    from datetime import datetime
    from app.core.config import get_settings
    settings = get_settings()
    tz = getattr(settings, "TIMEZONE", "America/El_Salvador")
    try:
        import pytz
        now = datetime.now(pytz.timezone(tz))
    except Exception:
        now = datetime.now()
    return _WEEKDAY_MAP_EN.get(now.strftime("%A").lower(), "mon")


class CourseClassService:
    """Business logic for course classes."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CourseClassRepository(db)
        self.attendance_repo = AttendanceRepository(db)

    async def list_classes_by_course(self, course_id: UUID) -> list[dict]:
        """List all classes for a course."""
        classes = await self.repo.list_by_course(course_id)
        return [await self._class_to_dict(c) for c in classes]

    async def list_active_classes_by_course(self, course_id: UUID) -> list[dict]:
        """List active classes for a course."""
        classes = await self.repo.list_active_by_course(course_id)
        return [await self._class_to_dict(c) for c in classes]

    async def list_active_classes_by_course_public(self, course_id: UUID) -> list[dict]:
        """List active classes for a course (public view, no meeting_url)."""
        classes = await self.repo.list_active_by_course(course_id)
        return [await self._class_to_dict_public(c) for c in classes]

    async def create_class(
        self,
        course_id: UUID,
        name: str,
        created_by: UUID | None = None,
        **kwargs,
    ) -> dict:
        """Create a new class for a course."""
        slug = f"{str(course_id)[:8]}-{slugify(name)}"
        existing = await self.repo.get_by_slug(slug)
        if existing:
            suffix = str(uuid.uuid4())[:4]
            slug = f"{slug}-{suffix}"

        name_conflict = await self.repo.get_by_name_in_course(course_id, name)
        if name_conflict:
            raise DuplicateError(f"Ya existe una clase con el nombre '{name}' en este curso")

        days_of_week = kwargs.get("days_of_week") or []
        start_time = kwargs.get("start_time")
        end_time = kwargs.get("end_time")
        schedule_info = _generate_schedule_info(days_of_week, start_time, end_time)

        course_class = CourseClass(
            course_id=course_id,
            name=name,
            slug=slug,
            created_by=created_by,
            schedule_info=schedule_info,
            days_of_week=days_of_week,
            start_time=start_time,
            end_time=end_time,
            meeting_platform=kwargs.get("meeting_platform"),
            meeting_url=kwargs.get("meeting_url"),
            status="active",
        )
        course_class = await self.repo.create(course_class)
        course_class = await self.repo.get_by_id_full(course_class.id)
        return await self._class_to_dict(course_class)

    async def update_class(self, class_id: UUID, **kwargs) -> dict | None:
        """Update a class."""
        course_class = await self.repo.get_by_id_full(class_id)
        if not course_class:
            return None

        for key, value in kwargs.items():
            if hasattr(course_class, key) and value is not None:
                setattr(course_class, key, value)

        # Auto-regenerate schedule_info when schedule fields change
        if any(k in kwargs for k in ("days_of_week", "start_time", "end_time")):
            course_class.schedule_info = _generate_schedule_info(
                course_class.days_of_week,
                course_class.start_time,
                course_class.end_time,
            )

        if "name" in kwargs and kwargs["name"]:
            name_conflict = await self.repo.get_by_name_in_course_excluding(
                course_class.course_id, kwargs["name"], class_id
            )
            if name_conflict:
                raise DuplicateError(f"Ya existe una clase con el nombre '{kwargs['name']}' en este curso")
            new_slug = f"{str(course_class.course_id)[:8]}-{slugify(kwargs['name'])}"
            existing = await self.repo.get_by_slug_excluding(new_slug, class_id)
            if existing:
                suffix = str(uuid.uuid4())[:4]
                new_slug = f"{new_slug}-{suffix}"
            course_class.slug = new_slug

        await self.repo.update(course_class)
        return await self._class_to_dict(course_class)

    async def assign_teacher(self, class_id: UUID, teacher_id: UUID) -> dict | None:
        """Assign a teacher to a class."""
        course_class = await self.repo.get_by_id(class_id)
        if not course_class:
            return None
        course_class.teacher_id = teacher_id
        await self.repo.update(course_class)
        # Re-fetch with eager-loaded teacher relationship for serialization
        course_class = await self.repo.get_by_id_full(class_id)
        if not course_class:
            return None
        return await self._class_to_dict(course_class)

    async def change_status(self, class_id: UUID, new_status: str) -> dict | None:
        """Change class status (active/inactive/cancelled/deleted)."""
        from datetime import datetime, timezone
        course_class = await self.repo.get_by_id_full(class_id)
        if not course_class:
            return None
        course_class.status = new_status
        if new_status == "deleted":
            course_class.deleted_at = datetime.now(timezone.utc)
        elif new_status in ("active", "inactive", "cancelled") and course_class.deleted_at is not None:
            course_class.deleted_at = None
        await self.repo.update(course_class)
        return await self._class_to_dict(course_class)

    async def soft_delete_class(self, class_id: UUID) -> dict | None:
        """Soft delete a class. Sets status=deleted and deleted_at=now."""
        course_class = await self.repo.get_by_id(class_id)
        if not course_class:
            return None
        from datetime import datetime, timezone
        course_class.status = "deleted"
        course_class.deleted_at = datetime.now(timezone.utc)
        await self.repo.update(course_class)
        return {"id": str(class_id), "status": "deleted", "deleted_at": course_class.deleted_at.isoformat()}

    async def update_meeting_link(
        self, class_id: UUID, meeting_platform: str, meeting_url: str
    ) -> dict | None:
        """Update meeting link for a class."""
        course_class = await self.repo.get_by_id_full(class_id)
        if not course_class:
            return None
        course_class.meeting_platform = meeting_platform
        course_class.meeting_url = meeting_url
        await self.repo.update(course_class)
        return await self._class_to_dict(course_class)

    async def update_recording_link(
        self, class_id: UUID, recording_platform: str | None, recording_url: str | None
    ) -> dict | None:
        """
        Publica (o borra) la grabación de la clase.

        `recording_url` vacío o None borra la grabación: el docente deja de exponer un
        enlace que ya no sirve sin tocar el resto de la clase.
        """
        course_class = await self.repo.get_by_id_full(class_id)
        if not course_class:
            return None

        url = (recording_url or "").strip() or None
        course_class.recording_url = url
        course_class.recording_platform = (
            ((recording_platform or "").strip() or None) if url else None
        )
        course_class.recording_updated_at = (
            datetime.now(timezone.utc) if url else None
        )
        await self.repo.update(course_class)
        return await self._class_to_dict(course_class)

    async def get_class(self, class_id: UUID) -> dict | None:
        """Get class detail."""
        course_class = await self.repo.get_by_id_full(class_id)
        if not course_class:
            return None
        return await self._class_to_dict(course_class)

    async def get_class_public(self, class_id: UUID) -> dict | None:
        """Get class detail (public view, no meeting_url)."""
        course_class = await self.repo.get_by_id_full(class_id)
        if not course_class:
            return None
        return await self._class_to_dict_public(course_class)

    async def get_class_capacity(self, class_id: UUID) -> dict | None:
        """Get capacity info for a class."""
        course_class = await self.repo.get_by_id(class_id)
        if not course_class:
            return None

        global_max = await self._get_global_max_students()
        enrolled = await self.repo.get_enrolled_count(class_id)
        available = max(0, global_max - enrolled)

        return {
            "course_class_id": str(class_id),
            "global_max": global_max,
            "enrolled_count": enrolled,
            "available_slots": available,
            "is_full": available <= 0,
        }

    async def find_class_with_capacity(self, course_id: UUID) -> CourseClass | None:
        """Find an active class with available capacity."""
        global_max = await self._get_global_max_students()
        classes = await self.repo.list_active_by_course(course_id)
        for cls in classes:
            enrolled = await self.repo.get_enrolled_count(cls.id)
            if enrolled < global_max:
                return cls
        return None

    async def get_classes_for_teacher(self, teacher_id: UUID) -> list[dict]:
        """Get classes assigned to a teacher."""
        classes = await self.repo.list_by_teacher(teacher_id)
        return [await self._class_to_dict(c) for c in classes]

    async def get_classes_for_student(self, student_id: UUID) -> list[dict]:
        """Get classes where a student has an active enrollment (includes meeting_url)."""
        from app.models.payment import Enrollment
        from sqlalchemy.orm import selectinload
        from app.models.user import Teacher
        result = await self.db.execute(
            sa_select(CourseClass)
            .options(
                selectinload(CourseClass.course),
                selectinload(CourseClass.teacher).selectinload(Teacher.user),
            )
            .join(Enrollment, Enrollment.course_class_id == CourseClass.id)
            .where(
                Enrollment.student_id == student_id,
                Enrollment.status == "active",
                CourseClass.deleted_at.is_(None),
            )
            .order_by(CourseClass.name)
        )
        classes = result.scalars().all()
        return [await self._class_to_dict(c) for c in classes]

    async def list_classes_filtered(self, **filters) -> list[dict]:
        """List classes with backend filters."""
        classes = await self.repo.list_filtered(**filters)
        return [await self._class_to_dict(c) for c in classes]

    async def list_classes_today(self) -> list[dict]:
        """List active classes scheduled for today, ordered by start_time."""
        today_weekday = _get_today_weekday()
        classes = await self.repo.list_today(today_weekday)
        return [await self._class_to_dict(c) for c in classes]

    async def _get_global_max_students(self) -> int:
        """Read global_max_students_per_class from system_settings."""
        result = await self.db.execute(
            sa_select(SystemSetting.value).where(
                SystemSetting.key == "global_max_students_per_class"
            )
        )
        row = result.scalar_one_or_none()
        return int(row) if row else 100

    async def _class_to_dict(self, course_class: CourseClass) -> dict:
        """Serialize a CourseClass to dict (full, includes meeting_url)."""
        global_max = await self._get_global_max_students()
        enrolled = await self.repo.get_enrolled_count(course_class.id)
        available = max(0, global_max - enrolled)

        teacher_name = None
        if hasattr(course_class, "teacher") and course_class.teacher:
            teacher_name = f"{course_class.teacher.user.first_name} {course_class.teacher.user.last_name}".strip()

        course_title = None
        if hasattr(course_class, "course") and course_class.course:
            course_title = course_class.course.title

        return {
            "id": str(course_class.id),
            "course_id": str(course_class.course_id),
            "teacher_id": str(course_class.teacher_id) if course_class.teacher_id else None,
            "teacher_name": teacher_name,
            "created_by": str(course_class.created_by) if course_class.created_by else None,
            "name": course_class.name,
            "slug": course_class.slug,
            "schedule_info": course_class.schedule_info,
            "days_of_week": course_class.days_of_week,
            "start_time": _format_time_24h(course_class.start_time),
            "end_time": _format_time_24h(course_class.end_time),
            "status": course_class.status,
            "meeting_platform": course_class.meeting_platform,
            "meeting_url": course_class.meeting_url,
            "recording_platform": course_class.recording_platform,
            "recording_url": course_class.recording_url,
            "recording_updated_at": (
                course_class.recording_updated_at.isoformat()
                if course_class.recording_updated_at else None
            ),
            "created_at": course_class.created_at.isoformat() if course_class.created_at else None,
            "updated_at": course_class.updated_at.isoformat() if course_class.updated_at else None,
            "deleted_at": course_class.deleted_at.isoformat() if course_class.deleted_at else None,
            "enrolled_count": enrolled,
            "available_slots": available,
            "global_max": global_max,
            "course_title": course_title,
            "has_meeting_link": bool(course_class.meeting_url),
            "has_recording": bool(course_class.recording_url),
        }

    async def _class_to_dict_public(self, course_class: CourseClass) -> dict:
        """Serialize a CourseClass to dict for public consumption (no meeting_url)."""
        global_max = await self._get_global_max_students()
        enrolled = await self.repo.get_enrolled_count(course_class.id)
        available = max(0, global_max - enrolled)

        teacher_name = None
        if hasattr(course_class, "teacher") and course_class.teacher:
            teacher_name = f"{course_class.teacher.user.first_name} {course_class.teacher.user.last_name}".strip()

        course_title = None
        if hasattr(course_class, "course") and course_class.course:
            course_title = course_class.course.title

        return {
            "id": str(course_class.id),
            "course_id": str(course_class.course_id),
            "teacher_id": str(course_class.teacher_id) if course_class.teacher_id else None,
            "teacher_name": teacher_name,
            "name": course_class.name,
            "slug": course_class.slug,
            "schedule_info": course_class.schedule_info,
            "days_of_week": course_class.days_of_week,
            "start_time": _format_time_24h(course_class.start_time),
            "end_time": _format_time_24h(course_class.end_time),
            "status": course_class.status,
            "created_at": course_class.created_at.isoformat() if course_class.created_at else None,
            "updated_at": course_class.updated_at.isoformat() if course_class.updated_at else None,
            "enrolled_count": enrolled,
            "available_slots": available,
            "global_max": global_max,
            "course_title": course_title,
            "has_meeting_link": bool(course_class.meeting_url),
        }

    async def list_students_by_class(self, class_id: UUID) -> list[dict]:
        """List active enrollments for a class with student details and progress."""
        from app.models.payment import Enrollment
        from app.models.user import User

        result = await self.db.execute(
            sa_select(Enrollment, User)
            .join(User, Enrollment.student_id == User.id)
            .where(
                Enrollment.course_class_id == class_id,
                Enrollment.status == "active",
            )
            .order_by(User.first_name, User.last_name)
        )
        rows = result.all()
        students = []
        for enrollment, user in rows:
            students.append({
                "enrollment_id": str(enrollment.id),
                "student_id": str(user.id),
                "student_name": f"{user.first_name} {user.last_name}".strip(),
                "student_email": user.email,
                "status": enrollment.status,
                # El progreso vive en la inscripción; el docente lo edita desde aquí.
                "progress_percentage": float(enrollment.progress_percentage or 0),
                "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
            })
        return students

    async def is_student_enrolled(self, class_id: UUID, student_id: UUID) -> bool:
        """Check if a student has an active enrollment in a class."""
        from app.models.payment import Enrollment
        result = await self.db.execute(
            sa_select(Enrollment).where(
                Enrollment.course_class_id == class_id,
                Enrollment.student_id == student_id,
                Enrollment.status == "active",
            )
        )
        return result.scalar_one_or_none() is not None


class AttendanceService:
    """Business logic for attendance records."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AttendanceRepository(db)

    async def mark_attendance(
        self,
        course_class_id: UUID,
        student_id: UUID,
        teacher_id: UUID,
        session_date,
        status: str = "present",
        notes: str | None = None,
    ) -> dict:
        """Mark attendance for a student. Creates or updates record."""
        existing = await self.repo.get_by_class_student_date(
            course_class_id, student_id, session_date
        )
        if existing:
            existing.status = status
            existing.notes = notes
            await self.repo.update(existing)
            record = existing
        else:
            record = AttendanceRecord(
                course_class_id=course_class_id,
                student_id=student_id,
                teacher_id=teacher_id,
                session_date=session_date,
                status=status,
                notes=notes,
            )
            record = await self.repo.create(record)

        return {
            "id": str(record.id),
            "course_class_id": str(record.course_class_id),
            "student_id": str(record.student_id),
            "teacher_id": str(record.teacher_id),
            "session_date": str(record.session_date),
            "status": record.status,
            "notes": record.notes,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }

    async def list_class_attendance(self, course_class_id: UUID) -> list[dict]:
        """List all attendance records for a class."""
        records = await self.repo.list_by_class(course_class_id)
        return [
            {
                "id": str(r.id),
                "course_class_id": str(r.course_class_id),
                "student_id": str(r.student_id),
                "teacher_id": str(r.teacher_id),
                "session_date": str(r.session_date),
                "status": r.status,
                "notes": r.notes,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]

    async def list_student_attendance(self, student_id: UUID) -> list[dict]:
        """List attendance records for a student."""
        records = await self.repo.list_by_student(student_id)
        return [
            {
                "id": str(r.id),
                "course_class_id": str(r.course_class_id),
                "student_id": str(r.student_id),
                "teacher_id": str(r.teacher_id),
                "session_date": str(r.session_date),
                "status": r.status,
                "notes": r.notes,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]

    async def update_attendance(self, attendance_id: UUID, status: str, notes: str | None = None) -> dict | None:
        """Update an attendance record."""
        record = await self.repo.get_by_id(attendance_id)
        if not record:
            return None
        record.status = status
        if notes is not None:
            record.notes = notes
        await self.repo.update(record)
        return {
            "id": str(record.id),
            "course_class_id": str(record.course_class_id),
            "student_id": str(record.student_id),
            "teacher_id": str(record.teacher_id),
            "session_date": str(record.session_date),
            "status": record.status,
            "notes": record.notes,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }

    async def get_class_summary(self, course_class_id: UUID) -> dict:
        """Get attendance summary for a class."""
        return await self.repo.get_summary_by_class(course_class_id)
