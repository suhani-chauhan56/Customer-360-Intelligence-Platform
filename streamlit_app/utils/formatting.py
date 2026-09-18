"""Enterprise data formatting utilities for CustomerAtlas.

Provides presentation formatting for currencies, metrics, percentages,
and large numbers without modifying underlying numeric datasets.
"""

from typing import Union
import pandas as pd


def format_number(value: Union[int, float, None], decimals: int = 1) -> str:
    """Format large numbers into human-readable compact notation (e.g. 48.3K, 2.84M)."""
    if value is None or pd.isna(value):
        return "0"
    val = float(value)
    abs_val = abs(val)
    if abs_val >= 1_000_000_000:
        return f"{val / 1_000_000_000:.{decimals}f}B"
    if abs_val >= 1_000_000:
        return f"{val / 1_000_000:.{decimals}f}M"
    if abs_val >= 1_000:
        return f"{val / 1_000:.{decimals}f}K"
    if abs_val.is_integer():
        return f"{int(val):,}"
    return f"{val:,.{decimals}f}"


def format_currency(
    value: Union[int, float, None],
    symbol: str = "R$",
    decimals: int = 2,
    compact: bool = True,
) -> str:
    """Format currency values with standard currency symbols and optional compact notation."""
    if value is None or pd.isna(value):
        return f"{symbol} 0.00"
    val = float(value)
    abs_val = abs(val)

    if compact:
        if abs_val >= 1_000_000_000:
            return f"{symbol} {val / 1_000_000_000:.2f}B"
        if abs_val >= 1_000_000:
            return f"{symbol} {val / 1_000_000:.2f}M"
        if abs_val >= 10_000:
            return f"{symbol} {val / 1_000:.1f}K"

    return f"{symbol} {val:,.{decimals}f}"


def format_percent(value: Union[int, float, None], decimals: int = 1) -> str:
    """Format ratio/fraction to clean percentage string (e.g. 0.087 -> 8.7%)."""
    if value is None or pd.isna(value):
        return "0.0%"
    return f"{100.0 * float(value):.{decimals}f}%"


# Backwards compatibility helpers for existing codebase references
def format_brl(value: Union[int, float, None]) -> str:
    """Format Brazilian Real currency amounts."""
    if value is None or pd.isna(value):
        return "R$ 0"
    val = float(value)
    abs_val = abs(val)
    if abs_val >= 1_000_000:
        return f"R$ {val / 1_000_000:.2f}M"
    if abs_val >= 1_000:
        return f"R$ {val:,.0f}"
    return f"R$ {val:.2f}"


def format_pct(value: Union[int, float, None]) -> str:
    """Format percentage for existing dashboards."""
    return "0.0%" if pd.isna(value) else f"{100 * float(value):.1f}%"


def format_num(value: Union[int, float, None]) -> str:
    """Format standard number for existing dashboards."""
    if value is None or pd.isna(value):
        return "0"
    val = float(value)
    abs_val = abs(val)
    if abs_val >= 1_000_000:
        return f"{val / 1_000_000:.2f}M"
    if abs_val >= 1_000:
        return f"{val:,.0f}"
    return f"{val:.0f}"
