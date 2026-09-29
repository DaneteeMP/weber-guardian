"""Scope tests: subsidiary filtering, created_by, 401/403 over HTTP.

Shared in-memory SQLite (StaticPool) with get_db overridden, so the full
stack (routers + security + services) runs without Postgres or Entra.
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
import app.modules.customers.models  # noqa: F401
import app.modules.offers.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import create_customer
from app.modules.offers.schemas import OfferCalculateIn
from app.modules.subsidiaries.models import Subsidiary
from app.modules.users.models import User


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
            User(external_id="oid-es", role="sales", subsidiary_id="Weber Iberica"),
            User(external_id="oid-de", role="sales", subsidiary_id="Weber Germany"),
            User(external_id="oid-viewer", role="viewer", subsidiary_id="Weber Iberica"),
            Subsidiary(name="Weber Iberica", short_label="Iberica"),
            Subsidiary(name="Weber Germany", short_label="Germany"),
        ]
    )
    seed.commit()
    create_customer(seed, CustomerCreate(customer_id="C-ES", account_name="ES Client", subsidiary_id="Weber Iberica"))
    create_customer(seed, CustomerCreate(customer_id="C-DE", account_name="DE Client", subsidiary_id="Weber Germany"))
    create_customer(seed, CustomerCreate(customer_id="C-LEG", account_name="Legacy Client"))
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def _pricing():
    return OfferCalculateIn(
        work_hours=Decimal("8"),
        report_hours=Decimal("0"),
        trip_hours_base=Decimal("0"),
        km=Decimal("0"),
        km_rate=Decimal("0"),
        tech_rate=Decimal("60"),
        diet_full_rate=Decimal("0"),
        diet_half_rate=Decimal("0"),
        hotel_rate=Decimal("0"),
    )


def test_no_identity_is_401(client):
    assert client.get("/api/v1/customers").status_code == 401


def test_unknown_oid_is_401(client):
    assert client.get("/api/v1/customers", headers={"X-Dev-User": "oid-ghost"}).status_code == 401


def test_me_returns_db_role_and_scope(client):
    res = client.get("/api/v1/users/me", headers={"X-Dev-User": "oid-es"})
    assert res.status_code == 200
    assert res.json() == {
        "external_id": "oid-es",
        "role": "sales",
        "subsidiary_id": "Weber Iberica",
        "subsidiary_short": "Iberica",
        "scope_subsidiary_id": "Weber Iberica",
        "scope_subsidiary_short": "Iberica",
    }


def test_es_sees_only_own_filial(client):
    rows = client.get("/api/v1/customers", headers={"X-Dev-User": "oid-es"}).json()
    assert {r["customer_id"] for r in rows} == {"C-ES"}


def test_untagged_rows_are_admin_only(client):
    es_rows = client.get("/api/v1/customers", headers={"X-Dev-User": "oid-es"}).json()
    assert "C-LEG" not in {r["customer_id"] for r in es_rows}
    admin_rows = client.get("/api/v1/customers", headers={"X-Dev-User": "oid-admin"}).json()
    assert "C-LEG" in {r["customer_id"] for r in admin_rows}


def test_admin_sees_everything(client):
    rows = client.get("/api/v1/customers", headers={"X-Dev-User": "oid-admin"}).json()
    assert {r["customer_id"] for r in rows} == {"C-ES", "C-DE", "C-LEG"}


def test_viewer_cannot_create(client):
    res = client.post(
        "/api/v1/customers",
        json={"customer_id": "C-X", "account_name": "Nope"},
        headers={"X-Dev-User": "oid-viewer"},
    )
    assert res.status_code == 403


def test_offer_scope_and_created_by(client):
    es_offer = client.post(
        "/api/v1/offers",
        json={
            "customer_id": "C-ES",
            "pricing": _pricing().model_dump(mode="json"),
            "items": [],
        },
        headers={"X-Dev-User": "oid-es"},
    )
    assert es_offer.status_code == 201, es_offer.text
    assert es_offer.json()["created_by"] is not None

    de_offer = client.post(
        "/api/v1/offers",
        json={
            "customer_id": "C-DE",
            "pricing": _pricing().model_dump(mode="json"),
            "items": [],
        },
        headers={"X-Dev-User": "oid-de"},
    )
    assert de_offer.status_code == 201

    es_rows = client.get("/api/v1/offers", headers={"X-Dev-User": "oid-es"}).json()
    assert {o["customer_id"] for o in es_rows} == {"C-ES"}

    # Out-of-scope detail reads as missing, not forbidden.
    assert (
        client.get(f"/api/v1/offers/{de_offer.json()['id']}", headers={"X-Dev-User": "oid-es"}).status_code
        == 404
    )


def test_scoped_writes_stay_inside_the_filial(client):
    # ES creating for DE reads as missing customer.
    res = client.post(
        "/api/v1/offers",
        json={"customer_id": "C-DE", "pricing": _pricing().model_dump(mode="json"), "items": []},
        headers={"X-Dev-User": "oid-es"},
    )
    assert res.status_code == 404
    # ES creating a customer for DE is forbidden.
    res = client.post(
        "/api/v1/customers",
        json={"customer_id": "C-X", "account_name": "Nope", "subsidiary_id": "Weber Germany"},
        headers={"X-Dev-User": "oid-es"},
    )
    assert res.status_code == 403
    # ES creating without subsidiary lands in ES.
    res = client.post(
        "/api/v1/customers",
        json={"customer_id": "C-Y", "account_name": "Mine"},
        headers={"X-Dev-User": "oid-es"},
    )
    assert res.status_code == 201
    assert res.json()["subsidiary_id"] == "Weber Iberica"


def test_admin_scope_header_filters_data(client):
    # The header arrives URL-encoded: filial names are free text.
    res = client.get(
        "/api/v1/customers",
        headers={"X-Dev-User": "oid-admin", "X-Scope-Subsidiary": "Weber%20Iberica"},
    )
    assert res.status_code == 200
    assert {r["customer_id"] for r in res.json()} == {"C-ES"}


def test_admin_scope_header_must_name_a_catalog_filial(client):
    res = client.get(
        "/api/v1/customers",
        headers={"X-Dev-User": "oid-admin", "X-Scope-Subsidiary": "Weber%20Nowhere"},
    )
    assert res.status_code == 403
    assert "Unknown subsidiary" in res.json()["detail"]


def test_admin_scope_header_reaches_me_and_summary(client):
    res = client.get(
        "/api/v1/users/me",
        headers={"X-Dev-User": "oid-admin", "X-Scope-Subsidiary": "Weber%20Germany"},
    )
    assert res.json()["scope_subsidiary_id"] == "Weber Germany"
    assert res.json()["scope_subsidiary_short"] == "Germany"


def test_non_admin_cannot_scope_elsewhere(client):
    res = client.get(
        "/api/v1/customers",
        headers={"X-Dev-User": "oid-es", "X-Scope-Subsidiary": "Weber%20Germany"},
    )
    assert res.status_code == 403
    assert "limited" in res.json()["detail"]


def test_non_admin_own_scope_header_is_accepted(client):
    res = client.get(
        "/api/v1/customers",
        headers={"X-Dev-User": "oid-es", "X-Scope-Subsidiary": "Weber%20Iberica"},
    )
    assert res.status_code == 200
    assert {r["customer_id"] for r in res.json()} == {"C-ES"}
