"""Domain business rules and playbook definitions for CustomerAtlas.

Encapsulates rule-based retention actions, segment descriptions, and priority
formulas to separate commercial logic from presentation code.
"""

from typing import Dict, Any


# Segment Metadata & Operational Focus
SEGMENT_RULES: Dict[str, Dict[str, Any]] = {
    "Champions": {
        "priority_level": "P0 - Protect & Advocate",
        "badge_color": "#16A34A",
        "description": "Top-tier customers with recent high-value purchases and frequent engagement.",
        "primary_objective": "VIP retention, exclusivity perks, and early-access cross-sell.",
    },
    "Loyal Customers": {
        "priority_level": "P1 - Value Maximization",
        "badge_color": "#0284C7",
        "description": "Dependable repeat purchasers who form the core revenue backbone.",
        "primary_objective": "Tiered rewards and category basket expansion.",
    },
    "Potential Loyalists": {
        "priority_level": "P2 - Nurture & Convert",
        "badge_color": "#8B5CF6",
        "description": "Recent buyers with solid initial spend who show potential for repeat conversion.",
        "primary_objective": "Automated post-purchase onboarding and second-order incentives.",
    },
    "Regular Customers": {
        "priority_level": "P3 - Baseline Growth",
        "badge_color": "#4F46E5",
        "description": "Moderate frequency and spending customers maintaining steady baseline demand.",
        "primary_objective": "Seasonal promotions and personalized category recommendations.",
    },
    "At Risk": {
        "priority_level": "P1 - Critical Win-Back",
        "badge_color": "#F59E0B",
        "description": "Valuable customers experiencing extended inactivity or delivery friction.",
        "primary_objective": "Targeted win-back campaigns and logistics satisfaction review.",
    },
    "Lost Customers": {
        "priority_level": "P4 - Selective Reactivation",
        "badge_color": "#DC2626",
        "description": "Longest inactive customers with lowest engagement and recency scores.",
        "primary_objective": "Low-touch clearance reactivations and churn root cause diagnosis.",
    },
}


# CLV Value Band Definitions
CLV_BAND_LABELS = {
    "Platinum": "Top 25% Forward Value (>= 75th percentile)",
    "Gold": "Upper Middle Value (50th - 75th percentile)",
    "Silver": "Lower Middle Value (25th - 50th percentile)",
    "Bronze": "Base Forward Value (< 25th percentile)",
}


# Actionable Retention Playbooks
def get_retention_playbook(probability: float, segment: str = "") -> Dict[str, str]:
    """Derive automated retention action according to calibrated churn probability and segment."""
    if probability >= 0.65:
        return {
            "tier": "Critical Priority",
            "badge_color": "#DC2626",
            "action": "Immediate VIP retention outreach. Audit fulfillment delay and deploy personalized win-back voucher.",
            "urgency": "High",
        }
    if probability >= 0.35:
        return {
            "tier": "Moderate Risk",
            "badge_color": "#F59E0B",
            "action": "Target with tailored category re-engagement campaign highlighting top-rated new arrivals.",
            "urgency": "Medium",
        }
    if segment in {"Champions", "Loyal Customers"}:
        return {
            "tier": "Advocate / Protect",
            "badge_color": "#16A34A",
            "action": "Reward loyalty with exclusive early-access perks and cross-sell premium complementary categories.",
            "urgency": "Growth",
        }
    return {
        "tier": "Standard Growth",
        "badge_color": "#4F46E5",
        "action": "Encourage second purchase journey with streamlined discovery and first-repeat free shipping incentive.",
        "urgency": "Standard",
    }
