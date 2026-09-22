"""Unit tests for What-If Scenario Simulation Service in CustomerAtlas."""

import pandas as pd
import pytest
from services.simulation_service import simulate_customer_value_shift


def test_simulate_customer_value_shift(single_customer_profile: pd.Series):
    res = simulate_customer_value_shift(
        profile=single_customer_profile,
        additional_orders=2,
        aov_multiplier=1.2,
        recency_reduction_days=30,
    )
    assert "current_state" in res
    assert "simulated_state" in res
    assert "delta" in res
    assert res["simulated_state"]["total_orders"] == res["current_state"]["total_orders"] + 2
    assert res["simulated_state"]["total_spend"] > res["current_state"]["total_spend"]
    assert res["delta"]["spend_increase"] > 0
    assert "disclaimer" in res
