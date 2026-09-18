# CustomerAtlas REST API Specification

## 1. Overview & Base URL

The CustomerAtlas REST API provides programmatic access to Customer 360 dossiers, audience segmentation, real-time ML inference, and portfolio analytics.

- **Base URL:** `http://localhost:8000/api/v1`
- **Interactive Swagger UI:** `http://localhost:8000/api/docs`
- **ReDoc UI:** `http://localhost:8000/api/redoc`
- **OpenAPI Schema:** `http://localhost:8000/api/openapi.json`

---

## 2. Authentication & Headers

Authentication is managed via API Keys or Bearer tokens:

```http
X-API-Key: ca_live_enterprise_secret_key_demo
X-Organization-ID: default_org
```

Or standard Bearer Authorization:

```http
Authorization: Bearer <api_key>
```

---

## 3. Endpoints Directory

### Customers & 360 Dossiers

| Method | Endpoint | Description | Required Permission |
|---|---|---|---|
| `GET` | `/customers` | Filtered, paginated list of customer profiles | `customers:search` |
| `GET` | `/customers/{customer_id}/360` | Complete 360-degree customer profile | `customer_360:view` |
| `POST` | `/customers/{customer_id}/simulate` | What-If scenario simulation | `simulation:run` |

#### Example Request: Get Customer 360
```bash
curl -X GET "http://localhost:8000/api/v1/customers/0000366f3b9a7992bf8c76cfdf3221e2/360" \
     -H "X-API-Key: ca_live_enterprise_secret_key_demo" \
     -H "X-Organization-ID: default_org"
```

---

### Segments & Audiences

| Method | Endpoint | Description | Required Permission |
|---|---|---|---|
| `GET` | `/segments` | RFM segment distribution & performance | `analytics:view` |
| `GET` | `/segments/{segment_name}/playbook` | Strategic retention playbook for segment | `analytics:view` |
| `GET` | `/segments/compare?segment_a=Champions&segment_b=At%20Risk` | Side-by-side segment comparison | `customers:compare` |

---

### Analytics & Insights

| Method | Endpoint | Description | Required Permission |
|---|---|---|---|
| `GET` | `/analytics/overview` | Macro executive portfolio health metrics | `analytics:view` |
| `GET` | `/analytics/insights` | Evidence-backed structured business insights | `analytics:view` |
| `GET` | `/analytics/recommendations/{customer_id}` | Next-best-category offers for customer | `customer_360:view` |

---

### Machine Learning & MLOps

| Method | Endpoint | Description | Required Permission |
|---|---|---|---|
| `GET` | `/ml/models` | Model registry readiness & metadata | `analytics:view` |
| `POST` | `/ml/predict/churn` | Live XGBoost churn propensity inference | `ml:infer` |
| `POST` | `/ml/predict/clv` | Live XGBoost 12-month forward CLV inference | `ml:infer` |
| `GET` | `/ml/drift` | Population Stability Index (PSI) feature drift | `ml:view_drift` |

#### Example Request: Live Churn Prediction
```bash
curl -X POST "http://localhost:8000/api/v1/ml/predict/churn" \
     -H "Content-Type: application/json" \
     -d '{
       "recency_days": 120,
       "frequency": 2,
       "monetary": 280.0,
       "avg_order_value": 140.0,
       "number_of_products": 2,
       "customer_age_days": 60
     }'
```

---

### System & Governance

| Method | Endpoint | Description | Required Permission |
|---|---|---|---|
| `GET` | `/system/health` | System status, data quality, model count | None (Public Health) |
| `GET` | `/system/audit-logs` | Recent enterprise compliance audit logs | `system:view_audit` |

---

## 4. Standard Response Envelope

All API responses conform to the standard enterprise envelope:

```json
{
  "success": true,
  "data": { ... },
  "message": null,
  "timestamp": "2026-09-18 19:45:00 UTC"
}
```

Error responses return structured, non-leaking JSON envelopes:

```json
{
  "success": false,
  "error": "DataValidationError",
  "detail": "Invalid input parameters: recency_days must be non-negative."
}
```
