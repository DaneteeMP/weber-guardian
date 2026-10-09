"""Fixtures: in-memory DB (SQLite) for learning service without Postgres."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
import app.modules.basic_kit.models  # noqa: F401
import app.modules.component_names.models  # noqa: F401
import app.modules.customers.models  # noqa: F401
import app.modules.distances.models  # noqa: F401
import app.modules.equipment.models  # noqa: F401
import app.modules.equipment_catalog.models  # noqa: F401
import app.modules.machine_prices.models  # noqa: F401
import app.modules.offers.models  # noqa: F401
import app.modules.prices.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
import app.modules.workload_rules.models  # noqa: F401


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
