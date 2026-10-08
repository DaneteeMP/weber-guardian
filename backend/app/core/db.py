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


# Supabase's pooler (Supavisor / PgBouncer in transaction mode) does not support
# server-side prepared statements, which psycopg uses automatically after a few
# executions. Disabling them keeps the pooler URL usable; on a direct connection
# the cost is negligible. The pooler is much faster to connect to than the direct
# database, which is what makes the first requests on a cold/fresh pool slow.
_connect_args: dict = {}
if settings.database_url.startswith("postgresql"):
    _connect_args["prepare_threshold"] = None

engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """FastAPI dependency: opens a session, yields it, closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
