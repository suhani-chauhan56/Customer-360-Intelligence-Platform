"""Authentication, API token verification, and security context utilities for CustomerAtlas."""

import os
from typing import Optional
from pydantic import BaseModel
from security.rbac import Role


class UserContext(BaseModel):
    """Authenticated user context carrying identity, role, and tenant isolation."""
    user_id: str = "usr_default"
    org_id: str = "default_org"
    email: str = "analyst@customeratlas.io"
    full_name: str = "Enterprise Analyst"
    role: Role = Role.ANALYST
    is_authenticated: bool = True


# Standard Master API Key for service-to-service or enterprise integration
MASTER_API_KEY = os.getenv("CUSTOMERATLAS_API_KEY", "ca_live_enterprise_secret_key_demo")


def verify_api_key(api_key: Optional[str]) -> bool:
    """Verify provided API Key against configured enterprise credentials."""
    if not api_key:
        return False
    # Constant-time comparison to prevent timing attacks
    import hmac
    return hmac.compare_digest(api_key.strip(), MASTER_API_KEY)
