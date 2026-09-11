"""Reviews router."""
from fastapi import APIRouter, Depends
from app.middlewares.rbac import require_student
from app.db.rls import get_rls_db

router = APIRouter()

@router.post("/")
async def create_review(current_user=Depends(require_student)):
    """Create a course review (student)."""
    return {}

@router.get("/course/{course_id}")
async def course_reviews(course_id: str, page: int = 1, per_page: int = 20):
    """Get reviews for a course (public)."""
    return {"items": [], "total": 0}
