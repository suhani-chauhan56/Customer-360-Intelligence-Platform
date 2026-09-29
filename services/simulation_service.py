"""What-If Analytical Scenario Simulation Service for CustomerAtlas.

Provides scenario modeling for hypothetical changes in purchase cadence,
order frequency, and basket sizes with explicit simulation disclaimers.
"""

from typing import Any, Dict
import pandas as pd
from utils.formatting import format_brl, format_pct


def simulate_customer_value_shift(
    profile: pd.Series,
    additional_orders: int = 1,
    aov_multiplier: float = 1.0,
    recency_reduction_days: int = 30,
) -> Dict[str, Any]:
    """Simulate the commercial impact of increased frequency, spend, or recency on customer trajectory.

    Note: This is an analytical simulation for strategic scenario planning, not a guaranteed realized outcome.
    """
    current_spend = float(profile.get("total_spend", 0.0))
    current_orders = int(profile.get("total_orders", 1))
    current_aov = float(profile.get("avg_order_value", 0.0))
    current_clv = float(profile.get("predicted_clv", 0.0))
    current_churn = float(profile.get("churn_probability", 0.5))

    # Simulated metrics
    sim_aov = current_aov * aov_multiplier
    sim_additional_spend = additional_orders * sim_aov
    sim_spend = current_spend + sim_additional_spend
    sim_orders = current_orders + additional_orders

    # Estimated forward CLV multiplier (elasticity proxy based on historical cohort progression)
    freq_elasticity = 0.35 * (additional_orders / max(1, current_orders))
    aov_elasticity = 0.25 * (aov_multiplier - 1.0)
    sim_clv = max(0.0, current_clv * (1.0 + freq_elasticity + aov_elasticity))

    # Churn probability reduction estimate from re-engagement
    churn_mitigation = min(0.30, 0.08 * additional_orders + (0.05 if recency_reduction_days > 0 else 0.0))
    sim_churn = max(0.05, current_churn - churn_mitigation)

    return {
        "scenario_parameters": {
            "additional_orders": additional_orders,
            "aov_multiplier": aov_multiplier,
            "recency_reduction_days": recency_reduction_days,
        },
        "current_state": {
            "total_spend": current_spend,
            "total_orders": current_orders,
            "avg_order_value": current_aov,
            "predicted_clv": current_clv,
            "churn_probability": current_churn,
        },
        "simulated_state": {
            "total_spend": sim_spend,
            "total_orders": sim_orders,
            "avg_order_value": sim_aov,
            "predicted_clv": sim_clv,
            "churn_probability": sim_churn,
        },
        "delta": {
            "spend_increase": sim_additional_spend,
            "clv_increase": sim_clv - current_clv,
            "clv_lift_pct": (sim_clv - current_clv) / max(1.0, current_clv),
            "churn_reduction_pct": current_churn - sim_churn,
        },
        "disclaimer": "Scenario simulation: Hypothetical estimation for decision modeling; does not guarantee realized future transactions.",
    }
