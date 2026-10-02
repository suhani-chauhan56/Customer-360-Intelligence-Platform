# CustomerAtlas AI — Enterprise Customer 360 Intelligence Platform

> Unified Customer Intelligence, Predictive Churn Modeling, 12-Month CLV Forecasting, and Grounded Decision Support System.

---

## 1. Project Overview

### Problem Statement
Modern e-commerce and retail businesses operate across fragmented data silos: transaction ledgers, payment gateways, customer review forums, and digital web engagement logs. Without a unified analytical framework, commercial teams struggle with:
- **Blind Retention:** Inability to pinpoint high-value accounts at imminent risk of churning.
- **Single-Purchase Drop-Off:** Failure to convert first-time buyers into dependable repeat purchasers.
- **Generic Marketing:** Lack of granular RFM segmentation and personalized next-best-action guidance.
- **Data Governance Gaps:** Inability to detect population drift (PSI) or verify feature integrity before decisions are made.

### Purpose and Objective
**CustomerAtlas AI** was developed to bridge the gap between rigorous data science modeling and enterprise commercial operations. It transforms 94,983 unified customer records into actionable business intelligence through:
1. Multi-dimensional RFM quintile segmentation and strategic playbooks.
2. Machine learning-driven 12-month forward Customer Lifetime Value (CLV) regression.
3. Calibrated XGBoost churn propensity modeling and revenue-at-risk prioritization.
4. Voice of Customer (VoC) Portuguese sentiment theme extraction and CSAT tracking.
5. Deterministic, hallucination-free decision support with full data lineage and drift monitoring.

---

## 2. Key Features

- **Executive Intelligence Dashboard:** Real-time macro GMV, active buyer rates, AOV, repeat purchase metrics, and dynamic Pareto revenue concentration analysis.
- **Customer 360 Unified Dossier:** Individual 360° dossiers across 94,983 profiles with 6-Factor Vital Health Scoring ($0-100$), 6-stage lifecycle state machine, chronological order timeline, and payment breakdown.
- **RFM Segmentation Engine:** 6 canonical cohorts (*Champions*, *Loyal*, *Potential Loyalists*, *Regular*, *At Risk*, *Lost*), 5x5 heatmap comparisons, and targeted cohort builder with CSV export.
- **12-Month Predictive CLV Engine:** Dynamic value tier banding (*Platinum*, *Gold*, *Silver*, *Bronze*), top decile concentration analysis, and interactive what-if revenue simulator.
- **Churn Intelligence & Risk Exposure:** Revenue exposure quantification, 4-quadrant value-risk matrix, XGBoost feature drivers, and prioritized retention queue:
  $$\text{Priority Score} = \text{Churn Probability} \times \left(\frac{\text{Predicted CLV}}{\text{CLV}_{p99}}\right) \times 100$$
- **Sentiment & CSAT Intelligence:** Macro CSAT rating ($4.1/5.0$), longitudinal monthly trends, segment ratings, and Portuguese keyword root-cause extraction for logistics friction.
- **Multi-Signal Action Engine:** Transparent 7-rule decision engine translating risk, value, recency, and CSAT signals into immediate commercial retention and upsell workflows.
- **Analytics Explorer:** Multi-criteria slice-and-dice discovery across recency windows, spend brackets, geographic states, and risk tiers with live distribution histograms.
- **Data Quality & MLOps Governance:** Automated schema validation, field null completeness audit, raw-to-processed data lineage, and Population Stability Index (PSI) feature drift monitoring.
- **Ask CustomerAtlas AI:** Deterministic, mathematically grounded conversational AI providing direct answers backed by verified profile records with zero hallucinations.

---

## 3. Data & Dataset

The platform is engineered on verified multi-source transaction and customer feedback records:

| Dataset / Table | Records / Scale | Description | Key Attributes |
| :--- | :--- | :--- | :--- |
| **`customer_360_features.csv`** | 94,983 Profiles | Canonical entity feature store | `customer_id`, `total_spend`, `total_orders`, `avg_order_value`, `recency_days`, `frequency`, `monetary`, `rfm_segment`, `churn_probability`, `predicted_clv`, `priority_score`, `state`, `city`, `favorite_category` |
| **`fact_orders.csv`** | 99,441 Transactions | Transaction purchase ledger | `order_id`, `customer_id`, `purchase_date`, `order_status`, `item_price`, `freight_value`, `revenue`, `month_year` |
| **`fact_payments.csv`** | 103,886 Payments | Payment method breakdown | `order_id`, `payment_type`, `payment_installments`, `payment_value` |
| **`olist_order_reviews_dataset.csv`** | 104,721 Reviews | Voice of Customer feedback | `review_id`, `order_id`, `review_score`, `review_comment_message`, `review_creation_date` |
| **`recommendations.csv`** | 474,917 Associations | Market basket recommendations | `customer_id`, `rank`, `recommended_category`, `method`, `reason` |
| **`model_feature_importance.csv`** | 6 Features | Global model feature drivers | `feature`, `churn_importance`, `clv_importance` |

---

## 4. Data Analytics & Data Science Workflow

```
[Raw Ingestion] ──────> [Data Cleaning] ──────> [Feature Engineering] ──────> [ML Modeling]
 ├─ Orders Ledgers       ├─ Deduplication        ├─ RFM Quintile Scoring       ├─ XGBoost Churn
 ├─ Payments Data        ├─ Type Enforcement     ├─ Digital Web Scores         ├─ Ridge CLV Regressor
 └─ Review Texts         └─ Null Imputation      └─ Inactivity Windows         └─ TF-IDF CSAT
                                                                                     │
                                                                                     ▼
[Action Engine] <────── [Executive Insights] <─── [Entity Store] <──────── [Health Scoring]
 ├─ Win-Back Flows       ├─ Pareto Concentration   ├─ MongoDB Database          ├─ 6-Factor Vital Signs
 ├─ VIP Concierge        ├─ Single-Order Bottleneck└─ In-Memory Cache           └─ Lifecycle State Machine
 └─ CSV Export Queue     └─ Geographic Clusters
```

1. **Data Collection & Ingestion:** Ingest raw multi-table transaction facts, review ledgers, and catalog categories.
2. **Data Cleaning & Sanity Checking:** Filter canceled/unavailable orders, eliminate orphan foreign keys, enforce non-negative monetary constraints, and calibrate probabilities to $[0.0, 1.0]$.
3. **Feature Engineering:** Calculate days since last purchase (`recency_days`), total transaction count (`frequency`), gross monetary value (`monetary`), average order value (`avg_order_value`), and review sentiment scores.
4. **Exploratory Data Analysis (EDA):** Analyze spend distributions, inactivity intervals, category affinities, and geographic demand concentrations.
5. **Machine Learning & Predictive Modeling:**
   - Supervised XGBoost Classifier for churn probability estimation.
   - Ridge / XGBoost Regressor for forward 12-month CLV expectation.
   - Market basket co-occurrence modeling for Next-Best-Category cross-sell.
6. **Health Scoring & Lifecycle State Machine:** Synthesize vital signs into a single composite score ($0-100$) and track accounts across 6 lifecycle milestones.
7. **Actionable Business Recommendations:** Apply multi-signal commercial rules to generate prioritized win-back, loyalty, and recovery tasks.
8. **MLOps Drift Monitoring:** Monitor distribution stability using Population Stability Index (PSI) between baseline and active cohorts.

---

## 5. Technical Architecture

```mermaid
flowchart TD
    subgraph Client_Layer ["Frontend SPA Layer (React 18 + Vite + Tailwind)"]
        SPA["React 18 Single Page Application"]
        ROUTER["React Router v6 (11 Dedicated Workspaces)"]
        CHARTS["Recharts (Bar, Line, Area, Pie, Gauge)"]
        API_CLIENT["Axios REST Client (/api)"]
        SPA --> ROUTER
        ROUTER --> CHARTS
        ROUTER --> API_CLIENT
    end

    subgraph Server_Layer ["Backend API Engine (Node.js + Express)"]
        SRV["Express REST Router"]
        CTRL["10 Domain Controllers\n(Analytics, Churn, CLV, Customers, Quality, AI, etc.)"]
        SRV --> CTRL
    end

    subgraph Service_Layer ["Domain Calculation Services"]
        CUST_SVC["Customer 360 & Health Scoring"]
        RFM_SVC["RFM Intelligence & Segmentation"]
        CLV_SVC["12-Month Predictive CLV Engine"]
        CHURN_SVC["Churn Propensity & Risk Exposure"]
        SENT_SVC["CSAT Sentiment & Theme Extraction"]
        REC_SVC["7-Rule Decision Recommendation Engine"]
        DRIFT_SVC["PSI Feature Drift Monitoring"]
        AI_SVC["Deterministic Grounded AI Router"]
        CTRL --> Service_Layer
    end

    subgraph Persistence_Layer ["Data & Feature Store"]
        MEM_STORE[("In-Memory Canonical Feature Cache (94,983 Profiles)")]
        MONGO[("MongoDB Database (Compound Indexes)")]
        Service_Layer --> MEM_STORE
        Service_Layer -.-> MONGO
    end

    API_CLIENT -->|REST HTTP / JSON| SRV
```

### Technology Stack
- **Frontend:** React 18.3, Vite 5.4, Tailwind CSS 3.4, Recharts 2.12, Lucide React, Axios, React Router DOM 6.23.
- **Backend:** Node.js 18+, Express.js 4.19, Mongoose 8.4 / MongoDB (with graceful in-memory CSV cache fallback), CSV-Parser, Cors, Dotenv.
- **Data Science & ML:** Python 3.11+, Pandas 2.2, NumPy 1.26, Scikit-learn 1.4, XGBoost 2.0, Joblib, `analytics.py`.
- **Deployment:** Vercel Serverless Function bridge (`api/index.js`) + static CDN distribution (`vercel.json`).

---

## 6. Mathematical Formulations & Data Science Logic

### A. 6-Factor Customer Health Score ($0-100$)
$$\text{Health Score} = \left(0.25 R_{\text{norm}} + 0.25 F_{\text{norm}} + 0.25 M_{\text{norm}} + 0.15 \text{Eng}_{\text{norm}} + 0.10 \text{CSAT}_{\text{norm}} - 0.20 \text{Risk}\right) \times 100$$
- $R_{\text{norm}} = \max\left(0, 1 - \frac{\text{Recency Days}}{365}\right)$
- $F_{\text{norm}} = \min\left(1, \frac{\text{Frequency}}{5}\right)$
- $M_{\text{norm}} = \min\left(1, \frac{\text{Spend}}{1000}\right)$
- $\text{Eng}_{\text{norm}} = \min\left(1, \frac{\text{Orders}}{3}\right)$
- $\text{CSAT}_{\text{norm}} = \frac{\text{CSAT Score}}{5.0}$
- $\text{Risk} = \text{Churn Probability}$

### B. Population Stability Index (PSI) Feature Drift
$$\text{PSI} = \sum_{i=1}^{k} \left(T_i - B_i\right) \times \ln\left(\frac{T_i}{B_i}\right)$$
- $\text{PSI} < 0.10$: Stable / No Action Required.
- $0.10 \le \text{PSI} < 0.25$: Moderate Drift / Flag for Monitoring.
- $\text{PSI} \ge 0.25$: Significant Drift / Action Required before Retraining.

---

## 7. REST API Reference

The backend exposes fully documented RESTful JSON endpoints under `/api`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/dashboard` | Executive KPIs, monthly trajectory, geographic breakdown, and automated Pareto insights. |
| `GET` | `/api/customers` | Paginated customer list with sorting and multi-field filters (`page`, `limit`, `segment`, `risk`, `state`, `search`). |
| `GET` | `/api/customers/:id` | Full Customer 360 profile, health score breakdown, orders, payments, timeline, and risk diagnostics. |
| `GET` | `/api/customers/:id/dossier` | Complete dossier export metadata for immediate JSON/PDF download. |
| `GET` | `/api/rfm` | RFM segment distributions, size shares, revenue shares, and benchmark averages. |
| `GET` | `/api/rfm/:segment` | Granular drill-down metrics, top customer records, and strategic playbook for a segment. |
| `GET` | `/api/rfm/compare` | Side-by-side comparative analysis of two chosen segments across 8 commercial dimensions. |
| `POST` | `/api/rfm/cohort` | Targeted marketing cohort builder matching segments, spend thresholds, and risk bounds. |
| `GET` | `/api/clv` | CLV overview benchmarks, dynamic value tier brackets, and top 10% high-value cohort analysis. |
| `POST` | `/api/clv/simulate` | Forward 12-month CLV expectation simulator based on RFM and engagement inputs. |
| `GET` | `/api/churn` | Churn overview, revenue exposure, 4-quadrant value-risk matrix, and priority queue. |
| `POST` | `/api/churn/simulate` | Real-time churn propensity calculator with automated playbook recommendation. |
| `GET` | `/api/sentiment` | CSAT overview, star distribution, longitudinal trend, segment ratings, and negative themes. |
| `GET` | `/api/sentiment/reviews` | Review explorer with star rating filters and written comment filtering. |
| `GET` | `/api/recommendations` | Next-Best-Action recommendations overview, rule distribution, and actionable queue. |
| `GET` | `/api/recommendations/customer/:id` | Market basket category recommendations for a specific customer ID. |
| `GET` | `/api/analytics/explorer` | Multi-criteria sliced explorer with histograms and paginated cohort table. |
| `GET` | `/api/analytics/export` | Downloadable CSV export generator for filtered customer cohorts. |
| `GET` | `/api/data-quality` | Data completeness audit, schema test suite, data lineage, and PSI drift monitoring. |
| `POST` | `/api/data-quality/audit` | Record compliance and operational audit events. |
| `POST` | `/api/grounded-ai/ask` | Deterministic natural-language decision support with verified data grounding. |

---

## 8. Business Insights & Practical Outcomes

1. **Pareto Revenue Concentration:** Identifies that top spenders contribute disproportionate gross merchandise value, enabling commercial leaders to deploy dedicated VIP concierge perks to safeguard the revenue foundation.
2. **Single-Purchase Drop-Off Bottleneck:** Highlights that approximately 97% of customer relationships conclude after a single order, proving that an automated 14-day post-purchase replenishment workflow is the highest-leverage growth driver.
3. **Revenue at Risk Defense:** Isolates accounts with high historical spend exhibiting elevated churn probabilities ($\ge 65\%$), queuing them into high-touch win-back workflows before complete account attrition.
4. **Logistics Satisfaction Feedback:** Extracts specific Portuguese review feedback themes (e.g., delivery delays, missing items) to prioritize carrier SLA audits and warehouse dispatch verification.
5. **Geographic Demand Allocation:** Reveals top state concentrations (e.g., São Paulo leading demand) to optimize regional logistics, fulfillment routing, and localized promotional campaigns.

---

## 9. Project Structure

```
Customer 360 Intelligence/
├── api/
│   └── index.js                      # Vercel Serverless Function Bridge
├── backend/
│   ├── config/
│   │   └── db.js                     # MongoDB connection with in-memory fallback
│   ├── controllers/                  # 10 REST API Controllers
│   │   ├── analyticsController.js
│   │   ├── churnController.js
│   │   ├── clvController.js
│   │   ├── customerController.js
│   │   ├── dashboardController.js
│   │   ├── dataQualityController.js
│   │   ├── groundedAiController.js
│   │   ├── recommendationController.js
│   │   ├── rfmController.js
│   │   └── sentimentController.js
│   ├── middleware/
│   │   └── errorHandler.js           # Centralized JSON error handler
│   ├── models/                       # Mongoose Schemas & Indexes
│   │   ├── AuditEvent.js
│   │   └── Customer.js
│   ├── routes/                       # Express REST Route Handlers
│   │   ├── analyticsRoutes.js
│   │   ├── api.js                    # Master API router
│   │   ├── churnRoutes.js
│   │   ├── clvRoutes.js
│   │   ├── customerRoutes.js
│   │   ├── dashboardRoutes.js
│   │   ├── dataQualityRoutes.js
│   │   ├── groundedAiRoutes.js
│   │   ├── recommendationRoutes.js
│   │   ├── rfmRoutes.js
│   │   └── sentimentRoutes.js
│   ├── scripts/
│   │   └── seedDatabase.js           # Optional MongoDB batch seed script
│   ├── services/                     # Core Domain Calculation Engines
│   │   ├── analyticsService.js
│   │   ├── auditService.js
│   │   ├── churnService.js
│   │   ├── clvService.js
│   │   ├── customerService.js
│   │   ├── dataQualityService.js
│   │   ├── dataService.js            # In-memory CSV cache & streaming reader
│   │   ├── driftService.js           # PSI calculation engine
│   │   ├── groundedAiService.js      # Semantic routing & data grounding
│   │   ├── recommendationService.js
│   │   ├── rfmService.js
│   │   └── sentimentService.js
│   ├── package.json
│   └── server.js                     # Backend Express server entrypoint
├── data/
│   ├── processed/
│   │   ├── customer_360_features.csv # Canonical dataset (94,983 profiles)
│   │   ├── fact_orders.csv           # Transaction records (99,441 orders)
│   │   ├── fact_payments.csv         # Payment methods & installments
│   │   ├── model_feature_importance.csv # XGBoost feature weights
│   │   └── recommendations.csv       # Market basket cross-sell rules
│   └── raw/
│       └── olist_order_reviews_dataset.csv # Voice of Customer reviews
├── frontend/
│   ├── src/
│   │   ├── components/               # Reusable UI & Chart components
│   │   │   ├── charts/               # Recharts wrappers (Bar, Line, Pie, Gauge)
│   │   │   ├── common/               # KpiCard, InsightCard, CustomerTable, Badge
│   │   │   ├── customer/             # HealthGrid, LifecycleJourney, RiskDiagnostics, Timeline
│   │   │   └── layouts/              # Navbar, Sidebar, Footer, AppLayout
│   │   ├── pages/                    # 11 Dedicated Workspace Pages
│   │   │   ├── AnalyticsExplorer.jsx
│   │   │   ├── AskAtlas.jsx
│   │   │   ├── ChurnIntelligence.jsx
│   │   │   ├── Customer360.jsx
│   │   │   ├── CustomerSegmentation.jsx
│   │   │   ├── CustomerValue.jsx
│   │   │   ├── DataQuality.jsx
│   │   │   ├── ExecutiveOverview.jsx
│   │   │   ├── Methodology.jsx
│   │   │   ├── Recommendations.jsx
│   │   │   └── SentimentIntelligence.jsx
│   │   ├── services/
│   │   │   └── api.js                # Axios REST API Client
│   │   ├── utils/
│   │   │   └── formatting.js         # Currency, percentage, count formatters
│   │   ├── App.jsx                   # Master Router & Route Declarations
│   │   ├── index.css                 # Tailwind CSS styles
│   │   └── main.jsx                  # React DOM Entrypoint
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
├── models/                           # Serialized ML Model Artifacts
│   ├── churn_model.pkl
│   ├── clv_model.pkl
│   ├── scaler.pkl
│   └── sentiment_model.pkl
├── src/                              # Python Data Science Utilities
│   ├── data_loader.py
│   └── preprocessing.py
├── analytics.py                      # Standalone Python Analytics Pipeline
├── requirements.txt                  # Python Data Science Dependencies
├── package.json                      # Root NPM Orchestration Script
├── vercel.json                       # Vercel Production Deployment Config
└── .env.example                      # Environment Configuration Template
```

---

## 10. Getting Started & Local Setup

### Prerequisites
- **Node.js**: Version `18.x` or higher
- **npm**: Version `9.x` or higher
- *(Optional)* **Python**: `3.11+` for running offline data science pipelines in `analytics.py`
- *(Optional)* **MongoDB**: Local MongoDB instance or MongoDB Atlas connection string (if omitted, the platform runs seamlessly using its fast in-memory CSV cache)

### Step 1: Clone Repository & Configure Environment
```bash
git clone https://github.com/suhani-chauhan56/Customer-360-Intelligence-Platform.git
cd Customer-360-Intelligence-Platform

# Copy environment variables template
cp .env.example .env
```

### Step 2: Install Dependencies
```bash
# Install root orchestration packages
npm install

# Install backend dependencies
cd backend && npm install && cd ..

# Install frontend dependencies
cd frontend && npm install && cd ..
```

### Step 3: Run the Full-Stack Application
Start both backend API and frontend dev server concurrently:
```bash
npm run dev
```

Or run each service individually in separate terminals:
```bash
# Terminal 1 — Backend API (starts on http://localhost:5000)
npm run dev:backend

# Terminal 2 — Frontend UI (starts on http://localhost:3000)
npm run dev:frontend
```

Open your browser at `http://localhost:3000` to interact with the platform.

### Step 4 (Optional): Run Standalone Python Analytics Pipeline
```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install data science dependencies
pip install -r requirements.txt

# Execute analytics audit
python analytics.py
```

### Step 5 (Optional): Seed MongoDB Instance
If you have configured a `MONGODB_URI` in `.env` and want to populate MongoDB collections:
```bash
npm run db:seed
```

---

## 11. Environment Variables Reference

| Variable | Required | Default | Description |
| :--- | :---: | :--- | :--- |
| `PORT` | Optional | `5000` | Port for the backend Express REST API server. |
| `NODE_ENV` | Optional | `development` | Runtime environment (`development`, `production`, `test`). |
| `MONGODB_URI` | Optional | `""` | MongoDB connection URI. If omitted, the server uses fast in-memory caching. |
| `VITE_API_URL` | Optional | `/api` | Base API URL for frontend Axios client (defaults to `/api` proxy). |

---

## 12. Deployment (Vercel)

CustomerAtlas AI is configured for one-click deployment to **Vercel**:
1. Push repository to GitHub.
2. Import project into Vercel.
3. Configure environment variables (`NODE_ENV=production`, optional `MONGODB_URI`).
4. Vercel automatically builds the frontend into `frontend/dist` and mounts backend routes to `api/index.js`.

---

## 13. Future Roadmap

- **Streaming Webhook Ingestion:** Ingest real-time order and review events via authenticated webhooks.
- **Automated CRM & Email Integrations:** Export prioritized retention queues directly into marketing platforms (e.g., Klaviyo, HubSpot, SendGrid).
- **Automated Uplift Modeling:** Implement randomized control trial (RCT) tracking to measure incremental lift from win-back vouchers.

---

## 14. License

This project is licensed under the MIT License. Developed for enterprise customer intelligence, retention modeling, and commercial decision support.
