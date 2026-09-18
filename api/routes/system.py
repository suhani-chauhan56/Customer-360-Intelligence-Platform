"""System Health, Metrics, and Audit API endpoints for CustomerAtlas."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from api.dependencies import require_permission
from api.schemas.common import APIResponse
from config.settings import get_environment_info
from security.auth import UserContext
from security.rbac import Permission
from services.audit_service import get_recent_audit_events
from services.data_quality_service import run_data_quality_audit
from services.data_service import load_csv
from services.model_service import audit_model_registry
from utils.helpers import calculate_data_snapshot_info

router = APIRouter(prefix="/system", tags=["System & Governance"])


@router.get("/health", response_model=APIResponse[dict])
def get_system_health():
    """Retrieve operational system status, data quality, and model readiness."""
    df = load_csv("customer_360_features.csv")
    quality_audit = run_data_quality_audit(df)
    model_reg = audit_model_registry()
    env_info = get_environment_info()
    snapshot = calculate_data_snapshot_info(df)

    ready_models = sum(1 for m in model_reg if "Ready" in m["Status"])
    is_operational = quality_audit["is_healthy"] and (ready_models == len(model_reg))

    data = {
        "status": "Operational 🟢" if is_operational else "Degraded 🟡",
        "app_name": env_info["app_name"],
        "version": env_info["app_version"],
        "environment": env_info["environment"],
        "data_quality_score": quality_audit["quality_score_pct"],
        "canonical_profiles": snapshot["rows"],
        "models_ready": f"{ready_models}/{len(model_reg)}",
    }
    return APIResponse(success=True, data=data)


@router.get("/audit-logs", response_model=APIResponse[List[dict]])
def get_audit_logs(
    limit: int = 50,
    current_user: UserContext = Depends(require_permission(Permission.VIEW_AUDIT_LOGS)),
):
    """Retrieve recent enterprise audit logs."""
    logs = get_recent_audit_events(limit=limit)
    return APIResponse(success=True, data=logs)
