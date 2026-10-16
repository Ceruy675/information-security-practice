from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.audit.logger import AuditLog
from app.database import get_db
from app.dependencies import require_role
from app.models import User

router = APIRouter(prefix="/admin", tags=["Security Audit"])


@router.get("/audit-log")
def audit_log(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    events = (
        db.query(AuditLog)
        .order_by(AuditLog.id.desc())
        .limit(limit)
        .all()
    )
    return [{
        "id": e.id,
        "action": e.action,
        "status": e.status,
        "ip": e.ip_address,
        "timestamp": e.timestamp.isoformat(),
        "status_code": e.status_code,
    } for e in events]


@router.get("/security-stats")
def security_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    events = db.query(AuditLog).filter(
        AuditLog.timestamp >= since
    ).all()

    return {
        "period_hours": 24,
        "total_events": len(events),
        "failed_logins": sum(
            e.action == "login_failed" for e in events
        ),
        "access_denied": sum(
            e.action == "access_denied" for e in events
        ),
        "rate_limited": sum(
            e.action == "rate_limited" for e in events
        ),
    }
