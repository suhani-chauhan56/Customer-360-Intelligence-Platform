# CustomerAtlas Relational Database Architecture

## 1. Overview

CustomerAtlas supports a relational database layer powered by **SQLAlchemy ORM** compatible with **SQLite** (local / embedded development) and **PostgreSQL** (production cloud deployments).

---

## 2. Entity-Relationship Schema

```mermaid
erDiagram
    ORGANIZATIONS ||--o{ USERS : "has"
    ORGANIZATIONS ||--o{ CUSTOMERS : "owns"
    ORGANIZATIONS ||--o{ AUDIT_LOGS : "records"
    
    USERS ||--o{ AUDIT_LOGS : "performs"
    
    CUSTOMERS ||--o{ TRANSACTIONS : "places"
    CUSTOMERS ||--o{ RECOMMENDATIONS : "receives"

    ORGANIZATIONS {
        string id PK
        string name
        datetime created_at
        boolean is_active
    }

    USERS {
        string id PK
        string org_id FK
        string email UK
        string hashed_password
        string full_name
        string role
        boolean is_active
        datetime created_at
    }

    CUSTOMERS {
        string customer_id PK
        string org_id FK
        string city
        string state
        string rfm_segment
        string cluster_segment
        string favorite_category
        float total_spend
        int total_orders
        float avg_order_value
        int recency_days
        int frequency
        float monetary
        int customer_age_days
        float predicted_clv
        float predicted_90d_revenue
        float churn_probability
        string churn_risk_band
        string clv_band
        float web_engagement_score
        float avg_review_score
        datetime first_purchase_date
        datetime last_purchase_date
        datetime updated_at
    }

    TRANSACTIONS {
        int id PK
        string order_id
        string customer_id FK
        string product_id
        datetime purchase_date
        string order_status
        float item_price
        float freight_value
        float revenue
    }

    RECOMMENDATIONS {
        int id PK
        string customer_id FK
        int rank
        string recommended_category
        string reason
        string method
    }

    AUDIT_LOGS {
        int id PK
        string org_id FK
        string user_id FK
        string action
        string resource_type
        string resource_id
        string details
        string ip_address
        datetime timestamp
    }
```

---

## 3. Database Indexes

To maintain sub-50ms query response times over large customer datasets, the schema enforces composite and single-column indexes:

| Table | Index Name | Columns | Purpose |
|---|---|---|---|
| `customers` | `ix_customers_customer_id` | `customer_id` | Primary Key & Instant Profile Lookup |
| `customers` | `ix_cust_org_segment` | `org_id, rfm_segment` | Fast Segment Partition Filtering |
| `customers` | `ix_cust_org_churn` | `org_id, churn_probability` | Rapid At-Risk Prioritization Querying |
| `customers` | `ix_cust_org_clv` | `org_id, predicted_clv` | High-Value Cohort Extraction |
| `transactions` | `ix_tx_cust_date` | `customer_id, purchase_date` | Ordered Customer Transaction Timelines |
| `audit_logs` | `ix_audit_org_timestamp` | `org_id, timestamp` | Compliance Time-Series Range Scans |

---

## 4. Seeding & Migrations

- **Database Initialization:** Run `python database/seed.py` to auto-create all tables and seed 5,000 canonical profiles from `data/processed/customer_360_features.csv`.
- **Alembic Readiness:** The SQLAlchemy declarative models inherit from `database.connection.Base`, making Alembic migration generation seamless:
  ```bash
  alembic revision --autogenerate -m "Initial enterprise schema"
  alembic upgrade head
  ```
