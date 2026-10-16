from app.audit.detector import check_brute_force
from app.audit.logger import log_event
from app.crypto.encryption import blind_index
from fastapi import Request
from app.limiter import limiter
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserResponse
from app.security import hash_password

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db)
):
    email = str(data.email).lower()

    existing_user = db.query(User).filter(
        User.email_index == blind_index(email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    user = User(
        email=email,
        hashed_password=hash_password(data.password),
        role="student"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import TokenResponse
from app.security import verify_password, create_access_token


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username.lower()

    ip = request.client.host if request.client else "unknown"

    if check_brute_force(db, ip, email):
        raise HTTPException(
            status_code=429,
            detail="Too many failed attempts. Try again later."
        )

    user = db.query(User).filter(
        User.email_index == blind_index(email)
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        log_event(
            "login_failed", "failure",
            request.client.host if request.client else "unknown",
            username=blind_index(email),
            http_method="POST",
            endpoint="/login",
            status_code=401,
        )
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    log_event(
        "login_success", "success",
        request.client.host if request.client else "unknown",
        user_id=user.id,
        http_method="POST",
        endpoint="/login",
        status_code=200,
    )

    token = create_access_token(
        user_id=user.id,
        role=user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


from app.dependencies import get_current_user


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user

