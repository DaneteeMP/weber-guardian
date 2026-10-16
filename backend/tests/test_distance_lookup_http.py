"""HTTP contract tests for the distance lookup used by offer trip costs.

Free-text SAP provinces resolve server-side; out-of-scope filials get 403
and unknown provinces 404 (the offer keeps zeroes, never a guess).
"""
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.db import Base, get_db
from app.main import app as api_app
import app.modules.distances.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.modules.distances.models import Distance
from app.modules.subsidiaries.models import Subsidiary
from app.modules.users.models import User

ADMIN = {"X-Dev-User": "oid-admin"}
ITALY_SALES = {"X-Dev-User": "oid-italy"}


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
    seed.add_all(
        [
            Subsidiary(name="Weber Iberica", short_label="Iberica"),
            Subsidiary(name="Weber Italy", short_label="Italy"),
            User(external_id="oid-admin", role="admin"),
            User(external_id="oid-italy", role="sales", subsidiary_id="Weber Italy"),
            Distance(
                subsidiary_id="Weber Italy",
                province="Firenze",
                province_code="FI",
                km=Decimal("351"),
                trip_hours=Decimal("2.5"),
            ),
        ]
    )
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def test_lookup_requires_authentication(client):
    response = client.get("/api/v1/distances/lookup?subsidiary_id=Weber Italy&province=Firenze")
    assert response.status_code == 401


def test_lookup_resolves_name_code_and_alias(client):
    for province in ("Firenze", "FI", "florence"):
        response = client.get(
            f"/api/v1/distances/lookup?subsidiary_id=Weber Italy&province={province}",
            headers=ADMIN,
        )
        assert response.status_code == 200, response.text
        assert response.json()["km"] == "351.0"


def test_lookup_unknown_province_is_404(client):
    response = client.get(
        "/api/v1/distances/lookup?subsidiary_id=Weber Italy&province=Atlantis",
        headers=ADMIN,
    )
    assert response.status_code == 404


def test_lookup_out_of_scope_is_forbidden(client):
    response = client.get(
        "/api/v1/distances/lookup?subsidiary_id=Weber Iberica&province=Madrid",
        headers=ITALY_SALES,
    )
    assert response.status_code == 403
