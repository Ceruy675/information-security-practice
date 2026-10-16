from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role, get_current_user
from app.models import Course, User
from app.sanitizer import sanitize_text

router = APIRouter(prefix="/courses", tags=["Courses"])


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=1000)


class CourseResponse(BaseModel):
    id: int
    title: str
    description: str
    teacher_id: int

    model_config = {"from_attributes": True}


@router.post("/", response_model=CourseResponse)
def create_course(
    data: CourseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("teacher"))
):
    course = Course(
        title=sanitize_text(data.title),
        description=sanitize_text(data.description),
        teacher_id=user.id
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


@router.get("/", response_model=list[CourseResponse])
def list_courses(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Course).all()
