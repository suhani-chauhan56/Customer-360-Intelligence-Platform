"""Role-Based Access Control (RBAC) definitions and permission enforcement for CustomerAtlas.

Implements explicit roles: Admin, Analyst, Manager, Viewer with granular permissions.
"""

from enum import Enum
from typing import Dict, List, Set


class Role(str, Enum):
    ADMIN = "Admin"
    ANALYST = "Analyst"
    MANAGER = "Manager"
    VIEWER = "Viewer"


class Permission(str, Enum):
    # Analytics & Dashboards
    VIEW_ANALYTICS = "analytics:view"
    VIEW_CUSTOMER_360 = "customer_360:view"
    SEARCH_CUSTOMERS = "customers:search"
    COMPARE_CUSTOMERS = "customers:compare"
    
    # Exports & Actions
    EXPORT_DATA = "data:export"
    EXPORT_PDF = "pdf:export"
    RUN_SIMULATION = "simulation:run"
    
    # ML & System Governance
    RUN_INFERENCE = "ml:infer"
    VIEW_DRIFT_MONITORING = "ml:view_drift"
    VIEW_AUDIT_LOGS = "system:view_audit"
    MANAGE_CONFIGURATION = "system:manage_config"
    MANAGE_USERS = "users:manage"


# Granular Role to Permission Mapping Matrix
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_CUSTOMER_360,
        Permission.SEARCH_CUSTOMERS,
        Permission.COMPARE_CUSTOMERS,
        Permission.EXPORT_DATA,
        Permission.EXPORT_PDF,
        Permission.RUN_SIMULATION,
        Permission.RUN_INFERENCE,
        Permission.VIEW_DRIFT_MONITORING,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_CONFIGURATION,
        Permission.MANAGE_USERS,
    },
    Role.ANALYST: {
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_CUSTOMER_360,
        Permission.SEARCH_CUSTOMERS,
        Permission.COMPARE_CUSTOMERS,
        Permission.EXPORT_DATA,
        Permission.EXPORT_PDF,
        Permission.RUN_SIMULATION,
        Permission.RUN_INFERENCE,
        Permission.VIEW_DRIFT_MONITORING,
    },
    Role.MANAGER: {
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_CUSTOMER_360,
        Permission.SEARCH_CUSTOMERS,
        Permission.COMPARE_CUSTOMERS,
        Permission.EXPORT_PDF,
        Permission.RUN_SIMULATION,
    },
    Role.VIEWER: {
        Permission.VIEW_ANALYTICS,
        Permission.VIEW_CUSTOMER_360,
        Permission.SEARCH_CUSTOMERS,
    },
}


def has_permission(user_role: str, permission: Permission) -> bool:
    """Check whether a given user role possesses a specific permission."""
    try:
        r = Role(user_role)
        return permission in ROLE_PERMISSIONS.get(r, set())
    except ValueError:
        return False
