"""HTTP contract tests for responsibles.

Reads need identity, writes need admin, and scoped identities only touch
their own subsidiary (404 otherwise, so existence never leaks).
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.db import Base, get_db
from app.main import app as api_app
import app.modules.responsibles.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.modules.subsidiaries.models import Subsidiary
from app.modules.users.models import User

ADMIN = {"X-Dev-User": "oid-admin"}
ITALY = {"X-Dev-User": "oid-italy"}
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
            Subsidiary(name="Weber Iberica", short_label="Iberica"),
            Subsidiary(name="Weber Italy", short_label="Italy"),
            User(external_id="oid-admin", role="admin"),
            User(external_id="oid-italy", role="admin", subsidiary_id="Weber Italy"),
            User(external_id="oid-viewer", role="viewer"),
        ]
    )
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def test_list_requires_authentication(client):
    assert client.get("/api/v1/responsibles?subsidiary_id=Weber Iberica").status_code == 401


def test_list_requires_subsidiary_id(client):
    assert client.get("/api/v1/responsibles", headers=ADMIN).status_code == 422


def test_scoped_admin_cannot_read_other_subsidiary(client):
    response = client.get("/api/v1/responsibles?subsidiary_id=Weber Iberica", headers=ITALY)
    assert response.status_code == 404


def test_create_and_list_roundtrip(client):
    created = client.post(
        "/api/v1/responsibles",
        json={"subsidiary_id": "Weber Iberica", "name": "Ana"},
        headers=ADMIN,
    )
    assert created.status_code == 201, created.text
    assert created.json()["name"] == "Ana"

    listed = client.get("/api/v1/responsibles?subsidiary_id=Weber Iberica", headers=ADMIN)
    assert [r["name"] for r in listed.json()] == ["Ana"]


def test_create_duplicate_conflicts_and_unknown_subsidiary_404s(client):
    client.post(
        "/api/v1/responsibles",
        json={"subsidiary_id": "Weber Iberica", "name": "Ana"},
        headers=ADMIN,
    )
    duplicate = client.post(
        "/api/v1/responsibles",
        json={"subsidiary_id": "Weber Iberica", "name": "Ana"},
        headers=ADMIN,
    )
    assert duplicate.status_code == 409

    unknown = client.post(
        "/api/v1/responsibles",
        json={"subsidiary_id": "Weber Nowhere", "name": "Ana"},
        headers=ADMIN,
    )
    assert unknown.status_code == 404

    blank = client.post(
        "/api/v1/responsibles",
        json={"subsidiary_id": "Weber Iberica", "name": "   "},
        headers=ADMIN,
    )
    assert blank.status_code == 422


def test_viewer_cannot_write_and_scoped_admin_cannot_write_elsewhere(client):
    assert (
        client.post(
            "/api/v1/responsibles",
            json={"subsidiary_id": "Weber Iberica", "name": "Ana"},
            headers=VIEWER,
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/v1/responsibles",
            json={"subsidiary_id": "Weber Iberica", "name": "Ana"},
            headers=ITALY,
        ).status_code
        == 404
    )


def test_update_and_delete_roundtrip(client):
    created = client.post(
        "/api/v1/responsibles",
        json={"subsidiary_id": "Weber Iberica", "name": "Ana"},
        headers=ADMIN,
    ).json()

    renamed = client.patch(
        f"/api/v1/responsibles/{created['id']}",
        json={"name": "Marta", "active": False},
        headers=ADMIN,
    )
    assert renamed.status_code == 200, renamed.text
    assert renamed.json()["name"] == "Marta"
    assert renamed.json()["active"] is False

    missing_id = "00000000-0000-0000-0000-000000000000"
    assert client.patch(f"/api/v1/responsibles/{missing_id}", json={"name": "X"}, headers=ADMIN).status_code == 404
    assert client.delete(f"/api/v1/responsibles/{missing_id}", headers=ADMIN).status_code == 404

    assert client.delete(f"/api/v1/responsibles/{created['id']}", headers=ADMIN).status_code == 204
    listed = client.get("/api/v1/responsibles?subsidiary_id=Weber Iberica", headers=ADMIN)
    assert listed.json() == []
