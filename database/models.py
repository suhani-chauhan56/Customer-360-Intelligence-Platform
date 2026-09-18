"""SQLAlchemy ORM Data Models for CustomerAtlas Enterprise Schema.

Implements normalized entities with primary keys, foreign keys, indexes,
timestamps, constraints, and multi-tenant organization boundaries.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    Index,
    Enum,
)
from sqlalchemy.orm import relationship
from database.connection import Base


class Organization(Base):
    """Multi-tenant organization boundary entity."""
    __tablename__ = "organizations"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    customers = relationship("Customer", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    """Enterprise user account for Role-Based Access Control (RBAC)."""
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    org_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(32), default="Analyst", nullable=False)  # Admin, Analyst, Manager, Viewer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    organization = relationship("Organization", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")


class Customer(Base):
    """Canonical Customer 360 master profile entity."""
    __tablename__ = "customers"

    customer_id = Column(String(64), primary_key=True, index=True)
    org_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), default="default_org", nullable=False, index=True)
    city = Column(String(128), nullable=True)
    state = Column(String(16), nullable=True, index=True)
    rfm_segment = Column(String(64), nullable=True, index=True)
    cluster_segment = Column(String(64), nullable=True, index=True)
    favorite_category = Column(String(128), nullable=True, index=True)
    
    # Financial & RFM Core Metrics
    total_spend = Column(Float, default=0.0, nullable=False, index=True)
    total_orders = Column(Integer, default=1, nullable=False)
    avg_order_value = Column(Float, default=0.0, nullable=False)
    recency_days = Column(Integer, default=0, nullable=False, index=True)
    frequency = Column(Integer, default=1, nullable=False)
    monetary = Column(Float, default=0.0, nullable=False)
    customer_age_days = Column(Integer, default=1, nullable=False)
    
    # Predictive & Intelligence Targets
    predicted_clv = Column(Float, default=0.0, nullable=False, index=True)
    predicted_90d_revenue = Column(Float, default=0.0, nullable=False)
    churn_probability = Column(Float, default=0.0, nullable=False, index=True)
    churn_risk_band = Column(String(32), default="Low", nullable=False, index=True)
    clv_band = Column(String(32), default="Bronze", nullable=False, index=True)
    
    # Behavioral & Experience Signals
    web_engagement_score = Column(Float, default=0.0, nullable=False)
    avg_review_score = Column(Float, default=5.0, nullable=False)
    first_purchase_date = Column(DateTime, nullable=True)
    last_purchase_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    organization = relationship("Organization", back_populates="customers")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="customer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_cust_org_segment", "org_id", "rfm_segment"),
        Index("ix_cust_org_churn", "org_id", "churn_probability"),
        Index("ix_cust_org_clv", "org_id", "predicted_clv"),
    )


class Transaction(Base):
    """Order transaction fact ledger entity."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String(64), nullable=False, index=True)
    customer_id = Column(String(64), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(64), nullable=True, index=True)
    purchase_date = Column(DateTime, nullable=False, index=True)
    order_status = Column(String(32), default="delivered", nullable=False)
    item_price = Column(Float, default=0.0, nullable=False)
    freight_value = Column(Float, default=0.0, nullable=False)
    revenue = Column(Float, default=0.0, nullable=False)

    customer = relationship("Customer", back_populates="transactions")

    __table_args__ = (
        Index("ix_tx_cust_date", "customer_id", "purchase_date"),
    )


class Product(Base):
    """Merchandise product catalog dimension entity."""
    __tablename__ = "products"

    product_id = Column(String(64), primary_key=True, index=True)
    category_name = Column(String(128), nullable=True, index=True)
    category_name_english = Column(String(128), nullable=True, index=True)
    product_weight_g = Column(Float, nullable=True)


class Recommendation(Base):
    """Precomputed explainable next-best-offer recommendation entity."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(64), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True)
    rank = Column(Integer, default=1, nullable=False)
    recommended_category = Column(String(128), nullable=False)
    reason = Column(Text, nullable=False)
    method = Column(String(64), default="Basket Co-occurrence", nullable=False)

    customer = relationship("Customer", back_populates="recommendations")


class ModelPredictionLog(Base):
    """Audit log entity for real-time model inference requests."""
    __tablename__ = "model_prediction_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String(128), nullable=False, index=True)
    model_version = Column(String(32), default="1.0.0", nullable=False)
    customer_id = Column(String(64), nullable=True, index=True)
    input_payload = Column(Text, nullable=False)
    prediction_output = Column(Text, nullable=False)
    latency_ms = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class AuditLog(Base):
    """Enterprise security and compliance audit event ledger entity."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(String(64), ForeignKey("organizations.id", ondelete="CASCADE"), default="default_org", nullable=False, index=True)
    user_id = Column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String(64), nullable=False, index=True)  # e.g., CUSTOMER_VIEWED, EXPORT_GENERATED, MODEL_PREDICT
    resource_type = Column(String(64), nullable=False)       # e.g., Customer, Report, Model
    resource_id = Column(String(128), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
