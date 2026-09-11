"""
CodeAcademy Pro — Tests: Optional teacher_id in courses
Validates the end-to-end flow for creating and updating courses
with or without an assigned teacher.

Run with:
    pytest backend/tests/test_courses_optional_teacher.py -v
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from app.schemas.course import CourseCreate, CourseUpdate
from app.services.course_service import CourseService, slugify


# ---------------------------------------------------------------------------
# Schema Validation Tests
# ---------------------------------------------------------------------------

class TestCourseCreateSchema:
    """Verify Pydantic schema accepts or rejects teacher_id correctly."""

    def test_create_with_teacher_id(self):
        teacher_id = uuid.uuid4()
        data = CourseCreate(
            title="Python Avanzado",
            description="Curso de Python avanzado",
            teacher_id=teacher_id,
            price=Decimal("99.99"),
        )
        assert data.teacher_id == teacher_id

    def test_create_without_teacher_id(self):
        data = CourseCreate(
            title="Python Avanzado",
            description="Curso de Python avanzado",
            teacher_id=None,
            price=Decimal("99.99"),
        )
        assert data.teacher_id is None

    def test_create_teacher_id_default_none(self):
        data = CourseCreate(
            title="Python Avanzado",
            description="Curso de Python avanzado",
            price=Decimal("99.99"),
        )
        assert data.teacher_id is None

    def test_create_rejects_empty_string_teacher_id(self):
        with pytest.raises(ValidationError) as exc_info:
            CourseCreate(
                title="Python Avanzado",
                description="Curso de Python avanzado",
                teacher_id="",
                price=Decimal("99.99"),
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("teacher_id",) for e in errors)


class TestCourseUpdateSchema:
    """Verify CourseUpdate allows explicit teacher_id=None."""

    def test_update_allows_teacher_id_none(self):
        data = CourseUpdate(teacher_id=None)
        assert data.teacher_id is None

    def test_update_allows_teacher_id_uuid(self):
        tid = uuid.uuid4()
        data = CourseUpdate(teacher_id=tid)
        assert data.teacher_id == tid

    def test_update_allows_unset_teacher_id(self):
        data = CourseUpdate(title="Nuevo título")
        assert data.teacher_id is None  # default
        assert data.title == "Nuevo título"

    def test_update_rejects_empty_string_teacher_id(self):
        with pytest.raises(ValidationError) as exc_info:
            CourseUpdate(teacher_id="")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("teacher_id",) for e in errors)


# ---------------------------------------------------------------------------
# Service Logic Tests (mocked DB)
# ---------------------------------------------------------------------------

class TestCourseServiceCreate:
    """Verify CourseService.create_course handles optional teacher_id."""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_db):
        return CourseService(mock_db)

    @pytest.mark.asyncio
    async def test_create_with_teacher_id(self, service, mock_db):
        mock_repo = AsyncMock()
        mock_repo.get_by_slug = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(side_effect=lambda c: c)
        service.course_repo = mock_repo

        teacher_id = uuid.uuid4()
        result = await service.create_course(
            title="Curso con docente",
            description="Desc",
            teacher_id=teacher_id,
            price=49.99,
        )
        assert result["title"] == "Curso con docente"
        created = mock_repo.create.call_args[0][0]
        assert created.teacher_id == teacher_id

    @pytest.mark.asyncio
    async def test_create_without_teacher_id(self, service, mock_db):
        mock_repo = AsyncMock()
        mock_repo.get_by_slug = AsyncMock(return_value=None)
        mock_repo.create = AsyncMock(side_effect=lambda c: c)
        service.course_repo = mock_repo

        result = await service.create_course(
            title="Curso sin docente",
            description="Desc",
            teacher_id=None,
            price=49.99,
        )
        assert result["title"] == "Curso sin docente"
        created = mock_repo.create.call_args[0][0]
        assert created.teacher_id is None

    @pytest.mark.asyncio
    async def test_slug_unique_fallback_without_teacher(self, service, mock_db):
        mock_repo = AsyncMock()
        mock_repo.get_by_slug = AsyncMock(return_value=MagicMock())
        mock_repo.create = AsyncMock(side_effect=lambda c: c)
        service.course_repo = mock_repo

        await service.create_course(
            title="Curso sin docente",
            description="Desc",
            teacher_id=None,
            price=49.99,
        )
        created = mock_repo.create.call_args[0][0]
        assert created.slug.startswith("curso-sin-docente-")
        # suffix should be 4 chars (from uuid4)
        assert len(created.slug.split("-")[-1]) == 4


class TestCourseServiceUpdate:
    """Verify CourseService.update_course allows explicit None for nullable fields."""

    @pytest.fixture
    def service(self):
        db = MagicMock()
        svc = CourseService(db)
        return svc

    @pytest.mark.asyncio
    async def test_update_sets_teacher_id_to_none(self, service):
        course = MagicMock()
        course.teacher_id = uuid.uuid4()
        course.deleted_at = None

        async def mock_execute(query):
            result = MagicMock()
            result.scalar_one_or_none = MagicMock(return_value=course)
            return result

        service.db.execute = mock_execute
        service.course_repo = AsyncMock()
        service.course_repo.update = AsyncMock(side_effect=lambda c: c)
        service.course_repo.get_by_id_full = AsyncMock(return_value=None)

        await service.update_course(course.id, teacher_id=None)
        assert course.teacher_id is None

    @pytest.mark.asyncio
    async def test_update_sets_teacher_id_to_new_value(self, service):
        course = MagicMock()
        course.teacher_id = None
        course.deleted_at = None

        async def mock_execute(query):
            result = MagicMock()
            result.scalar_one_or_none = MagicMock(return_value=course)
            return result

        service.db.execute = mock_execute
        service.course_repo = AsyncMock()
        service.course_repo.update = AsyncMock(side_effect=lambda c: c)
        service.course_repo.get_by_id_full = AsyncMock(return_value=None)

        new_teacher = uuid.uuid4()
        await service.update_course(course.id, teacher_id=new_teacher)
        assert course.teacher_id == new_teacher

    @pytest.mark.asyncio
    async def test_update_skips_unset_fields(self, service):
        course = MagicMock()
        course.title = "Original"
        course.deleted_at = None

        async def mock_execute(query):
            result = MagicMock()
            result.scalar_one_or_none = MagicMock(return_value=course)
            return result

        service.db.execute = mock_execute
        service.course_repo = AsyncMock()
        service.course_repo.update = AsyncMock(side_effect=lambda c: c)
        service.course_repo.get_by_id_full = AsyncMock(return_value=None)

        await service.update_course(course.id, title="Nuevo")
        assert course.title == "Nuevo"


# ---------------------------------------------------------------------------
# Serialization Tests
# ---------------------------------------------------------------------------

class TestCourseSerialization:
    """Verify output when teacher is None."""

    @pytest.mark.asyncio
    async def test_list_item_teacher_none(self):
        course = MagicMock()
        course.id = uuid.uuid4()
        course.title = "Curso"
        course.slug = "curso"
        course.description = "Descripción larga de prueba"
        course.short_description = None
        course.thumbnail_url = None
        course.price = Decimal("0.00")
        course.currency = "USD"
        course.level = "beginner"
        course.duration_hours = None
        course.is_featured = False
        course.is_active = True
        course.max_students = None
        course.teacher = None
        course.category = None

        from unittest.mock import AsyncMock
        mock_db = MagicMock()
        mock_db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value="100")))
        svc = CourseService(mock_db)
        svc._get_enrolled_count = AsyncMock(return_value=0)
        svc._get_course_classes_summary = AsyncMock(return_value={
            "total_classes_count": 0,
            "total_available_slots": 0,
            "has_available_classes": False,
        })
        item = await svc._course_to_list_item(course)
        assert item["teacher"] is None
        assert item["category"] is None
        assert item["description"] == "Descripción larga de prueba"
        assert item["max_students"] is None


# ---------------------------------------------------------------------------
# Router Payload Tests (simulated)
# ---------------------------------------------------------------------------

class TestRouterPayloadHandling:
    """Verify the router passes the correct payload shapes to the service."""

    def test_update_uses_exclude_unset(self):
        from app.schemas.course import CourseUpdate

        data = CourseUpdate(title="Nuevo", teacher_id=None)
        dumped = data.model_dump(exclude_unset=True)
        assert "title" in dumped
        assert "teacher_id" in dumped
        assert dumped["teacher_id"] is None

    def test_update_excludes_unset_fields(self):
        from app.schemas.course import CourseUpdate

        data = CourseUpdate(title="Nuevo")
        dumped = data.model_dump(exclude_unset=True)
        assert "title" in dumped
        assert "teacher_id" not in dumped
        assert "price" not in dumped

    def test_create_dumps_all_fields(self):
        from app.schemas.course import CourseCreate

        data = CourseCreate(title="Curso", description="Descripción larga", price=Decimal("10"))
        dumped = data.model_dump()
        assert dumped["teacher_id"] is None
        assert dumped["category_id"] is None
