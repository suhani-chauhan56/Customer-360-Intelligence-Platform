"""Data and Prediction Drift Monitoring Service for CustomerAtlas MLOps.

Implements Population Stability Index (PSI) and distribution drift monitoring
between baseline training distributions and active customer populations.
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd


def calculate_psi(baseline: pd.Series, target: pd.Series, num_buckets: int = 10) -> float:
    """Calculate Population Stability Index (PSI) between baseline and target distributions.

    Interpretation:
        - PSI < 0.10: Stable (No significant distribution shift)
        - 0.10 <= PSI < 0.25: Moderate Shift (Monitor closely)
        - PSI >= 0.25: Significant Drift (Actionable investigation required)
    """
    b_clean = baseline.dropna()
    t_clean = target.dropna()

    if b_clean.empty or t_clean.empty or b_clean.nunique() <= 1:
        return 0.0

    # Quantile bin edges based on baseline
    percentiles = np.linspace(0, 100, num_buckets + 1)
    bin_edges = np.percentile(b_clean, percentiles)
    bin_edges = np.unique(bin_edges)  # Remove non-unique bin edges

    if len(bin_edges) < 2:
        return 0.0

    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    b_counts, _ = np.histogram(b_clean, bins=bin_edges)
    t_counts, _ = np.histogram(t_clean, bins=bin_edges)

    # Normalize proportions with Laplace smoothing epsilon
    eps = 1e-4
    b_prop = (b_counts / max(1, len(b_clean))) + eps
    t_prop = (t_counts / max(1, len(t_clean))) + eps

    b_prop = b_prop / b_prop.sum()
    t_prop = t_prop / t_prop.sum()

    psi_val = np.sum((t_prop - b_prop) * np.log(t_prop / b_prop))
    return float(round(max(0.0, psi_val), 4))


def run_feature_drift_audit(
    baseline_df: pd.DataFrame,
    current_df: pd.DataFrame,
    monitored_features: List[str] = None,
) -> Dict[str, Any]:
    """Run comprehensive drift analysis across critical ML and behavioral features."""
    if monitored_features is None:
        monitored_features = [
            "recency_days",
            "frequency",
            "monetary",
            "avg_order_value",
            "predicted_clv",
            "churn_probability",
        ]

    drift_report = []
    overall_drift_detected = False

    for feat in monitored_features:
        if feat in baseline_df.columns and feat in current_df.columns:
            psi = calculate_psi(baseline_df[feat], current_df[feat])
            
            if psi >= 0.25:
                status, badge = "Significant Drift 🔴", "Action Required"
                overall_drift_detected = True
            elif psi >= 0.10:
                status, badge = "Moderate Shift 🟡", "Monitor"
            else:
                status, badge = "Stable 🟢", "Normal"

            drift_report.append({
                "Feature": feat,
                "PSI Score": psi,
                "Status": status,
                "Alert Tier": badge,
                "Baseline Mean": round(float(baseline_df[feat].mean()), 2),
                "Current Mean": round(float(current_df[feat].mean()), 2),
                "Baseline Std": round(float(baseline_df[feat].std()), 2),
                "Current Std": round(float(current_df[feat].std()), 2),
            })

    return {
        "overall_status": "Drift Alert Triggered ⚠️" if overall_drift_detected else "Distributions Stable 🟢",
        "monitored_features_count": len(drift_report),
        "drift_detected": overall_drift_detected,
        "features": drift_report,
        "governance_policy": "Drift values >= 0.25 trigger review & human audit before any scheduled model retraining.",
    }
