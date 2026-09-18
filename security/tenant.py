"""Multi-Tenant context isolation and tenant boundary enforcement for CustomerAtlas."""

from contextvars import ContextVar
from typing import Optional

# Thread-local / Async Context variable storing the active organization tenant ID
_current_tenant_id: ContextVar[str] = ContextVar("current_tenant_id", default="default_org")


def get_current_tenant_id() -> str:
    """Retrieve active organization tenant ID for current execution context."""
    return _current_tenant_id.get()


def set_current_tenant_id(tenant_id: str) -> None:
    """Set active organization tenant ID for current execution context."""
    _current_tenant_id.set(tenant_id or "default_org")
