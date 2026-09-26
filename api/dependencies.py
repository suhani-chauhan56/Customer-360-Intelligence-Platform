import sys
from pathlib import Path
from typing import Generator, Optional

# Ensure root and streamlit_app are in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
APP_DIR = ROOT_DIR / "streamlit_app"
for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from fastapi import Header, HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database.connection import get_db_session
from security.auth import UserContext, verify_api_key, MASTER_API_KEY
from security.rbac import Permission, Role, has_permission
from security.tenant import set_current_tenant_id
from utils.logging_config import logger

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_auth = HTTPBearer(auto_error=False)


def get_current_user(
    x_api_key: Optional[str] = Security(api_key_header),
    auth_creds: Optional[HTTPAuthorizationCredentials] = Security(bearer_auth),
    x_org_id: Optional[str] = Header(default="default_org", alias="X-Organization-ID"),
) -> UserContext:
    """Validate incoming API credentials and establish user and tenant context."""
    provided_key = x_api_key
    if not provided_key and auth_creds:
        provided_key = auth_creds.credentials

    # For development & evaluation demo: allow anonymous with Analyst role if key not passed
    if provided_key:
        if not verify_api_key(provided_key):
            logger.warning(f"Invalid API key attempt from tenant {x_org_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key credentials.",
            )
        # Authenticated as Admin via valid master key
        user_ctx = UserContext(
            user_id="usr_api_key",
            org_id=x_org_id or "default_org",
            email="api@customeratlas.io",
            full_name="Enterprise API Client",
            role=Role.ADMIN,
            is_authenticated=True,
        )
    else:
        # Default Analyst context for local/demo API calls
        user_ctx = UserContext(
            user_id="usr_default",
            org_id=x_org_id or "default_org",
            email="analyst@customeratlas.io",
            full_name="Enterprise Analyst",
            role=Role.ANALYST,
            is_authenticated=True,
        )

    # Set context tenant ID
    set_current_tenant_id(user_ctx.org_id)
    return user_ctx


def require_permission(permission: Permission):
    """Enforce specific RBAC permission requirement on endpoint."""
    def permission_checker(current_user: UserContext = Depends(get_current_user)) -> UserContext:
        if not has_permission(current_user.role.value, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: User role '{current_user.role.value}' lacks required permission '{permission.value}'.",
            )
        return current_user
    return permission_checker
