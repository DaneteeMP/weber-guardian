"""HTTP contract tests for the maintenance draft endpoint.

Regression cover for the production incident where maintenance-draft failed
with a bare 500: Starlette answers unhandled exceptions outside the CORS
middleware, so browsers misreport the failure as a CORS block and the real
error is invisible. Database failures must therefore surface as mapped HTTP
errors (which carry CORS headers), never as raw tracebacks.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.config import settings as app_settings
from app.core.db import Base, get_db
from app.main import app as api_app
from app.modules.offers import maintenance as maintenance_module
import app.modules.customers.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.modules.users.models import User

ADMIN = {"X-Dev-User": "oid-admin"}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(security.settings, "dev_auth_enabled", True)
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    api_app.dependency_overrides[get_db] = override_db
    seed = Session()
    seed.add(User(external_id="oid-admin", role="admin"))
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def _draft_payload():
    return {"customer_id": "CUST-1", "machine_names": ["M-1"]}


def test_maintenance_draft_database_failure_is_a_503_with_cors_headers(
    client, monkeypatch
):
    """A DB failure (missing table from unapplied migrations, lost connection)
    must come back as 503 with CORS headers, not as a bare 500 the browser
    misreports as a CORS block. Raw DB text must never leak to the client."""

    def boom(*args, **kwargs):
        raise OperationalError("select 1", {}, Exception("relation does not exist"))

    monkeypatch.setattr(maintenance_module, "maintenance_draft", boom)

    origin = (app_settings.cors_origins or ["http://localhost:5173"])[0]
    response = client.post(
        "/api/v1/offers/maintenance-draft",
        json=_draft_payload(),
        headers={**ADMIN, "Origin": origin},
    )

    assert response.status_code == 503, response.text
    assert response.headers.get("access-control-allow-origin") == origin
    assert "relation does not exist" not in response.text
    assert "alembic upgrade head" in response.json()["detail"]
