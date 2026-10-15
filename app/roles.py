from fastapi import APIRouter, Depends

from app.dependencies import require_role
from app.models import User

router = APIRouter(tags=["Role-Based Access Control"])


@router.get("/student/dashboard")
def student_dashboard(
    user: User = Depends(require_role("student"))
):
    return {
        "message": "Welcome to student dashboard",
        "user_id": user.id
    }


@router.get("/teacher/dashboard")
def teacher_dashboard(
    user: User = Depends(require_role("teacher"))
):
    return {
        "message": "Welcome to teacher dashboard",
        "user_id": user.id
    }


@router.get("/admin/dashboard")
def admin_dashboard(
    user: User = Depends(require_role("admin"))
):
    return {
        "message": "Welcome to admin dashboard",
        "user_id": user.id
    }
