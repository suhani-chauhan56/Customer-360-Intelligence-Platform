# CustomerAtlas Privacy & Data Minimization Policy

## 1. Data Minimization Principles

CustomerAtlas operates under privacy-by-design standards:
- **Canonical Pseudonymization:** Raw customer identifiers are hashed canonical IDs (`customer_id`). Direct PII (e.g., Brazilian CPF tax IDs, phone numbers, full residential street addresses) are excluded from the analytics feature store.
- **Sensitive Field Shielding:** Exports and API responses exclude raw payment card tokens, security CVVs, and raw customer passwords.
- **Aggregated Analytics:** Macro executive dashboards and segment overviews compute aggregate metrics, minimizing individual profile exposure.

---

## 2. Auditability & Compliance

- **Audit Logging:** Access to individual customer profiles, export generation, and simulation queries are logged in `audit_logs` with timestamps, actor IDs, and IP addresses.
- **Right to Erasure (LGPD / GDPR):** Relational schema cascades ensure that deleting a customer entity automatically purges associated transactions, predictions, and recommendations.
