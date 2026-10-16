from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models import User, Course, Enrollment

router = APIRouter(
    prefix="/enrollments",
    tags=["Enrollments"]
)


class EnrollmentCreate(BaseModel):
    course_id: int = Field(gt=0)


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int

    model_config = {"from_attributes": True}


@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=201
)
def enroll_student(
    data: EnrollmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("student"))
):
    course = db.query(Course).filter(
        Course.id == data.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    existing = db.query(Enrollment).filter(
        Enrollment.student_id == user.id,
        Enrollment.course_id == data.course_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Already enrolled"
        )

    enrollment = Enrollment(
        student_id=user.id,
        course_id=data.course_id
    )

    db.add(enrollment)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Already enrolled"
        )

    db.refresh(enrollment)
    return enrollment


@router.get(
    "/my",
    response_model=list[EnrollmentResponse]
)
def my_enrollments(
    db: Session = Depends(get_db),
    user: User = Depends(require_role("student"))
):
    return db.query(Enrollment).filter(
        Enrollment.student_id == user.id
    ).all()
