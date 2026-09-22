"""Formatting and defensive data helpers under src."""

from typing import Any, Union
import pandas as pd


def format_currency(value: Union[int, float, None], symbol: str = "R$") -> str:
    """Format numeric values into standard currency strings."""
    if value is None or pd.isna(value):
        return f"{symbol} 0.00"
    val = float(value)
    abs_val = abs(val)
    if abs_val >= 1_000_000:
        return f"{symbol} {val / 1_000_000:.2f}M"
    if abs_val >= 1_000:
        return f"{symbol} {val:,.0f}"
    return f"{symbol} {val:,.2f}"


def format_pct(value: Union[int, float, None], decimals: int = 1) -> str:
    """Format ratio into clean percentage string."""
    if value is None or pd.isna(value):
        return "0.0%"
    return f"{100.0 * float(value):.{decimals}f}%"
