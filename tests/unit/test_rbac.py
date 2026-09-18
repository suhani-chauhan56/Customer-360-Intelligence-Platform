"""Unit tests for Role-Based Access Control (RBAC) permissions."""

import pytest
from security.rbac import Role, Permission, has_permission, ROLE_PERMISSIONS


def test_admin_permissions():
    assert has_permission(Role.ADMIN.value, Permission.MANAGE_CONFIGURATION) is True
    assert has_permission(Role.ADMIN.value, Permission.VIEW_AUDIT_LOGS) is True
    assert has_permission(Role.ADMIN.value, Permission.RUN_INFERENCE) is True


def test_analyst_permissions():
    assert has_permission(Role.ANALYST.value, Permission.VIEW_ANALYTICS) is True
    assert has_permission(Role.ANALYST.value, Permission.RUN_INFERENCE) is True
    assert has_permission(Role.ANALYST.value, Permission.EXPORT_DATA) is True
    assert has_permission(Role.ANALYST.value, Permission.MANAGE_CONFIGURATION) is False
    assert has_permission(Role.ANALYST.value, Permission.VIEW_AUDIT_LOGS) is False


def test_viewer_permissions():
    assert has_permission(Role.VIEWER.value, Permission.VIEW_ANALYTICS) is True
    assert has_permission(Role.VIEWER.value, Permission.SEARCH_CUSTOMERS) is True
    assert has_permission(Role.VIEWER.value, Permission.RUN_INFERENCE) is False
    assert has_permission(Role.VIEWER.value, Permission.EXPORT_DATA) is False


def test_invalid_role():
    assert has_permission("NonExistentRole", Permission.VIEW_ANALYTICS) is False
