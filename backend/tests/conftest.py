"""Fixtures: in-memory DB (SQLite) for learning service without Postgres."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
import app.modules.customers.models  # noqa: F401
import app.modules.offers.models  # noqa: F401


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
