"""Database connection engine and session factory for CustomerAtlas.

Supports SQLite for lightweight local and embedded execution, with seamless
PostgreSQL support via standard DATABASE_URL environment configuration.
"""

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# Ensure root and streamlit_app are in sys.path
DB_DIR = Path(__file__).resolve().parent
ROOT_DIR = DB_DIR.parent
APP_DIR = ROOT_DIR / "streamlit_app"
for p in [str(ROOT_DIR), str(APP_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from config.settings import ROOT_DIR
from utils.logging_config import logger

# Base class for all ORM declarative entities
Base = declarative_base()

# Database connection URL from environment, defaulting to local SQLite database
DEFAULT_SQLITE_PATH = ROOT_DIR / "data" / "customer_atlas.db"
DEFAULT_SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}")

# Configure engine with connection pooling and thread safety
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False,
    )

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize all registered database tables and schema objects."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database schema initialized successfully (Target: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL})")
    except Exception as e:
        logger.error(f"Database initialization error: {e}", exc_info=True)
        raise


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI and service dependency for acquiring scoped database sessions."""
    session: Session = SessionFactory()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def db_session_scope() -> Generator[Session, None, None]:
    """Context manager for standalone repository and background operations."""
    session: Session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
