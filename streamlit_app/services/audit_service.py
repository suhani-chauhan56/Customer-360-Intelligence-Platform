"""Enterprise Audit and Observability Service for CustomerAtlas.

Provides structured logging of security, analytical, and operational events
with dual-mode database repository persistence and fallback in-memory/file streaming.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from utils.logging_config import logger


# In-memory transient buffer for audit events when running without an external DB
_TRANSIENT_AUDIT_BUFFER: List[Dict[str, Any]] = []


def record_audit_event(
    action: str,
    resource_type: str,
    user_id: str = "usr_analyst",
    org_id: str = "default_org",
    resource_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> Dict[str, Any]:
    """Record an enterprise compliance and operational audit log event."""
    event = {
        "action": action,
        "resource_type": resource_type,
        "user_id": user_id,
        "org_id": org_id,
        "resource_id": resource_id,
        "details": details,
        "ip_address": ip_address or "127.0.0.1",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    }

    # Attempt to write to database repository if available
    try:
        from database.connection import db_session_scope
        from database.repositories.audit_repository import AuditRepository

        with db_session_scope() as session:
            repo = AuditRepository(session)
            repo.log_event(
                action=action,
                resource_type=resource_type,
                org_id=org_id,
                user_id=user_id,
                resource_id=resource_id,
                details=details,
                ip_address=ip_address,
            )
    except Exception as e:
        logger.debug(f"Audit log writing to database skipped (using transient buffer): {e}")

    # Always keep in transient buffer for real-time UI inspection
    _TRANSIENT_AUDIT_BUFFER.insert(0, event)
    if len(_TRANSIENT_AUDIT_BUFFER) > 500:
        _TRANSIENT_AUDIT_BUFFER.pop()

    logger.info(f"AUDIT | {action} | resource={resource_type}:{resource_id} | user={user_id}")
    return event


def get_recent_audit_events(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent enterprise audit log events."""
    try:
        from database.connection import db_session_scope
        from database.repositories.audit_repository import AuditRepository

        with db_session_scope() as session:
            repo = AuditRepository(session)
            db_logs = repo.get_recent_events(limit=limit)
            if db_logs:
                return [
                    {
                        "action": l.action,
                        "resource_type": l.resource_type,
                        "user_id": l.user_id,
                        "org_id": l.org_id,
                        "resource_id": l.resource_id,
                        "details": l.details,
                        "ip_address": l.ip_address,
                        "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    }
                    for l in db_logs
                ]
    except Exception:
        pass

    return _TRANSIENT_AUDIT_BUFFER[:limit]
