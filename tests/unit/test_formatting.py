"""Unit tests for enterprise formatting utilities."""

import pytest
from utils.formatting import (
    format_brl,
    format_currency,
    format_num,
    format_number,
    format_pct,
    format_percent,
)


def test_format_number():
    assert format_number(1284) == "1.3K"
    assert format_number(48291) == "48.3K"
    assert format_number(2840000) == "2.8M"
    assert format_number(1500000000) == "1.5B"
    assert format_number(50) == "50"
    assert format_number(None) == "0"


def test_format_currency():
    assert format_currency(1250.50, symbol="R$", decimals=2, compact=False) == "R$ 1,250.50"
    assert "M" in format_currency(2840000, symbol="R$", compact=True)
    assert format_currency(None) == "R$ 0.00"


def test_format_percent():
    assert format_percent(0.087, decimals=1) == "8.7%"
    assert format_percent(0.5, decimals=0) == "50%"
    assert format_percent(1.0) == "100.0%"
    assert format_percent(None) == "0.0%"


def test_format_brl():
    assert format_brl(1250.0) == "R$ 1,250"
    assert format_brl(45.50) == "R$ 45.50"
    assert "M" in format_brl(3500000)
    assert format_brl(None) == "R$ 0"


def test_format_pct():
    assert format_pct(0.1234) == "12.3%"
    assert format_pct(0.0) == "0.0%"
    assert format_pct(None) == "0.0%"
