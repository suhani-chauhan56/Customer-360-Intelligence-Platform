# CustomerAtlas Enterprise Deployment & Scalability Architecture

## 1. Cloud Architecture

CustomerAtlas is designed for flexible cloud hosting:

```mermaid
flowchart TD
    subgraph Edge["Edge & Ingress Layer"]
        CF[Cloudflare / AWS CloudFront\nSSL & DDoS Protection]
        ALB[Application Load Balancer\nPath Routing]
    end

    subgraph Compute["Container Compute Cluster (ECS / EKS)"]
        UI_Nodes[Streamlit UI Instances\nPort 8501]
        API_Nodes[FastAPI API Instances\nPort 8000]
    end

    subgraph DataStore["Managed Persistence Layer"]
        RDS[(Amazon Aurora PostgreSQL\nPrimary & Read Replicas)]
        S3[(AWS S3\nModel Artifacts & Exports)]
    end

    CF --> ALB
    ALB -->|/api/*| API_Nodes
    ALB -->|/*| UI_Nodes
    UI_Nodes --> RDS
    API_Nodes --> RDS
    API_Nodes --> S3
    UI_Nodes --> S3
```

---

## 2. Horizontal & Vertical Scaling

1. **Stateless API Layer:** FastAPI instances can scale horizontally behind an ALB based on CPU utilization and request concurrency.
2. **Database Read Replicas:** Read-heavy analytical workloads (e.g., segment aggregations, explorer filtering) route to PostgreSQL read replicas.
3. **Streamlit Connection Pooling:** Streamlit UI instances leverage SQLAlchemy connection pooling (`pool_size=10, max_overflow=20`).
4. **Caching:** Dataset caching (`@st.cache_data`) and model resource caching (`@st.cache_resource`) minimize repeated computations.
