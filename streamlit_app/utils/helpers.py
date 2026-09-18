"""General utility helpers and defensive data handling functions for CustomerAtlas."""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd


def safe_float(val: Any, default: float = 0.0) -> float:
    """Safely cast input to float without raising uncaught exceptions."""
    if val is None or pd.isna(val):
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def safe_int(val: Any, default: int = 0) -> int:
    """Safely cast input to int without raising uncaught exceptions."""
    if val is None or pd.isna(val):
        return default
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return default


def safe_str(val: Any, default: str = "") -> str:
    """Safely convert value to string, handling null/NaN cleanly."""
    if val is None or pd.isna(val):
        return default
    return str(val).strip()


def calculate_pareto_cutoff(series: pd.Series, top_pct: float = 0.20) -> float:
    """Calculate the value threshold separating the top X% of a numeric series."""
    if series is None or series.empty:
        return 0.0
    clean_series = series.dropna()
    if clean_series.empty:
        return 0.0
    return float(clean_series.quantile(1.0 - top_pct))


def calculate_data_snapshot_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute lightweight metadata for data snapshot auditing."""
    if df is None or df.empty:
        return {"rows": 0, "columns": 0, "memory_mb": 0.0, "has_records": False}
    
    mem_bytes = df.memory_usage(deep=True).sum()
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "memory_mb": round(mem_bytes / (1024 * 1024), 2),
        "has_records": True,
    }
