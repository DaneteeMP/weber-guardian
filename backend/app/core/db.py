"""Sync DB. One Session per request, self-closed via yield.

Why sync: F0 is for learning the full path. Async adds complexity
(asyncpg, greenlet, async Alembic) with no benefit for a CRUD. Async will be
isolated only in the Salesforce client if ever needed.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI dependency: opens a session, yields it, closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
