# CustomerAtlas Security Architecture & Governance

## 1. Authentication & API Security

- **Authentication Schemes:** API Key validation (`X-API-Key`) and HTTP Bearer tokens with constant-time cryptographic hash comparison to prevent timing side-channel attacks.
- **Role-Based Access Control (RBAC):** Strict 4-role hierarchy (`Admin`, `Analyst`, `Manager`, `Viewer`) with granular endpoint-level permissions.
- **Input Sanitization & Validation:** Pydantic v2 schemas reject malformed data, unexpected fields, and out-of-range numerical parameters.
- **SQL Injection Prevention:** All database operations utilize parameterized SQLAlchemy ORM queries; no dynamic SQL string concatenation is permitted.
- **Error Shielding:** Internal database exception tracebacks are suppressed from client responses and logged exclusively to server logs with structured identifiers.

---

## 2. RBAC Permission Matrix

| Permission Key | Admin | Analyst | Manager | Viewer |
|---|:---:|:---:|:---:|:---:|
| `analytics:view` | ✅ | ✅ | ✅ | ✅ |
| `customer_360:view` | ✅ | ✅ | ✅ | ✅ |
| `customers:search` | ✅ | ✅ | ✅ | ✅ |
| `customers:compare` | ✅ | ✅ | ✅ | ❌ |
| `data:export` | ✅ | ✅ | ❌ | ❌ |
| `pdf:export` | ✅ | ✅ | ✅ | ❌ |
| `simulation:run` | ✅ | ✅ | ✅ | ❌ |
| `ml:infer` | ✅ | ✅ | ❌ | ❌ |
| `ml:view_drift` | ✅ | ✅ | ❌ | ❌ |
| `system:view_audit` | ✅ | ❌ | ❌ | ❌ |
| `system:manage_config`| ✅ | ❌ | ❌ | ❌ |
| `users:manage` | ✅ | ❌ | ❌ | ❌ |

---

## 3. Secret Management & File Upload Security

- **No Hardcoded Secrets:** Configuration keys, database URLs, and API tokens are resolved exclusively from environment variables.
- **Pre-commit Gate:** `.gitignore` blocks `.env`, `.streamlit/secrets.toml`, and credential JSON files.
- **Serialization Safety:** ML models are loaded strictly from the verified local `models/` directory; unverified remote pickle files are disallowed.
