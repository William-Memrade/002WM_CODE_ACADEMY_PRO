"""
CodeAcademy Pro — Pydantic Schemas: Course
Request/response schemas for courses, modules, lessons.
"""

import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CourseCreate(BaseModel):
    """POST /courses request body."""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10, max_length=5000)
    short_description: str | None = Field(None, max_length=500)
    category_id: UUID | None = None
    price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    currency: str = Field("USD", max_length=3)
    level: str = Field("beginner")
    duration_hours: int | None = Field(None, ge=0)
    duration_months: int | None = Field(None, ge=1)
    full_payment_discount_pct: Decimal | None = Field(None, ge=0, le=100)
    is_featured: bool = False
    teacher_id: UUID | None = None

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        if v not in ("beginner", "intermediate", "advanced"):
            raise ValueError("Level must be beginner, intermediate, or advanced")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if re.search(r"[<>]", v):
            raise ValueError("Title must not contain HTML characters")
        return v.strip()


class CourseUpdate(BaseModel):
    """PUT /courses/{id} request body."""
    title: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = Field(None, min_length=10, max_length=5000)
    short_description: str | None = Field(None, max_length=500)
    category_id: UUID | None = None
    price: Decimal | None = Field(None, ge=0)
    currency: str | None = Field(None, max_length=3)
    level: str | None = None
    duration_hours: int | None = Field(None, ge=0)
    duration_months: int | None = Field(None, ge=1)
    full_payment_discount_pct: Decimal | None = Field(None, ge=0, le=100)
    is_featured: bool | None = None
    teacher_id: UUID | None = None


class CoursePricingDetail(BaseModel):
    """Computed pricing for a course."""
    total_price: Decimal
    duration_months: int | None
    full_payment_discount_pct: Decimal
    monthly_price: Decimal | None = None
    full_payment_price: Decimal | None = None
    currency: str


class CourseResponse(BaseModel):
    """Course detail response."""
    id: UUID
    title: str
    slug: str
    description: str
    short_description: str | None
    thumbnail_url: str | None
    category: "CategoryResponse | None"
    price: Decimal
    currency: str
    level: str
    duration_hours: int | None
    duration_months: int | None
    full_payment_discount_pct: Decimal
    is_active: bool
    is_featured: bool
    max_students: int | None
    effective_max_students: int | None = None
    enrolled_count: int = 0
    available_slots: int | None = None
    total_classes_count: int = 0
    total_available_slots: int = 0
    has_available_classes: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class CourseListItem(BaseModel):
    """Course item in list responses."""
    id: UUID
    title: str
    slug: str
    short_description: str | None
    thumbnail_url: str | None
    price: Decimal
    currency: str
    level: str
    duration_hours: int | None
    duration_months: int | None
    full_payment_discount_pct: Decimal
    is_featured: bool
    effective_max_students: int | None = None
    enrolled_count: int = 0
    available_slots: int | None = None
    total_classes_count: int = 0
    total_available_slots: int = 0
    has_available_classes: bool = False

    model_config = {"from_attributes": True}


class CategoryCreate(BaseModel):
    """POST /courses/categories request body."""
    name: str = Field(..., min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)
    sort_order: int = Field(0, ge=0)


class CategoryUpdate(BaseModel):
    """PUT /courses/categories/{id} request body."""
    name: str | None = Field(None, min_length=2, max_length=100)
    description: str | None = Field(None, max_length=500)
    sort_order: int | None = Field(None, ge=0)
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    """Category in responses."""
    id: UUID
    name: str
    slug: str
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0
    model_config = {"from_attributes": True}


class TeacherBrief(BaseModel):
    """Teacher brief info in course responses."""
    id: UUID
    first_name: str
    last_name: str
    avatar_url: str | None
    model_config = {"from_attributes": True}


class ReorderRequest(BaseModel):
    """
    PATCH /courses/{course_id}/modules/order y /courses/modules/{module_id}/lessons/order.

    `ordered_ids` es la lista en el orden final (lo que envía el drag & drop). El backend
    reescribe `sort_order` como 0..n-1; lo que no venga en la lista queda detrás, en su
    orden actual, así que una lista parcial nunca borra ni pierde elementos.
    """
    ordered_ids: list[UUID] = Field(..., min_length=1)


class ModuleCreate(BaseModel):
    """POST /modules request body."""
    course_id: UUID
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = Field(None, max_length=2000)
    sort_order: int = Field(0, ge=0)


class ModuleUpdate(BaseModel):
    """PUT /modules/{id} request body."""
    title: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=2000)
    sort_order: int | None = Field(None, ge=0)
    is_published: bool | None = None


class LessonCreate(BaseModel):
    """POST /lessons request body."""
    module_id: UUID
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = Field(None, max_length=2000)
    content: str | None = Field(None, max_length=50000)
    sort_order: int = Field(0, ge=0)
    duration_minutes: int | None = Field(None, ge=0)
    is_free: bool = False


class LessonUpdate(BaseModel):
    """PUT /lessons/{id} request body."""
    title: str | None = Field(None, min_length=2, max_length=255)
    description: str | None = Field(None, max_length=2000)
    content: str | None = Field(None, max_length=50000)
    sort_order: int | None = Field(None, ge=0)
    duration_minutes: int | None = Field(None, ge=0)
    is_free: bool | None = None
    is_published: bool | None = None


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: list
    total: int
    page: int
    per_page: int
    pages: int
