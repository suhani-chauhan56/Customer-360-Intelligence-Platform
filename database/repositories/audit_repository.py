"""Audit Repository for compliance logging and user activity tracking."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import desc
from sqlalchemy.orm import Session

from database.models import AuditLog
from database.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Data access repository for security and compliance audit events."""

    def __init__(self, session: Session):
        super().__init__(AuditLog, session)

    def log_event(
        self,
        action: str,
        resource_type: str,
        org_id: str = "default_org",
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """Create and persist an audit event log."""
        event = AuditLog(
            org_id=org_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
        )
        self.session.add(event)
        self.session.commit()
        return event

    def get_recent_events(self, org_id: str = "default_org", limit: int = 50) -> List[AuditLog]:
        """Fetch the most recent audit logs for an organization."""
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.org_id == org_id)
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .all()
        )
