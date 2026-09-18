"""Customer Health Scoring and Lifecycle State Machine Service for CustomerAtlas.

Implements a transparent, fully documented multi-factor Customer Health Score (0-100)
and a 6-stage operational lifecycle state machine based on measurable business facts.
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd
from utils.formatting import format_brl, format_pct


def calculate_customer_health_score(profile: pd.Series) -> Dict[str, Any]:
    """Calculate the transparent, 6-factor Customer Health Score (0-100).

    Formula:
        Health Score = 0.25 * Recency_Norm + 0.25 * Frequency_Norm + 0.25 * Monetary_Norm
                     + 0.15 * Engagement_Norm + 0.10 * CSAT_Norm - 0.20 * Risk_Penalty

        Where:
        - Recency_Norm (0-100): 100 * max(0, 1 - (recency_days / 365))
        - Frequency_Norm (0-100): min(100, orders * 33.3)
        - Monetary_Norm (0-100): min(100, (spend / 500.0) * 100)
        - Engagement_Norm (0-100): min(100, (web_engagement_score / 60.0) * 100)
        - CSAT_Norm (0-100): (avg_review_score / 5.0) * 100
        - Risk_Penalty (0-100): churn_probability * 100
    """
    recency_days = float(profile.get("recency_days", 300))
    orders = int(profile.get("total_orders", 1))
    spend = float(profile.get("total_spend", 0.0))
    web_score = float(profile.get("web_engagement_score", 0.0))
    csat = float(profile.get("avg_review_score", 5.0))
    churn_prob = float(profile.get("churn_probability", 0.5))

    # Normalized component scores (0 - 100)
    r_norm = max(0.0, min(100.0, 100.0 * (1.0 - (recency_days / 365.0))))
    f_norm = min(100.0, orders * 33.33)
    m_norm = min(100.0, (spend / 500.0) * 100.0)
    eng_norm = min(100.0, (web_score / 60.0) * 100.0)
    csat_norm = min(100.0, (csat / 5.0) * 100.0)
    risk_penalty = churn_prob * 100.0

    raw_score = (
        0.25 * r_norm
        + 0.25 * f_norm
        + 0.25 * m_norm
        + 0.15 * eng_norm
        + 0.10 * csat_norm
        - 0.20 * risk_penalty
    )

    final_score = round(float(np.clip(raw_score, 0.0, 100.0)), 1)

    if final_score >= 75.0:
        health_tier, color = "Thriving 🟢", "#16A34A"
    elif final_score >= 50.0:
        health_tier, color = "Healthy 🔵", "#0284C7"
    elif final_score >= 30.0:
        health_tier, color = "At Risk 🟡", "#F59E0B"
    else:
        health_tier, color = "Critical 🔴", "#DC2626"

    return {
        "score": final_score,
        "health_tier": health_tier,
        "badge_color": color,
        "components": {
            "Recency Vital": round(r_norm, 1),
            "Frequency Vital": round(f_norm, 1),
            "Monetary Vital": round(m_norm, 1),
            "Engagement Vital": round(eng_norm, 1),
            "CSAT Vital": round(csat_norm, 1),
            "Churn Risk Penalty": round(risk_penalty, 1),
        },
        "formula": "Score = 0.25*R + 0.25*F + 0.25*M + 0.15*Eng + 0.10*CSAT - 0.20*Risk",
    }


def classify_lifecycle_state(profile: pd.Series) -> Dict[str, Any]:
    """Classify customer into the 6-stage operational lifecycle state machine.

    Stages:
        1. New: Customer tenure <= 60 days and total orders == 1.
        2. Activated: Completed 1 order, recency <= 180 days, moderate engagement.
        3. Engaged: Total orders >= 2, recency <= 120 days.
        4. Loyal: Total orders >= 3 or RFM segment in {'Champions', 'Loyal Customers'}.
        5. At Risk: Recency > 180 days or churn probability >= 0.65.
        6. Inactive / Lost: Recency > 365 days and churn probability >= 0.65.
    """
    age_days = int(profile.get("customer_age_days", 1))
    recency = int(profile.get("recency_days", 0))
    orders = int(profile.get("total_orders", 1))
    churn_prob = float(profile.get("churn_probability", 0.0))
    rfm_seg = str(profile.get("rfm_segment", "Regular Customers"))

    if recency > 365 and churn_prob >= 0.65:
        state = "Inactive / Lost"
        description = "Longest lapsed customer with high inactivity; requires low-touch win-back."
        badge_color = "#DC2626"
    elif recency > 180 or churn_prob >= 0.65:
        state = "At Risk"
        description = "Previously active customer now exhibiting extended purchase lapse."
        badge_color = "#F59E0B"
    elif orders >= 3 or rfm_seg in {"Champions", "Loyal Customers"}:
        state = "Loyal"
        description = "Dependable repeat purchaser with strong lifetime engagement."
        badge_color = "#16A34A"
    elif orders >= 2 and recency <= 120:
        state = "Engaged"
        description = "Active repeat customer with consistent ongoing order velocity."
        badge_color = "#0284C7"
    elif age_days <= 60 and orders == 1:
        state = "New"
        description = "Recently acquired first-time buyer in initial onboarding window."
        badge_color = "#8B5CF6"
    else:
        state = "Activated"
        description = "Baseline customer who has completed initial transaction cycle."
        badge_color = "#4F46E5"

    return {
        "lifecycle_state": state,
        "description": description,
        "badge_color": badge_color,
        "orders": orders,
        "recency_days": recency,
    }
