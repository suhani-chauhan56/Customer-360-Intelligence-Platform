# CustomerAtlas Production Deployment Checklist

This document details the operational verification gates required prior to deploying **CustomerAtlas — Unified Customer Intelligence Platform** to staging, Streamlit Community Cloud, or enterprise production hosting.

---

## 1. Code Quality & Static Analysis
- [ ] Automated tests passing (`pytest tests/ -v`).
- [ ] Code formatted and linted without critical errors (`ruff check streamlit_app tests`).
- [ ] No local development paths (`C:\Users\...` or `/Users/...`) hardcoded in application logic.
- [ ] No temporary debug `print()` statements or mock fixtures in production paths.
- [ ] All public service methods contain descriptive docstrings and type annotations.

## 2. Configuration & Secrets Management
- [ ] Environment variables configured (`APP_ENV=production`, `LOG_LEVEL=INFO`, `CACHE_TTL_SECONDS=3600`).
- [ ] `.gitignore` verifies `.env`, `.streamlit/secrets.toml`, and `*.log` are ignored.
- [ ] No database credentials, API keys, or private tokens committed to git history.
- [ ] `.streamlit/config.toml` has `gatherUsageStats = false` and `headless = true`.

## 3. Data Pipeline & Schema Validation
- [ ] Primary feature store `data/processed/customer_360_features.csv` is present, complete, and uncorrupted.
- [ ] Dimension and fact tables (`fact_orders.csv`, `fact_payments.csv`, `dim_product.csv`, `recommendations.csv`, `segment_summary.csv`) are accessible.
- [ ] Schema validation checks pass for all required columns, non-null customer IDs, and non-negative revenue.
- [ ] Empty state, missing profile, and filter edge cases fail gracefully with user-friendly messages.

## 4. Machine Learning Artifacts & Governance
- [ ] Serialized model artifacts exist in `models/`:
  - `churn_model.pkl` (XGBoost Churn Classifier)
  - `clv_model.pkl` (XGBoost 12-Month CLV Regressor)
  - `segment_model.pkl` (K-Means Behavioral Cluster Pipeline)
  - `sentiment_model.pkl` (TF-IDF + Logistic Review Classifier)
- [ ] JSON metadata files in `models/metadata/` reflect model provenance and evaluation benchmarks.
- [ ] Feature input order strictly matches the model contract (`recency_days`, `frequency`, `monetary`, `avg_order_value`, `number_of_products`, `customer_age_days`).
- [ ] Fallback handling is active if a model artifact is missing or corrupt.

## 5. Presentation Layer & UX Flow
- [ ] All 8 primary product workspaces load cleanly:
  - *Executive Overview*
  - *Customer 360*
  - *Customer Explorer*
  - *Segmentation*
  - *RFM Analysis*
  - *Customer Lifetime Value*
  - *Churn & Risk*
  - *Customer Insights*
- [ ] 1-click customer transition from *Explorer*, *Prioritization Queue*, and *High-Value tables* into *Customer 360* works via session state.
- [ ] PDF dossier generation and CSV data exports function reliably.
- [ ] Responsive UI layouts maintain alignment on desktop, laptop, and tablet viewports.
