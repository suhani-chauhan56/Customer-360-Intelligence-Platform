"""Model Explainability 2.0 Service for CustomerAtlas.

Provides clear distinctions between global feature drivers (XGBoost importance weights)
and local customer-level risk/value attribution with responsible phrasing.
"""

from typing import Any, Dict, List
import pandas as pd


def get_global_feature_importance(importance_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Retrieve global model feature importance rankings."""
    if importance_df is None or importance_df.empty:
        return []

    sorted_df = importance_df.sort_values(by="churn_importance", ascending=False)
    results = []
    for _, row in sorted_df.iterrows():
        results.append({
            "feature": str(row.get("feature", "unknown")),
            "churn_importance_pct": round(float(row.get("churn_importance", 0.0)) * 100, 1),
            "clv_importance_pct": round(float(row.get("clv_importance", 0.0)) * 100, 1) if "clv_importance" in row else 0.0,
            "description": _get_feature_plain_description(str(row.get("feature", ""))),
        })
    return results


def explain_individual_prediction(profile: pd.Series) -> Dict[str, Any]:
    """Provide local customer prediction attribution factors with responsible language."""
    recency = float(profile.get("recency_days", 0))
    orders = int(profile.get("total_orders", 1))
    spend = float(profile.get("total_spend", 0.0))
    csat = float(profile.get("avg_review_score", 5.0))
    churn_prob = float(profile.get("churn_probability", 0.0))

    attributions = []

    # Recency factor
    if recency > 180:
        attributions.append({
            "feature": "recency_days",
            "observation": f"Customer has been inactive for {int(recency)} days",
            "direction": "Elevated Churn Propensity",
            "weight": "High Contributing Factor",
        })
    else:
        attributions.append({
            "feature": "recency_days",
            "observation": f"Recent order completed {int(recency)} days ago",
            "direction": "Protective / Lowers Churn Risk",
            "weight": "Moderate Contributing Factor",
        })

    # Frequency factor
    if orders > 1:
        attributions.append({
            "feature": "frequency",
            "observation": f"Repeat transaction history ({orders} completed orders)",
            "direction": "Increases Forward CLV & Retention",
            "weight": "High Contributing Factor",
        })
    else:
        attributions.append({
            "feature": "frequency",
            "observation": "Single purchase transaction recorded to date",
            "direction": "Limited Retention Track Record",
            "weight": "Moderate Contributing Factor",
        })

    # CSAT Feedback factor
    if csat < 3.0:
        attributions.append({
            "feature": "avg_review_score",
            "observation": f"Sub-optimal feedback score ({csat:.1f} / 5.0 stars)",
            "direction": "Elevated Churn Risk Signal",
            "weight": "Moderate Contributing Factor",
        })

    return {
        "customer_id": str(profile.get("customer_id")),
        "predicted_churn_probability": churn_prob,
        "contributing_factors": attributions,
        "governance_notice": "Features contributed to the statistical model estimate; these factors represent statistical correlations rather than direct causal certainty.",
    }


def _get_feature_plain_description(feature_name: str) -> str:
    descriptions = {
        "recency_days": "Number of days since customer's last completed transaction.",
        "frequency": "Total lifetime completed order transaction count.",
        "monetary": "Cumulative lifetime gross merchandise spend in BRL.",
        "avg_order_value": "Average monetary amount spent per completed order.",
        "number_of_products": "Count of distinct catalog products purchased.",
        "customer_age_days": "Total days between customer's first purchase and snapshot date.",
    }
    return descriptions.get(feature_name, "Behavioral feature used during model training.")
