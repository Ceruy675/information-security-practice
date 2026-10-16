import json
import logging
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database import Base, SessionLocal

logger = logging.getLogger("security_audit")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    user_id = Column(Integer, nullable=True)
    username = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=False)
    action = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    http_method = Column(String(10), nullable=True)
    endpoint = Column(String(200), nullable=True)
    status_code = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)


def log_event(action, status, ip_address, **kwargs):
    allowed = {
        "user_id", "username", "http_method",
        "endpoint", "status_code"
    }
    data = {k: v for k, v in kwargs.items() if k in allowed}

    with SessionLocal() as db:
        event = AuditLog(
            action=action,
            status=status,
            ip_address=ip_address,
            **data,
        )
        db.add(event)
        db.commit()

    logger.info(json.dumps({
        "action": action,
        "status": status,
        "ip": ip_address,
    }))
