"""Database seeding script to populate relational tables from processed CSV datasets."""

import pandas as pd
from datetime import datetime
from config.settings import DATA_DIR
from database.connection import init_db, db_session_scope
from database.models import Organization, User, Customer, Product, Recommendation
from utils.logging_config import logger


def seed_database(sample_size: int = 5000) -> None:
    """Initialize schema and seed database from processed feature store."""
    init_db()
    logger.info("Seeding database tables...")

    with db_session_scope() as session:
        # 1. Seed Default Organization
        org = session.query(Organization).filter(Organization.id == "default_org").first()
        if not org:
            org = Organization(id="default_org", name="CustomerAtlas Enterprise")
            session.add(org)
            session.flush()

        # 2. Seed Default Admin User
        admin = session.query(User).filter(User.email == "admin@customeratlas.io").first()
        if not admin:
            admin = User(
                id="usr_admin_01",
                org_id="default_org",
                email="admin@customeratlas.io",
                hashed_password="scrypt:32768:8:1$demo_salt$demo_hash",  # Enterprise auth readiness placeholder
                full_name="Enterprise Admin",
                role="Admin",
            )
            session.add(admin)

        # 3. Seed Customers from processed feature store
        features_file = DATA_DIR / "customer_360_features.csv"
        if features_file.exists():
            existing_count = session.query(Customer).count()
            if existing_count == 0:
                logger.info(f"Loading customer features from {features_file}...")
                df = pd.read_csv(features_file, nrows=sample_size)
                
                customers_to_insert = []
                for _, row in df.iterrows():
                    first_dt = pd.to_datetime(row.get("first_purchase_date"), errors="coerce")
                    last_dt = pd.to_datetime(row.get("last_purchase_date"), errors="coerce")

                    cust = Customer(
                        customer_id=str(row["customer_id"]),
                        org_id="default_org",
                        city=str(row.get("city", "Unknown")),
                        state=str(row.get("state", "SP")),
                        rfm_segment=str(row.get("rfm_segment", "Regular Customers")),
                        cluster_segment=str(row.get("cluster_segment", "Standard")),
                        favorite_category=str(row.get("favorite_category", "General")),
                        total_spend=float(row.get("total_spend", 0.0)),
                        total_orders=int(row.get("total_orders", 1)),
                        avg_order_value=float(row.get("avg_order_value", 0.0)),
                        recency_days=int(row.get("recency_days", 0)),
                        frequency=int(row.get("frequency", 1)),
                        monetary=float(row.get("monetary", 0.0)),
                        customer_age_days=int(row.get("customer_age_days", 1)),
                        predicted_clv=float(row.get("predicted_clv", 0.0)),
                        predicted_90d_revenue=float(row.get("predicted_90d_revenue", 0.0)),
                        churn_probability=float(row.get("churn_probability", 0.0)),
                        churn_risk_band=str(row.get("churn_risk_band", "Low")),
                        clv_band=str(row.get("clv_band", "Bronze")),
                        web_engagement_score=float(row.get("web_engagement_score", 0.0)),
                        avg_review_score=float(row.get("avg_review_score", 5.0)),
                        first_purchase_date=first_dt if pd.notna(first_dt) else None,
                        last_purchase_date=last_dt if pd.notna(last_dt) else None,
                    )
                    customers_to_insert.append(cust)

                session.bulk_save_objects(customers_to_insert)
                logger.info(f"Seeded {len(customers_to_insert):,} customers into database.")

    logger.info("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_database()
