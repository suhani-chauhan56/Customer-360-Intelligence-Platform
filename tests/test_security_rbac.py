"""Unit tests for Security, Authentication, and RBAC in CustomerAtlas."""

import pytest
from security.auth import UserContext, verify_api_key, MASTER_API_KEY
from security.rbac import Role, Permission, has_permission
from security.tenant import get_current_tenant_id, set_current_tenant_id


def test_verify_api_key():
    assert verify_api_key(MASTER_API_KEY) is True
    assert verify_api_key("wrong_key_123") is False
    assert verify_api_key(None) is False
    assert verify_api_key("") is False


def test_admin_permissions():
    assert has_permission(Role.ADMIN.value, Permission.VIEW_ANALYTICS) is True
    assert has_permission(Role.ADMIN.value, Permission.MANAGE_USERS) is True
    assert has_permission(Role.ADMIN.value, Permission.VIEW_AUDIT_LOGS) is True


def test_viewer_permissions():
    assert has_permission(Role.VIEWER.value, Permission.VIEW_ANALYTICS) is True
    assert has_permission(Role.VIEWER.value, Permission.EXPORT_DATA) is False
    assert has_permission(Role.VIEWER.value, Permission.RUN_SIMULATION) is False
    assert has_permission(Role.VIEWER.value, Permission.MANAGE_USERS) is False


def test_invalid_role_permissions():
    assert has_permission("NonExistentRole", Permission.VIEW_ANALYTICS) is False


def test_tenant_context():
    set_current_tenant_id("tenant_corp_123")
    assert get_current_tenant_id() == "tenant_corp_123"
    set_current_tenant_id("")
    assert get_current_tenant_id() == "default_org"
