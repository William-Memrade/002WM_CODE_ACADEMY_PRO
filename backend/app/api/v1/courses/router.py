"""
CodeAcademy Pro — Courses Router
CRUD, catalog, modules, lessons, category management.
"""

import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.rls import get_rls_db
from app.middlewares.rbac import require_admin, require_admin_or_teacher
from app.models.course import Category
from app.schemas.course import (
    CourseCreate, CourseUpdate, ModuleCreate, LessonCreate,
    CategoryCreate, CategoryUpdate,
)
from app.services.course_service import CourseService, slugify
from app.services.audit_service import AuditService

router = APIRouter()


# ── Public Endpoints ──────────────────────────────────────────────────────────


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """List active categories (public). Cached for 5 minutes."""
    from app.core.cache import cache

    async def _fetch():
        svc = CourseService(db)
        cats = await svc.category_repo.list_active()
        return [
            {
                "id": str(c.id),
                "name": c.name,
                "slug": c.slug,
                "description": c.description,
                "sort_order": c.sort_order,
                "is_active": c.is_active,
            }
            for c in cats
        ]

    return await cache.get_or_set("categories:active", _fetch, ttl_seconds=300)


@router.get("")
async def list_courses(
    category: str | None = None,
    level: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List active courses (public)."""
    svc = CourseService(db)
    return await svc.list_courses(
        category=category, level=level, search=search, page=page, per_page=per_page
    )


@router.get("/admin/all")
async def admin_list_all_courses(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """List ALL courses including inactive (admin only)."""
    svc = CourseService(db)
    skip = (page - 1) * per_page
    courses, total = await svc.course_repo.list_all_admin(skip=skip, limit=per_page)
    pages = max(1, (total + per_page - 1) // per_page)
    return {
        "items": await asyncio.gather(*[svc._course_to_list_item(c) for c in courses]),
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


@router.get("/{slug}")
async def get_course(slug: str, db: AsyncSession = Depends(get_db)):
    """Get course detail by slug or UUID (public)."""
    svc = CourseService(db)
    # Try UUID first, then slug
    try:
        course_uuid = UUID(slug)
        course = await svc.get_course_by_id(course_uuid)
    except ValueError:
        course = await svc.get_course_detail(slug)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# ── Admin Course CRUD ─────────────────────────────────────────────────────────


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_course(
    data: CourseCreate,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Create a new course (admin only)."""
    svc = CourseService(db)
    result = await svc.create_course(
        title=data.title,
        description=data.description,
        price=float(data.price),
        short_description=data.short_description,
        category_id=data.category_id,
        currency=data.currency,
        level=data.level,
        duration_hours=data.duration_hours,
        duration_months=data.duration_months,
        full_payment_discount_pct=float(data.full_payment_discount_pct) if data.full_payment_discount_pct else None,
        is_featured=data.is_featured,
    )

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="course_created",
        entity_type="course",
        entity_id=result["id"],
        entity_label=result["title"],
        request=request,
        metadata={"slug": result["slug"]},
    )
    return result


@router.put("/{course_id}")
async def update_course(
    course_id: UUID,
    data: CourseUpdate,
    request: Request,
    current_user=Depends(require_admin_or_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """Update course (admin or assigned teacher)."""
    svc = CourseService(db)
    result = await svc.update_course(course_id, **data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Course not found")

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="course_updated",
        entity_type="course",
        entity_id=course_id,
        entity_label=result.get("title"),
        request=request,
        metadata={"fields_updated": list(data.model_dump(exclude_unset=True).keys())},
    )
    return result


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Soft delete course (admin only)."""
    svc = CourseService(db)
    # fetch course label before deletion
    course = await svc.get_course_by_id(course_id)
    deleted = await svc.delete_course(course_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found")

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="course_deleted",
        entity_type="course",
        entity_id=course_id,
        entity_label=course.get("title") if course else None,
        request=request,
    )


@router.patch("/{course_id}/activate")
async def activate_course(
    course_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Activate a course."""
    svc = CourseService(db)
    result = await svc.toggle_active(course_id, True)
    if not result:
        raise HTTPException(status_code=404, detail="Course not found")

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="course_published",
        entity_type="course",
        entity_id=course_id,
        entity_label=result.get("title"),
        request=request,
        metadata={"is_active": True},
    )
    return result


@router.patch("/{course_id}/deactivate")
async def deactivate_course(
    course_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Deactivate a course."""
    svc = CourseService(db)
    result = await svc.toggle_active(course_id, False)
    if not result:
        raise HTTPException(status_code=404, detail="Course not found")

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="course_unpublished",
        entity_type="course",
        entity_id=course_id,
        entity_label=result.get("title"),
        request=request,
        metadata={"is_active": False},
    )
    return result


# ── Category CRUD (Admin) ─────────────────────────────────────────────────────


@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Create a new category (admin only)."""
    svc = CourseService(db)
    slug = slugify(data.name)
    existing = await svc.category_repo.get_by_slug(slug)
    if existing:
        raise HTTPException(status_code=409, detail="A category with this name already exists")

    category = Category(
        name=data.name,
        slug=slug,
        description=data.description,
        sort_order=data.sort_order,
        is_active=True,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)

    from app.core.cache import cache
    await cache.delete("categories:active")

    await AuditService(db).log_action(
        actor_user=current_user,
        action="category_created",
        entity_type="category",
        entity_id=category.id,
        entity_label=category.name,
        request=request,
    )

    return {
        "id": str(category.id),
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "sort_order": category.sort_order,
        "is_active": category.is_active,
    }


@router.put("/categories/{category_id}")
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Update a category (admin only)."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if data.name is not None:
        category.name = data.name
        category.slug = slugify(data.name)
    if data.description is not None:
        category.description = data.description
    if data.sort_order is not None:
        category.sort_order = data.sort_order
    if data.is_active is not None:
        category.is_active = data.is_active

    await db.commit()
    await db.refresh(category)

    from app.core.cache import cache
    await cache.delete("categories:active")

    await AuditService(db).log_action(
        actor_user=current_user,
        action="category_updated",
        entity_type="category",
        entity_id=category.id,
        entity_label=category.name,
        request=request,
        metadata={"updated_fields": list(data.model_dump(exclude_unset=True).keys())},
    )

    return {
        "id": str(category.id),
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "sort_order": category.sort_order,
        "is_active": category.is_active,
    }


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Delete a category (admin only). Fails if courses are assigned."""
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category_name = category.name

    await db.delete(category)
    await db.commit()

    from app.core.cache import cache
    await cache.delete("categories:active")

    await AuditService(db).log_action(
        actor_user=current_user,
        action="category_deleted",
        entity_type="category",
        entity_id=category_id,
        entity_label=category_name,
        request=request,
    )


# ── Module & Lesson Endpoints ─────────────────────────────────────────────────


@router.post("/{course_id}/modules", status_code=status.HTTP_201_CREATED)
async def add_module(
    course_id: UUID,
    data: ModuleCreate,
    current_user=Depends(require_admin_or_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """Add a module to a course."""
    svc = CourseService(db)
    return await svc.add_module(
        course_id=course_id, title=data.title,
        description=data.description, sort_order=data.sort_order,
    )


@router.post("/modules/{module_id}/lessons", status_code=status.HTTP_201_CREATED)
async def add_lesson(
    module_id: UUID,
    data: LessonCreate,
    current_user=Depends(require_admin_or_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """Add a lesson to a module."""
    svc = CourseService(db)
    return await svc.add_lesson(
        module_id=module_id, title=data.title,
        description=data.description, sort_order=data.sort_order,
        duration_minutes=data.duration_minutes, is_free=data.is_free,
    )
