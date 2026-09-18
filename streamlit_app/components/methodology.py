"""Transparent Methodology and Model Governance Panels for CustomerAtlas.

Provides expandable explanations of inputs, formulas, assumptions, and
limitations for RFM, CLV, Churn Risk, and Customer Prioritization.
"""

import streamlit as st


def render_methodology_panel(topic: str = "all") -> None:
    """Render transparent methodology documentation."""
    if topic in {"rfm", "all"}:
        with st.expander("ℹ️ How is RFM Segmentation Calculated?", expanded=False):
            st.markdown(
                """
                **RFM Analytical Framework:**
                - **Recency (R):** Number of days elapsed between the customer's last completed purchase and the snapshot date. Binned into quintiles (1 to 5, where 5 is most recent).
                - **Frequency (F):** Total number of distinct completed orders placed by the customer across their lifetime.
                - **Monetary (M):** Total cumulative gross spend (in BRL, R$) across all completed orders.
                
                **Audience Segment Assignment Rules:**
                - **Champions (R: 4-5, F: 4-5, M: 4-5):** Highest spending, most frequent, and recently active customers.
                - **Loyal Customers (F: 3-5, M: 3-5, R: 3-4):** Consistent repeat buyers with dependable order frequency.
                - **Potential Loyalists (R: 4-5, F: 1-2, M: 3-4):** Recent first-time or second-time buyers with above-average basket value.
                - **Regular Customers (R: 2-4, F: 1-2, M: 2-3):** Baseline customer population with standard order sizes.
                - **At Risk (R: 1-2, F: 2-5, M: 2-5):** Previously valuable customers who have not transacted in over 180 days.
                - **Lost Customers (R: 1, F: 1-2, M: 1-2):** Longest inactive cohort (>365 days inactive) with lowest engagement.
                
                *Note: Segment classifications are computed directly from actual customer transaction facts.*
                """
            )

    if topic in {"clv", "all"}:
        with st.expander("ℹ️ How is 12-Month Customer Lifetime Value (CLV) Estimated?", expanded=False):
            st.markdown(
                """
                **12-Month Forward CLV Model Architecture:**
                - **Algorithm:** Supervised XGBoost Regressor trained on historical customer transaction trajectories.
                - **Model Inputs:** Recency (days), Order Frequency, Cumulative Monetary Spend, Average Order Value (AOV), Distinct Products, and Customer Tenure Span.
                - **Target Definition:** Forward 12-month gross revenue proxy calibrated on longitudinal cohort intervals.
                - **Value Bands:**
                  - **Platinum Tier:** Top 25% predicted CLV (>= 75th percentile).
                  - **Gold Tier:** 50th to 75th percentile.
                  - **Silver Tier:** 25th to 50th percentile.
                  - **Bronze Tier:** Bottom 25% predicted CLV (< 25th percentile).
                
                *Limitation: CLV estimates reflect predictive forward proxies for audience prioritization and do not guarantee realized future transactions.*
                """
            )

    if topic in {"risk", "all"}:
        with st.expander("ℹ️ How is Churn Propensity & Customer Risk Determined?", expanded=False):
            st.markdown(
                """
                **Customer Churn Risk Methodology:**
                - **Algorithm:** XGBoost Gradient Boosted Classifier outputting calibrated class probabilities $[0.0, 1.0]$.
                - **Key Feature Drivers:** Inactivity duration (recency_days), purchase frequency drop-off, review rating history, and digital engagement.
                - **Classification Thresholds:**
                  - **Low Risk:** Propensity $< 35\%$ — Healthy customer with normal repeat cadence.
                  - **Medium Risk:** Propensity $35\% \le p < 65\%$ — Showing initial signs of purchase lapse.
                  - **High Risk / At-Risk:** Propensity $\ge 65\%$ — Significant inactivity or negative experience signal.
                
                *Data Contract: Olist transactions lack native subscription churn events. Risk scores represent calibrated inactivity propensities for portfolio retention playbooks.*
                """
            )

    if topic in {"priority", "all"}:
        with st.expander("ℹ️ How is the Customer Prioritization Score Calculated?", expanded=False):
            st.markdown(
                """
                **Customer Prioritization Formula:**
                $$\\text{Priority Score} = \\text{Churn Probability} \\times \\left( \\frac{\\text{Predicted 12M CLV}}{\\text{CLV}_{p99}} \\right) \\times 100$$
                
                - Combines **risk of loss** (Churn Probability) with **commercial value at stake** (Predicted CLV normalized against the 99th percentile).
                - A customer with high CLV and high churn risk receives the highest score (up to 100), ensuring retention teams focus limited outreach resources where commercial impact is greatest.
                """
            )
