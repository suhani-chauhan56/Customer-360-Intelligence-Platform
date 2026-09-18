"""Integration tests verifying end-to-end analytics workflow."""

import pandas as pd
import pytest
from services.customer_service import (
    compute_customer_health,
    derive_lifecycle_stages,
    diagnose_customer_risk_factors,
    explain_rfm_segment,
    get_customer_profile,
    search_customers,
)
from services.data_service import build_customer_pdf
from services.rfm_service import compute_rfm_overview, compute_segment_distribution
from services.clv_service import compute_clv_overview, analyze_high_value_cohort
from services.risk_service import compute_risk_overview, calculate_customer_prioritization
from utils.validation import validate_customer_dataframe


def test_complete_customer_intelligence_flow(sample_customer_df: pd.DataFrame):
    # Step 1: Validate incoming dataset
    is_valid, issues = validate_customer_dataframe(sample_customer_df)
    assert is_valid is True

    # Step 2: Calculate Executive Benchmarks
    rfm_ov = compute_rfm_overview(sample_customer_df)
    clv_ov = compute_clv_overview(sample_customer_df)
    risk_ov = compute_risk_overview(sample_customer_df)
    assert rfm_ov["total_customers"] == len(sample_customer_df)
    assert clv_ov["total_pipeline_clv"] > 0
    assert risk_ov["total_customers"] == len(sample_customer_df)

    # Step 3: Search & Discover customer
    matched = search_customers(sample_customer_df, segment="Champions")
    assert not matched.empty
    cid = matched.iloc[0]["customer_id"]

    # Step 4: Open Customer 360 profile
    profile = get_customer_profile(sample_customer_df, cid)
    assert profile is not None

    # Step 5: Derive Profile Vitals, Lifecycle, Risk, and Segment Rationale
    health = compute_customer_health(profile)
    stages = derive_lifecycle_stages(profile)
    risk_diag = diagnose_customer_risk_factors(profile)
    rfm_diag = explain_rfm_segment(profile)

    assert len(health) == 6
    assert len(stages) == 5
    assert "risk_level" in risk_diag
    assert rfm_diag["segment"] == "Champions"

    # Step 6: Prioritization & High-Value Queue
    prio_queue = calculate_customer_prioritization(sample_customer_df)
    hv_cohort = analyze_high_value_cohort(sample_customer_df, percentile=0.50)
    assert not prio_queue.empty
    assert hv_cohort["count"] > 0

    # Step 7: Generate PDF Dossier
    pdf_bytes = build_customer_pdf(profile)
    assert len(pdf_bytes) > 100
    assert pdf_bytes.startswith(b"%PDF") or len(pdf_bytes) > 500
