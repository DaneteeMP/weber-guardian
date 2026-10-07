"""HTTP contract tests for the legacy module workloads (type_code keyed).

These are the hours the Offers tab edits when a module shows
"Workload no configurado"; slicers keep editing the product catalog.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.db import Base, get_db
from app.main import app as api_app
import app.modules.component_names.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.modules.component_names.models import ModuleWorkload
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
            ModuleWorkload(type_code="CCU", label="turntable CCU", workload=None, needs_review=True),
        ]
    )
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def test_module_workload_read_requires_authentication(client):
    assert client.get("/api/v1/module-workloads").status_code == 401


def test_module_workload_update_requires_admin_or_sales(client):
    response = client.put(
        "/api/v1/module-workloads/CCU", json={"workload": "1.00"}, headers=VIEWER
    )
    assert response.status_code == 403


def test_module_workload_update_sets_hours_and_clears_review(client):
    response = client.put(
        "/api/v1/module-workloads/CCU", json={"workload": "1.00"}, headers=ADMIN
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["type_code"] == "CCU"
    assert body["workload"] == "1.00"
    assert body["needs_review"] is False

    listed = client.get("/api/v1/module-workloads?search=CCU", headers=ADMIN)
    assert listed.status_code == 200
    assert listed.headers["X-Total-Count"] == "1"


def test_module_workload_null_hours_keeps_review(client):
    response = client.put(
        "/api/v1/module-workloads/CCU", json={"workload": None}, headers=ADMIN
    )
    assert response.status_code == 200, response.text
    assert response.json()["needs_review"] is True


def test_module_workload_unknown_code_is_created(client):
    """A code the legacy list never had (e.g. MLC) can still be configured."""
    response = client.put(
        "/api/v1/module-workloads/MLC",
        json={"workload": "1.50", "label": "accessories slicing line"},
        headers=ADMIN,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["type_code"] == "MLC"
    assert body["label"] == "accessories slicing line"
    assert body["workload"] == "1.50"
    assert body["needs_review"] is False
