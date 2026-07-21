# CustomerAtlas AI

### Customer 360 Intelligence Platform

From fragmented customer data to actionable retention, value, and growth intelligence.

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.56%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Status](https://img.shields.io/badge/Status-Portfolio%20Prototype-117A72)](#future-improvements)

---

## Project Overview

CustomerAtlas AI is an end-to-end Customer 360 analytics solution that combines customer transactions, digital behavior, campaign response, and product feedback. It establishes a canonical customer identity, organizes data in a MySQL dimensional warehouse, and creates one analysis-ready customer feature store. The platform supports RFM analysis, behavioral segmentation, churn and customer-value modeling, sentiment intelligence, and explainable recommendations. Business users access the results through a responsive Streamlit workspace with customer search, interactive filters, prediction tools, SQL insights, and downloadable reports. Synthetic and proxy elements are explicitly labeled so demonstrated architecture is never presented as observed business performance.

### STAR Summary

| Stage | Delivery |
|---|---|
| **Situation** | Customer, order, browsing, campaign, and feedback data lived at different grains and used incompatible identities. |
| **Task** | Build a governed customer view that supports revenue, retention, experience, and cross-sell decisions. |
| **Action** | Audited four sources, resolved the canonical customer key, designed a MySQL warehouse, engineered customer features, evaluated analytical models, and delivered a seven-page Streamlit product. |
| **Result** | Produced 94,983 searchable profiles, reusable SQL analyses, five business segments, model-assisted risk/value indicators, explainable recommendations, and exportable reports. |

---

## Business Problem

Customer information is usually distributed across sales, web analytics, marketing, CRM, support, and review systems. Teams see only part of the customer journey, which creates inconsistent metrics and slows decisions.

This fragmentation makes it difficult to answer:

- Who are the most valuable and loyal customers?
- Which customers show signs of inactivity?
- Which segments should receive retention or growth campaigns?
- Which products and categories create poor experiences?
- Which offer or category should be recommended next?
- Which campaigns produce the strongest response and ROI?

---

## Solution Overview

The platform keeps each source at a credible analytical grain instead of forcing unrelated records into one flat file:

- Olist provides the canonical customer, transaction, payment, product, and customer-rating records.
- Clickstream data demonstrates web engagement through a clearly marked simulated identity map.
- Amazon/Datafiniti reviews remain a separate product-sentiment module and are not joined to Olist customers.
- Marketing events are synthetic and demonstrate campaign funnel and ROI analysis.
- Python notebooks perform auditing, ETL, EDA, feature engineering, modeling, and release validation.
- MySQL and Streamlit provide governed analytics and an accessible business workspace.

The `customer360_db` warehouse definition is versioned in [`sql/schema.sql`](sql/schema.sql), while ten decision-oriented analyses are maintained in [`sql/business_queries.sql`](sql/business_queries.sql). They cover revenue, repeat purchasing, payment behavior, browse-without-purchase audiences, campaign ROI, customer feedback, and loyalty.

All source monetary values are displayed in Brazilian reais: `R$` is the currency symbol and `BRL` is the ISO currency code. No INR conversion is performed.

---

## System Architecture

```mermaid
flowchart TD
    A[Olist Transactions] --> E[Python ETL]
    B[Clickstream Events] --> E
    C[External Product Reviews] --> E
    D[Synthetic Campaign Events] --> E

    E --> F[Validation and Identity Resolution]
    F --> G[(MySQL Data Warehouse)]
    G --> H[SQL Analytics and EDA]
    G --> I[Customer Feature Store]

    I --> J[RFM and K-Means]
    I --> K[Churn and CLV Proxies]
    I --> L[Sentiment and Recommendations]

    H --> M[Customer Intelligence Layer]
    J --> M
    K --> M
    L --> M
    M --> N[CustomerAtlas AI Streamlit Workspace]
    N --> O[Business Recommendations]
```

### Warehouse Schema

```mermaid
erDiagram
    DIM_CUSTOMER ||--o{ FACT_ORDERS : places
    DIM_PRODUCT ||--o{ FACT_ORDERS : contains
    DIM_DATE ||--o{ FACT_ORDERS : records
    DIM_CUSTOMER ||--o{ FACT_WEB_ACTIVITY : generates
    DIM_CUSTOMER ||--o{ FACT_CUSTOMER_REVIEWS : writes
    DIM_CUSTOMER ||--o{ FACT_CAMPAIGN : receives
    DIM_CAMPAIGN ||--o{ FACT_CAMPAIGN : describes

    DIM_CUSTOMER {
        varchar customer_id PK
        varchar city
        varchar state
        int zip_code_prefix
    }
    DIM_PRODUCT {
        varchar product_id PK
        varchar category_name_english
        decimal product_weight_g
    }
    DIM_DATE {
        int date_key PK
        date full_date
        smallint calendar_year
        tinyint month_number
    }
    FACT_ORDERS {
        varchar order_id PK
        int order_item_id PK
        varchar customer_id FK
        varchar product_id FK
        int purchase_date_key FK
        decimal revenue
    }
    FACT_WEB_ACTIVITY {
        bigint event_id PK
        varchar customer_id FK
        varchar event_type
        datetime event_time
    }
    FACT_CUSTOMER_REVIEWS {
        varchar review_id PK
        varchar customer_id FK
        tinyint rating
    }
    DIM_CAMPAIGN {
        varchar campaign_id PK
        varchar campaign_type
        decimal campaign_cost
    }
    FACT_CAMPAIGN {
        bigint campaign_event_id PK
        varchar campaign_id FK
        varchar customer_id FK
        boolean converted
        decimal revenue_generated
    }
```

`fact_payments` preserves payment-level detail. `fact_product_reviews` remains an independent external product-intelligence fact because Amazon/Datafiniti identities do not belong to the Olist customer domain.

---

## Tech Stack

| Layer | Technologies |
|---|---|
| Programming and analysis | Python, Pandas, NumPy |
| Database and SQL | MySQL 8.0, SQL, SQLAlchemy, PyMySQL |
| Machine learning | Scikit-learn, XGBoost, Random Forest, K-Means, Logistic/Linear Regression |
| NLP and recommendations | TF-IDF, basket co-occurrence, popularity fallback |
| Visualization | Plotly, Matplotlib, Seaborn, WordCloud |
| Application | Streamlit, ReportLab |
| Development | Jupyter Notebook, Git, GitHub |
| Planned NLP benchmark | NLTK-based preprocessing |

NLTK preprocessing remains a roadmap benchmark; the current sentiment pipeline uses scikit-learn TF-IDF.

---

## Dataset Overview

| Dataset | Business purpose | Integration rule |
|---|---|---|
| Olist Brazilian E-Commerce | Customers, transactions, products, payments, ratings | Customer-level source of truth using `customer_unique_id` |
| E-Commerce Events History | Sessions, views, carts, and purchases | Simulated identity mapping for behavior demonstration |
| Amazon/Datafiniti Consumer Reviews | Product rating and review sentiment | External category intelligence; no Olist customer join |
| Marketing Campaign Data | Opens, clicks, conversions, revenue, and cost | Synthetic events marked at row level |

The available sources do not include names, email addresses, age, true discounts, or support tickets. These fields are not fabricated.

---

## Key Features

### Customer 360 Profile

Search a canonical customer and review location, spend, orders, favorite category, digital engagement, campaign response, feedback, purchase timeline, churn propensity, CLV proxy, recommended action, and next-best categories. Profiles can be exported to CSV or PDF.

### RFM Segmentation

Scores recency, frequency, and monetary value to identify Champions, Loyal Customers, Potential Loyalists, At Risk, Lost Customers, and Regular Customers. The segments translate transaction history into clear retention and growth audiences.

### Customer Segmentation

Uses standardized K-Means clustering and profile-based cluster naming to identify High Value, Inactive, Digitally Engaged, Growth Potential, and Regular Buyer groups.

### CLV Prediction

Estimates a calibrated 12-month forward-revenue proxy using recency, frequency, spend, average order value, product breadth, and customer purchase span. The dashboard provides a value band, model interval, and recommended commercial action.

### Churn Prediction

Produces a calibrated churn-propensity score, Low/Medium/High risk band, global model drivers, probability gauge, and suggested retention strategy. Olist has no observed churn label, so this is explicitly presented as a portfolio proxy.

### Sentiment Analysis

Classifies review text using TF-IDF and Logistic Regression. The application includes sentiment mix, trends, review exploration, category summaries, complaint and praise phrases, and an on-demand word cloud.

### Recommendation System

Recommends categories using basket co-occurrence with a popular-category fallback. Every recommendation includes its rank, method, and reason to keep cross-sell suggestions explainable.

### Model Evaluation

| Analytical task | Candidate | Accuracy | F1 | ROC-AUC | MAE | R^2 | Selected |
|---|---|---:|---:|---:|---:|---:|---|
| Churn propensity | Logistic Regression | `0.631` | `0.565` | `0.663` | - | - | No |
| Churn propensity | Random Forest | `0.627` | `0.580` | `0.665` | - | - | No |
| Churn propensity | XGBoost | `0.642` | `0.484` | `0.666` | - | - | **Yes** |
| 12-month CLV proxy | Linear Regression | - | - | - | `BRL 54.62` | `0.820` | No |
| 12-month CLV proxy | Random Forest | - | - | - | `BRL 38.26` | `0.917` | No |
| 12-month CLV proxy | XGBoost | - | - | - | `BRL 38.15` | `0.918` | **Yes** |
| Review sentiment | TF-IDF + Logistic Regression | `0.855` | `0.883` | - | - | - | **Yes** |

Churn selection uses ROC-AUC and CLV selection uses MAE. XGBoost wins both criteria narrowly. Random Forest produces stronger churn F1 and recall at the default threshold, so a production decision should tune the threshold against retention cost rather than treat one metric as universally best. Churn and CLV remain proxy tasks; sentiment labels are derived from review ratings.

---

## Project Workflow

```mermaid
flowchart LR
    A[Audit Sources] --> B[Clean and Validate]
    B --> C[Build Warehouse]
    C --> D[SQL and EDA]
    D --> E[Engineer Features]
    E --> F[Train and Evaluate Models]
    F --> G[Validate App Contracts]
    G --> H[Launch Streamlit]
```

The six notebooks must be run in sequence because each stage validates and produces inputs for the next stage.

---

## Repository Structure

```text
Customer 360 Intelligence/
|-- .streamlit/config.toml
|-- datasets/                              # Original source CSV files
|-- data/processed/                        # Warehouse and application outputs
|-- docs/images/                           # Dashboard screenshots
|-- models/                                # Serialized ML pipelines
|-- notebooks/
|   |-- 01_Data_Audit.ipynb
|   |-- 02_MySQL_Warehouse_ETL.ipynb
|   |-- 03_SQL_EDA.ipynb
|   |-- 04_Feature_Engineering.ipynb
|   |-- 05_ML_Models.ipynb
|   `-- 06_Streamlit_Data_Preparation.ipynb
|-- sql/
|   |-- schema.sql
|   `-- business_queries.sql
|-- streamlit_app/app.py
|-- requirements.txt
`-- README.md
```

---

## Dashboard Preview

The Streamlit workspace contains seven focused destinations:

| Page | Purpose |
|---|---|
| Executive Overview | Animated KPIs, segment revenue, geographic performance, value and recency |
| Customer Explorer | Unified profile, journey, timeline, retention action, recommendations |
| Segments | RFM distribution, behavior clusters, revenue contribution, drill-downs |
| Predictions | Churn gauge, CLV proxy, value band, interval, model drivers |
| Experience | Sentiment intelligence, review themes, campaign funnel and ROI |
| Recommendations | Next-best category, frequently bought together, product performance |
| Data & SQL | Artifact health, predefined analyses, pagination, SQL and report exports |

### Executive Overview

![Executive Dashboard](docs/images/executive-dashboard.png)

### Customer Explorer

![Customer Explorer](docs/images/customer-explorer.png)

### Predictive Intelligence

![Predictive Intelligence](docs/images/predictive-intelligence.png)

---

## Key Business Insights / Results

Historical Olist observations below are reproducible from the source CSVs; campaign and clickstream simulations are excluded.

| Finding | Recommended business action |
|---|---|
| The highest-spending 20% of customers generated **56.7% of merchandise revenue**. | Protect this audience with tiered loyalty benefits and relevant cross-sell offers. |
| Sao Paulo (`SP`) generated approximately **BRL 5.16M**, ahead of Rio de Janeiro and Minas Gerais. | Prioritize regional inventory, delivery capacity, and localized campaigns in high-value states. |
| Only **3.0%** of canonical customers placed more than one order in the observed period. | Build second-purchase journeys and measure cohort retention after the first order. |
| Health & Beauty led category revenue at approximately **BRL 1.26M**, followed by Watches & Gifts. | Use leading categories for acquisition, then recommend complementary products to improve basket value. |
| Late deliveries averaged a **2.57** review score versus **4.25** for on-time deliveries. | Trigger proactive delay communication and prioritize logistics fixes for at-risk orders. |
| **57.8%** of Olist reviews were five-star, while **11.5%** were one-star. | Preserve strong experiences while routing one-star feedback into category and delivery root-cause analysis. |

The pipeline also created **94,983** app-ready profiles and **474,915** explainable category recommendations. Proxy-model metrics measure target recovery, not realized churn reduction or revenue lift.

---

## Installation

### 1. Clone and create the environment

```powershell
git clone <your-repository-url>
cd "Customer 360 Intelligence"
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Prepare MySQL

Open `sql/schema.sql` in MySQL Workbench and execute the complete script to create `customer360_db`. Local CSV extracts are generated by default. To load MySQL from Notebook 02, set credentials and explicitly enable the load:

```powershell
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your-password"
$env:MYSQL_DATABASE="customer360_db"
$env:LOAD_TO_MYSQL="true"
```

### 3. Run the notebooks

```powershell
jupyter notebook
```

Run notebooks `01` through `06` in filename order using **Restart Kernel and Run All Cells**. Notebook 06 must report `Release checks passed.`

### 4. Launch the application

```powershell
streamlit run streamlit_app/app.py
```

Open `http://localhost:8501`.

---

## Future Improvements

- Replace simulated identity mappings and campaigns with consented source-system records.
- Train on observed churn and future-revenue labels and benchmark XGBoost.
- Add SHAP explanations and customer-level reason codes.
- Implement incremental orchestration, drift monitoring, and automated retraining.
- Add authenticated APIs, role-based access, privacy controls, and audit logging.
- Package with Docker, CI/CD, automated tests, and cloud deployment.

---

## Author

**Your Name**  
Data Analyst | Customer Analytics | SQL | Python | Machine Learning

- GitHub: `https://github.com/your-username`
- LinkedIn: `https://www.linkedin.com/in/your-profile`
- Email: `your.email@example.com`

Replace the author placeholders and `<your-repository-url>` before publishing the repository.
