from datetime import datetime, timedelta, timezone

from sqlalchemy import func, or_

from app.audit.logger import AuditLog, log_event
from app.crypto.encryption import blind_index


def check_brute_force(db, ip, email):
    since = datetime.now(timezone.utc) - timedelta(minutes=5)
    identity = blind_index(email)

    count = db.query(func.count(AuditLog.id)).filter(
        AuditLog.action == "login_failed",
        AuditLog.timestamp >= since,
        or_(
            AuditLog.ip_address == ip,
            AuditLog.username == identity
        )
    ).scalar() or 0

    if count >= 5:
        log_event(
            "brute_force_detected",
            "warning",
            ip,
            username=identity,
            endpoint="/login",
            status_code=429
        )
        return True

    return False
