"""Recommendation Domain Service for CustomerAtlas.

Provides explainable Next-Best-Category recommendations, basket association
rules, and catalog affinity analytics.
"""

from typing import Any, Dict, List, Optional
import pandas as pd


def get_customer_recommendations(
    recommendations_df: pd.DataFrame,
    customer_id: str,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """Retrieve ranked explainable product category recommendations for a customer."""
    if recommendations_df is None or recommendations_df.empty or not customer_id:
        return []

    matches = recommendations_df[recommendations_df["customer_id"].astype(str) == str(customer_id)]
    if matches.empty:
        return []

    sorted_recs = matches.sort_values("rank").head(top_n)
    results = []
    for _, row in sorted_recs.iterrows():
        results.append({
            "rank": int(row.get("rank", 1)),
            "recommended_category": str(row.get("recommended_category", "General")),
            "reason": str(row.get("reason", "Affinity based on purchase history.")),
            "method": str(row.get("method", "Basket Co-occurrence")),
        })
    return results


def summarize_recommendation_methods(recommendations_df: pd.DataFrame) -> pd.DataFrame:
    """Summarize the distribution of recommendation methodologies."""
    if recommendations_df is None or recommendations_df.empty or "method" not in recommendations_df.columns:
        return pd.DataFrame()

    counts = recommendations_df["method"].value_counts().reset_index()
    counts.columns = ["Recommendation Method", "Volume"]
    return counts
