from app.audit.logger import AuditLog
from app.audit.middleware import AuditMiddleware
from app.audit.router import router as audit_router
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import Base, engine
from app import models
from app.auth import router as auth_router
from app.roles import router as roles_router
from app.limiter import limiter
from app.courses import router as courses_router
from app.enrollments import router as enrollments_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Електронний деканат",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_middleware(AuditMiddleware)

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

app.include_router(auth_router)
app.include_router(roles_router)
app.include_router(courses_router)
app.include_router(enrollments_router)
app.include_router(audit_router)

@app.get("/")
def root():
    return {"message": "Hello World"}
