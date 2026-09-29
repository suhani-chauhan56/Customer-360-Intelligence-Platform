# CustomerAtlas Production Deployment Checklist

This document details the operational verification gates required prior to deploying **CustomerAtlas — Unified Customer Intelligence Platform** to Vercel, cloud serverless, or enterprise container environments.

---

## 1. Code Quality & Static Analysis
- [ ] Automated tests passing (`pytest tests/ -v`).
- [ ] Frontend build succeeds without errors (`npm run build:frontend`).
- [ ] Backend API endpoints verified (`node ...`).
- [ ] No local development paths hardcoded in application logic.
- [ ] No temporary debug `print()` statements or mock fixtures in production paths.
- [ ] All public service methods contain descriptive docstrings and type annotations.

## 2. Configuration & Secrets Management
- [ ] Environment variables configured (`NODE_ENV=production`, `LOG_LEVEL=INFO`).
- [ ] `.gitignore` verifies `.env` and `*.log` are ignored.
- [ ] No database credentials, API keys, or private tokens committed to git history.
- [ ] `vercel.json` configured for frontend static build and backend serverless API routing.

## 3. Data Pipeline & Schema Validation
- [ ] Primary feature store `data/processed/customer_360_features.csv` is present, complete, and uncorrupted.
- [ ] Dimension and fact tables (`fact_orders.csv`, `fact_payments.csv`, `recommendations.csv`) are accessible.
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
- [ ] All 11 primary product workspaces load cleanly:
  - *Executive Overview*
  - *Customer 360*
  - *Customer Segmentation*
  - *Customer Value (CLV)*
  - *Churn Intelligence*
  - *Sentiment Intelligence*
  - *Recommendations*
  - *Analytics Explorer*
  - *Data Quality & Governance*
  - *Methodology & Contracts*
  - *Ask CustomerAtlas (Grounded AI)*
- [ ] UI responsiveness verified across mobile, tablet, and desktop viewports.
- [ ] Chart tooltips and pagination work smoothly without console errors.
