# CustomerAtlas Data Engineering & Pipeline Architecture

## 1. Overview & Data Lineage

CustomerAtlas processes transactional, operational, behavioral, and customer feedback data across **94,983 unique Brazilian e-commerce customer profiles**. The end-to-end pipeline ingests multi-source relational records, cleans anomalies, performs dimensional star-schema modeling, computes RFM quintiles and predictive features, and materializes the unified Customer 360 Feature Store.

```
+-----------------------------------------------------------------------------------+
| RAW SOURCES (Olist Brazilian E-Commerce + Behavioral Event Streams)               |
| - olist_orders_dataset.csv         - olist_order_payments_dataset.csv            |
| - olist_order_items_dataset.csv    - olist_order_reviews_dataset.csv             |
| - olist_customers_dataset.csv      - olist_products_dataset.csv                  |
| - ecommerce_events_2019_dec.csv    - amazon_consumer_reviews.csv                 |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| DIMENSIONAL MODELING & ETL PIPELINE (scripts/data_pipeline.py)                    |
| 1. Entity Resolution: Unifies customer_id with canonical customer_unique_id       |
| 2. Anomaly Cleansing: Drops canceled/unavailable orders, validates timestamps     |
| 3. Star Schema Generation:                                                        |
|    - Fact Tables: fact_orders, fact_payments, fact_reviews, fact_campaign         |
|    - Dim Tables: dim_customer, dim_product, dim_date, dim_campaign                |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| FEATURE ENGINEERING & ML AGGREGATION                                              |
| 1. RFM Behavioral Quintiles (Recency, Frequency, Monetary scoring 1-5)            |
| 2. Commercial Engagement: AOV, Purchase Span (Tenure), Product Breadth            |
| 3. Sentiment & Feedback: Tokenization, CSAT distribution, sentiment polarity      |
| 4. Touchpoints: Web sessions, product views, cart additions, campaign conversions |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
| MATERIALIZED FEATURE STORE & CONTRACT VALIDATION                                  |
| - data/processed/customer_360_features.csv (94,983 records, 24 feature columns)   |
| - Pydantic & Data Quality Contract Verification (Zero null IDs, bounded metrics)  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Dimensional Star Schema Specification

The dimensional warehouse layer structures customer activity into fact and dimension tables optimized for analytical aggregation:

### Fact Tables
* **`fact_orders`**: Grain is individual order line items. Attributes: `order_id`, `customer_id`, `product_id`, `purchase_date`, `order_status`, `item_price`, `freight_value`, `revenue`.
* **`fact_payments`**: Grain is payment transaction slices. Attributes: `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value`.
* **`fact_reviews`**: Grain is feedback surveys. Attributes: `review_id`, `order_id`, `review_score`, `review_comment_title`, `review_comment_message`, `review_creation_date`.
* **`fact_campaign`**: Grain is marketing touchpoint exposures. Attributes: `customer_id`, `campaign_id`, `channel`, `touchpoint_type`, `converted`.

### Dimension Tables
* **`dim_customer`**: Canonical customer master attributes (`customer_unique_id`, `city`, `state`, `zip_code_prefix`, `first_seen_timestamp`).
* **`dim_product`**: Product catalog details (`product_id`, `category_name`, `weight_g`, `length_cm`, `height_cm`, `width_cm`).
* **`dim_date`**: Calendar date dimensional breakdown (`date_key`, `year`, `quarter`, `month`, `day`, `is_weekend`).

---

## 3. Feature Store Engineering Definitions

| Feature Name | Data Type | Formula / Derivation Logic | Business Meaning |
| :--- | :--- | :--- | :--- |
| `recency_days` | Integer | $\text{snapshot\_date} - \max(\text{order\_purchase\_timestamp})$ | Inactivity duration in days |
| `frequency` | Integer | $\text{COUNT}(\text{DISTINCT } \text{order\_id})$ | Lifetime completed purchase count |
| `monetary` / `total_spend` | Float | $\sum (\text{item\_price} + \text{freight\_value})$ | Cumulative gross merchandise spend (BRL) |
| `avg_order_value` | Float | $\text{total\_spend} / \max(1, \text{frequency})$ | Mean revenue per order transaction |
| `customer_age_days` | Integer | $\max(\text{order\_purchase\_date}) - \min(\text{order\_purchase\_date})$ | Customer active transaction tenure span |
| `avg_review_score` | Float | $\text{AVG}(\text{review\_score})$ | Historical CSAT survey score ($1.0\text{--}5.0$) |
| `favorite_category` | String | $\text{MODE}(\text{product\_category\_name\_english})$ | Primary merchandise affinity |
| `predicted_clv` | Float | Model inference via Ridge regressor ($12\text{-month forward}$) | Estimated forward economic value |
| `churn_probability` | Float | Model inference via XGBoost classifier ($[0.0, 1.0]$) | Calibrated probability of customer lapse |

---

## 4. Data Quality Contracts & Validation Engine

CustomerAtlas enforces data quality checks at ingestion and runtime via [`DataQualityService`](file:///C:/Users/HP/Desktop/Customer%20360%20Intelligence/streamlit_app/services/data_quality_service.py):

```python
# Core Quality Contract Invariants
assert df["customer_id"].nunique() == len(df), "Customer IDs must be unique"
assert df["recency_days"].min() >= 0, "Recency cannot be negative"
assert df["total_spend"].min() >= 0, "Monetary spend cannot be negative"
assert df["churn_probability"].between(0.0, 1.0).all(), "Churn probability must be bounded [0, 1]"
```

Data validation reports are logged to the enterprise audit trail on every application bootstrap.
