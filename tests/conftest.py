"""Pytest configuration and shared fixtures for CustomerAtlas test suite."""

import sys
from pathlib import Path
import pandas as pd
import pytest

# Ensure root and streamlit_app are in Python path for test discovery
TEST_DIR = Path(__file__).resolve().parent
ROOT_DIR = TEST_DIR.parent
APP_DIR = ROOT_DIR / "streamlit_app"

for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)


@pytest.fixture
def sample_customer_df() -> pd.DataFrame:
    """Fixture providing a realistic multi-row customer feature store."""
    return pd.DataFrame([
        {
            "customer_id": "cust_001",
            "total_orders": 3,
            "total_spend": 1250.0,
            "total_freight": 45.0,
            "first_purchase_date": "2017-01-15 10:00:00",
            "last_purchase_date": "2018-05-10 12:00:00",
            "number_of_products": 4,
            "avg_order_value": 416.67,
            "recency_days": 35,
            "frequency": 3,
            "monetary": 1250.0,
            "customer_age_days": 480,
            "favorite_category": "health_beauty",
            "city": "sao paulo",
            "state": "SP",
            "sessions": 12.0,
            "views": 45.0,
            "cart_additions": 6.0,
            "web_engagement_score": 68.5,
            "avg_review_score": 4.8,
            "r_score": 5,
            "f_score": 4,
            "m_score": 5,
            "rfm_score": 545,
            "rfm_segment": "Champions",
            "cluster_segment": "High-Value Core",
            "churn_probability": 0.15,
            "predicted_clv": 850.0,
            "predicted_90d_revenue": 210.0,
            "churn_risk_band": "Low",
            "clv_band": "Platinum",
        },
        {
            "customer_id": "cust_002",
            "total_orders": 1,
            "total_spend": 89.90,
            "total_freight": 15.0,
            "first_purchase_date": "2017-06-20 14:30:00",
            "last_purchase_date": "2017-06-20 14:30:00",
            "number_of_products": 1,
            "avg_order_value": 89.90,
            "recency_days": 380,
            "frequency": 1,
            "monetary": 89.90,
            "customer_age_days": 1,
            "favorite_category": "bed_bath_table",
            "city": "rio de janeiro",
            "state": "RJ",
            "sessions": 2.0,
            "views": 4.0,
            "cart_additions": 1.0,
            "web_engagement_score": 14.2,
            "avg_review_score": 2.0,
            "r_score": 1,
            "f_score": 1,
            "m_score": 2,
            "rfm_score": 112,
            "rfm_segment": "Lost Customers",
            "cluster_segment": "Inactive Buyers",
            "churn_probability": 0.78,
            "predicted_clv": 45.0,
            "predicted_90d_revenue": 10.0,
            "churn_risk_band": "High",
            "clv_band": "Bronze",
        },
        {
            "customer_id": "cust_003",
            "total_orders": 2,
            "total_spend": 320.0,
            "total_freight": 30.0,
            "first_purchase_date": "2018-01-10 09:00:00",
            "last_purchase_date": "2018-03-25 18:00:00",
            "number_of_products": 2,
            "avg_order_value": 160.0,
            "recency_days": 110,
            "frequency": 2,
            "monetary": 320.0,
            "customer_age_days": 74,
            "favorite_category": "sports_leisure",
            "city": "belo horizonte",
            "state": "MG",
            "sessions": 6.0,
            "views": 18.0,
            "cart_additions": 3.0,
            "web_engagement_score": 38.0,
            "avg_review_score": 4.0,
            "r_score": 4,
            "f_score": 2,
            "m_score": 3,
            "rfm_score": 423,
            "rfm_segment": "Potential Loyalists",
            "cluster_segment": "Growth Potential",
            "churn_probability": 0.42,
            "predicted_clv": 240.0,
            "predicted_90d_revenue": 60.0,
            "churn_risk_band": "Medium",
            "clv_band": "Gold",
        },
    ])


@pytest.fixture
def empty_customer_df() -> pd.DataFrame:
    """Fixture providing an empty dataframe."""
    return pd.DataFrame()


@pytest.fixture
def single_customer_profile(sample_customer_df: pd.DataFrame) -> pd.Series:
    """Fixture providing a single customer record."""
    return sample_customer_df.iloc[0]
