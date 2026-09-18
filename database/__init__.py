"""Database package for CustomerAtlas enterprise relational layer."""

from database.connection import Base, engine, SessionFactory, init_db, get_db_session, db_session_scope
from database.models import Organization, User, Customer, Transaction, Product, Recommendation, ModelPredictionLog, AuditLog
from database.repositories.customer_repository import CustomerRepository
from database.repositories.transaction_repository import TransactionRepository
from database.repositories.analytics_repository import AnalyticsRepository
from database.repositories.audit_repository import AuditRepository

__all__ = [
    "Base",
    "engine",
    "SessionFactory",
    "init_db",
    "get_db_session",
    "db_session_scope",
    "Organization",
    "User",
    "Customer",
    "Transaction",
    "Product",
    "Recommendation",
    "ModelPredictionLog",
    "AuditLog",
    "CustomerRepository",
    "TransactionRepository",
    "AnalyticsRepository",
    "AuditRepository",
]
