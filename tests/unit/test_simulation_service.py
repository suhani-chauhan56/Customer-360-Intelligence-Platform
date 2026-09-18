"""Unit tests for What-If scenario simulation service."""

import pandas as pd
import pytest
from services.simulation_service import simulate_customer_value_shift


def test_simulate_customer_value_shift(single_customer_profile: pd.Series):
    sim = simulate_customer_value_shift(
        profile=single_customer_profile,
        additional_orders=2,
        aov_multiplier=1.2,
        recency_reduction_days=45,
    )
    assert "scenario_parameters" in sim
    assert "current_state" in sim
    assert "simulated_state" in sim
    assert "delta" in sim
    assert "disclaimer" in sim

    assert sim["simulated_state"]["total_orders"] == single_customer_profile["total_orders"] + 2
    assert sim["simulated_state"]["total_spend"] > single_customer_profile["total_spend"]
    assert sim["delta"]["clv_increase"] > 0
