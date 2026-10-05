"""HTTP contract tests for the Workload Catalog.

They exercise authentication, role restrictions, CRUD and the combined SAP
import/reconciliation endpoint on the same in-memory stack used elsewhere.
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
from app.modules.users.models import User

HEADER = "Component Name EN;Type;Material No.;Component Type;Description"
ADMIN = {"X-Dev-User": "oid-admin"}
VIEWER = {"X-Dev-User": "oid-viewer"}


def sap_csv(*rows: str, encoding: str = "cp1252") -> bytes:
    return (HEADER + "\r\n" + "\r\n".join(rows) + "\r\n").encode(encoding)


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
            User(external_id="oid-sales", role="sales", subsidiary_id="Weber Italy"),
            User(external_id="oid-viewer", role="viewer", subsidiary_id="Weber Italy"),
        ]
    )
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def upload(client, content: bytes, headers=ADMIN):
    return client.post(
        "/api/v1/component-workloads/import",
        files={"file": ("sap-components.csv", content, "text/csv")},
        headers=headers,
    )


def test_workload_read_requires_authentication(client):
    assert client.get("/api/v1/component-workloads").status_code == 401


def test_workload_crud_requires_admin_or_sales(client):
    payload = {"name": "Rocker", "component_type": "Rocker", "workload": "2.00"}
    assert client.post("/api/v1/component-workloads", json=payload, headers=VIEWER).status_code == 403
    assert client.post("/api/v1/component-workloads/import", files={"file": ("a.csv", b"x")}, headers=VIEWER).status_code == 403


def test_workload_catalog_crud(client):
    created = client.post(
        "/api/v1/component-workloads",
        json={
            "name": "Checkweigher",
            "component_type": "Checkweigher",
            "workload": "1.50",
            "needs_review": False,
        },
        headers=ADMIN,
    )
    assert created.status_code == 201, created.text
    original = created.json()
    assert original["name"] == "Checkweigher"

    listed = client.get("/api/v1/component-workloads?search=checkweigher", headers=ADMIN)
    assert listed.status_code == 200
    assert listed.headers["X-Total-Count"] == "1"
    assert len(listed.json()) == 1

    changed = client.patch(
        f"/api/v1/component-workloads/{original['id']}",
        json={"name": "Checkweigher all models", "workload": "1.75"},
        headers=ADMIN,
    )
    assert changed.status_code == 200, changed.text
    assert changed.json()["name"] == "Checkweigher all models"
    assert changed.json()["workload"] == "1.75"
    assert changed.json()["needs_review"] is False

    deleted = client.delete(f"/api/v1/component-workloads/{original['id']}", headers=ADMIN)
    assert deleted.status_code == 204
    assert client.get("/api/v1/component-workloads", headers=ADMIN).json() == []


def test_import_is_idempotent_and_preserves_manual_workload(client):
    first = upload(
        client,
        sap_csv(
            "Checkweigher CCW 500;CCW;CCW04001;Checkweigher;Kontrollwaage",
            "Checkweigher CCW 500 serial;CCW;CCW04001-10591;Checkweigher;Kontrollwaage",
        ),
    )
    assert first.status_code == 200, first.text
    assert first.json()["source_entries"] == 1
    assert first.json()["workloads_created"] == 1

    rows = client.get("/api/v1/component-workloads?search=Checkweigher", headers=ADMIN).json()
    assert len(rows) == 1
    workload_id = rows[0]["id"]
    update = client.patch(
        f"/api/v1/component-workloads/{workload_id}",
        json={"workload": "1.50", "needs_review": False},
        headers=ADMIN,
    )
    assert update.status_code == 200

    second = upload(
        client,
        sap_csv(
            "Checkweigher CCW 500;CCW;CCW04001;Checkweigher;Kontrollwaage",
            "Checkweigher CCW 500 serial;CCW;CCW04001-10591;Checkweigher;Kontrollwaage",
        ),
    )
    assert second.status_code == 200, second.text
    assert second.json()["workloads_created"] == 0
    assert second.json()["workloads_preserved"] == 1

    kept = client.get("/api/v1/component-workloads?search=Checkweigher", headers=ADMIN).json()[0]
    assert kept["id"] == workload_id
    assert kept["workload"] == "1.50"
    assert kept["needs_review"] is False


def test_import_adds_models_separately_and_flags_ambiguous_slicer_names(client):
    response = upload(
        client,
        sap_csv(
            "Slicer 405-Basic;CCS;CCS04051;Slicer;Computerslicer 405 Basic",
            "Slicer 405-Extended;CCS;CCS04051-1;Slicer;Computerslicer 405 Extended",
            "Slicer 604-1;CCS;CCS06041;Slicer;Computerslicer 604-1",
            "Slicer 604-2;CCS;CCS06042;Slicer;Computerslicer 604-2",
            "CCS 302 | accessories;CCS;CCS03002;Slicer;CCS 302 accessories",
        ),
    )
    assert response.status_code == 200, response.text

    rows = client.get("/api/v1/component-workloads", headers=ADMIN).json()
    by_name = {row["name"]: row for row in rows}
    assert "Slicer 405" in by_name
    assert "Slicer 604" in by_name
    assert by_name["Slicer 405"]["needs_review"] is True
    review_rows = [row for row in rows if row["needs_review"]]
    assert any(row["name"] == "CCS 302 | accessories" for row in review_rows)
    assert not any(row["name"] == "Slicer 302" for row in rows)


def test_utf8_bom_csv_import_is_accepted(client):
    raw = (
        "\ufeff"
        + HEADER
        + "\r\nRocker;CCR;CCR01001;Rocker;Wippe mit Rückwärtsförderer\r\n"
    ).encode("utf-8")
    response = upload(client, raw)
    assert response.status_code == 200, response.text
    assert response.json()["encoding"] == "utf-8"
    assert response.json()["workloads_created"] == 1
