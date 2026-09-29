"""Operational and analytical threshold constants for CustomerAtlas.

Defines reproducible boundaries for churn risk bands, CLV percentiles,
recency intervals, and RFM scores without magic numbers.
"""

# Churn Risk Probability Thresholds
CHURN_THRESHOLD_LOW_MAX: float = 0.35
CHURN_THRESHOLD_HIGH_MIN: float = 0.65

# Recency Inactivity Thresholds (Days)
RECENCY_DAYS_RECENT: int = 60
RECENCY_DAYS_ACTIVE: int = 180
RECENCY_DAYS_LAPSED: int = 365

# Frequency Thresholds
FREQUENCY_REPEAT_MIN: int = 2
FREQUENCY_LOYAL_MIN: int = 3

# Monetary Spend Thresholds (BRL)
SPEND_TIER_HIGH: float = 500.0
SPEND_TIER_MODERATE: float = 150.0

# CLV Percentile Thresholds
CLV_P90_PERCENTILE: float = 0.90
CLV_P75_PERCENTILE: float = 0.75
CLV_P50_PERCENTILE: float = 0.50
CLV_P25_PERCENTILE: float = 0.25

# Value-Risk Quadrant Splits
QUADRANT_CHURN_SPLIT: float = 0.50

# Customer Health Score Weights & Scale
HEALTH_CSAT_POSITIVE_MIN: float = 4.0
HEALTH_CSAT_NEGATIVE_MAX: float = 2.5
HEALTH_WEB_ENGAGEMENT_HIGH: float = 40.0

# Pagination Defaults
DEFAULT_PAGE_SIZE: int = 25
PERMISSIBLE_PAGE_SIZES = [10, 25, 50, 100]
