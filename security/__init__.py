"""Security, RBAC, and multi-tenancy package for CustomerAtlas."""

from security.rbac import Role, Permission, ROLE_PERMISSIONS, has_permission
from security.auth import UserContext, verify_api_key, MASTER_API_KEY
from security.tenant import get_current_tenant_id, set_current_tenant_id

__all__ = [
    "Role",
    "Permission",
    "ROLE_PERMISSIONS",
    "has_permission",
    "UserContext",
    "verify_api_key",
    "MASTER_API_KEY",
    "get_current_tenant_id",
    "set_current_tenant_id",
]
