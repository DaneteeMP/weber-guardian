"""HTTP contract tests for machine-line workloads (equipment_catalog).

These are the hours the Offers tab edits when a line row shows
"Workload not configured" (the slicer family price, e.g. "40x").
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
import app.modules.equipment_catalog.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.modules.users.models import User

ADMIN = {"X-Dev-User": "oid-admin"}
VIEWER = {"X-Dev-User": "oid-viewer"}


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
            User(external_id="oid-admin", role="admin"),
            User(external_id="oid-viewer", role="viewer", subsidiary_id="Weber Italy"),
        ]
    )
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def test_line_workload_read_requires_authentication(client):
    assert client.get("/api/v1/line-workloads").status_code == 401


def test_line_workload_update_requires_admin_or_sales(client):
    response = client.put(
        "/api/v1/line-workloads/CCS302", json={"workload": "2.00"}, headers=VIEWER
    )
    assert response.status_code == 403


def test_line_workload_update_creates_and_confirms_a_new_code(client):
    created = client.put(
        "/api/v1/line-workloads/CCS302",
        json={"workload": "2.00", "label": "30x"},
        headers=ADMIN,
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["label"] == "30x"
    assert Decimal(body["workload"]) == Decimal("2.00")
    assert body["matches"][0]["match_value"] == "CCS302"
    assert body["matches"][0]["is_confirmed"] is True

    listed = client.get("/api/v1/line-workloads", headers=ADMIN)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_line_workload_update_changes_an_existing_code(client):
    client.put(
        "/api/v1/line-workloads/CCS302",
        json={"workload": "2.00", "label": "30x"},
        headers=ADMIN,
    )
    changed = client.put(
        "/api/v1/line-workloads/CCS302", json={"workload": "3.50"}, headers=ADMIN
    )
    assert changed.status_code == 200, changed.text
    assert Decimal(changed.json()["workload"]) == Decimal("3.50")
    assert len(client.get("/api/v1/line-workloads", headers=ADMIN).json()) == 1
