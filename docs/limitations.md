# CustomerAtlas Limitations, Boundary Conditions & Technical Debt

This document provides transparent disclosure of architectural, algorithmic, data, and operational limitations across the CustomerAtlas platform.

---

## 1. Machine Learning & Predictive Modeling Limitations

### A. Non-Contractual Churn Labeling Delay
* **Constraint:** In non-contractual e-commerce, customers do not explicitly cancel a subscription; they silently stop purchasing.
* **Operational Impact:** Churn is defined by a business rule threshold (inactivity $\ge 180$ days). Ground truth labels cannot be confirmed until after the full 180-day observation window expires.
* **Production Governance:** Model performance metrics reflect offline historical holdout evaluations. Real-time production accuracy cannot be evaluated instantaneously without awaiting label maturity.

### B. Correlation vs. Causation in Explainable AI
* **Constraint:** Tree-based feature importance (XGBoost) and attribution models identify *correlations* between input features and model decisions.
* **Operational Impact:** An attribution score indicating that higher delivery time increased churn risk does **not** mathematically prove that reducing delivery time by 1 day will guarantee retention.
* **Governance Rule:** All UI and API responses strictly frame insights as *contributed to prediction* rather than *caused outcome*.

### C. Cold-Start Customer Handling
* **Constraint:** Customers with only 1 completed transaction have zero purchase interval history and limited behavioral signal.
* **Operational Impact:** Forward CLV and Churn predictions for new customers rely heavily on population baseline priors (first order value, category average, and geographic baseline).

---

## 2. What-If Scenario Simulation Boundaries

* **Constraint:** The What-If simulation engine applies linear and polynomial sensitivity adjustments based on model response curves.
* **Operational Impact:** Simulations assume *ceteris paribus* (all other variables held constant). In a live macroeconomic environment, customer reactions may exhibit feedback loops or competitive market shifts.
* **Governance Rule:** All simulated outputs are explicitly labeled as **Scenario / Simulation** with standard error confidence intervals, never as guaranteed revenue or retention outcomes.

---

## 3. Data Architecture & Scalability Inflection Points

| Dimension | Current Architecture (v2.0 Monolith) | Scalability Ceiling | Future Distributed Evolution |
| :--- | :--- | :--- | :--- |
| **Active Dataset** | 94,983 customer profiles (~50MB CSV/SQLite) | ~2,500,000 profiles in-memory | Partitioned PostgreSQL / Snowflake warehouse |
| **Transaction Rate** | Batch loaded / REST API synchronous CRUD | ~1,200 req/sec per Uvicorn worker | Asynchronous Kafka event ingest + Celery workers |
| **Session Cache** | `@st.cache_data` in local process memory | Single host RAM limit (16GB-64GB) | Distributed Redis cluster for feature cache |
| **Search Indexing** | Pandas column filtering & SQLite B-Tree | ~500,000 records (<50ms) | Elasticsearch / Meilisearch cluster |

---

## 4. Security, Multi-Tenancy & Authentication Boundaries

* **Current Implementation:** RBAC roles (`Admin`, `Analyst`, `Manager`, `Viewer`), constant-time API key verification, and tenant context isolation are implemented and enforced across all API endpoints.
* **Production Requirement for Enterprise SaaS:**
  - Connect OAuth2 / OpenID Connect (OIDC) with enterprise SSO (Okta, Azure AD, Google Workspace).
  - Deploy dynamic secrets management (e.g., HashiCorp Vault or AWS Secrets Manager) for database connection strings and JWT signing keys.
  - Implement per-tenant database schemas for strict multi-tenant data residency compliance (GDPR/HIPAA).
