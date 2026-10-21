"""HTTP contract tests for the country supervision mapping.

Reads need identity (the import resolves countries server-side); writes are
global-admin only: a subsidiary-scoped admin manages their own filial, not
the cross-filial country map.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.db import Base, get_db
from app.main import app as api_app
import app.modules.customers.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.modules.customers.models import Customer
from app.modules.subsidiaries.models import Subsidiary, SubsidiaryCountry
from app.modules.users.models import User

ADMIN = {"X-Dev-User": "oid-admin"}
ITALY_ADMIN = {"X-Dev-User": "oid-italy"}
# An admin without the scope header operates with the "All subsidiaries"
# scope (security._resolve_scope), so the negative cases must narrow it.
ITALY_NARROWED = {"X-Dev-User": "oid-italy", "X-Scope-Subsidiary": "Weber Italy"}
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
            SubsidiaryCountry(country="Spain", subsidiary="Weber Iberica"),
            User(external_id="oid-admin", role="admin"),
            User(external_id="oid-italy", role="admin", subsidiary_id="Weber Italy"),
            User(external_id="oid-viewer", role="viewer", subsidiary_id="Weber Iberica"),
            # Stats and unassigned-country rows: Spain is covered by the map,
            # Indonesia and India are not.
            Customer(customer_id="C1", account_name="Cliente España", country="Spain", subsidiary_id="Weber Iberica"),
            Customer(customer_id="C2", account_name="Cliente Indonesia", country="Indonesia", subsidiary_id="Weber Italy"),
            Customer(customer_id="C3", account_name="Cliente India", country="India", subsidiary_id=None),
        ]
    )
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def test_list_requires_authentication(client):
    assert client.get("/api/v1/subsidiaries/countries").status_code == 401


def test_viewer_can_read_mapping(client):
    response = client.get("/api/v1/subsidiaries/countries", headers=VIEWER)
    assert response.status_code == 200
    assert response.json() == [{"country": "Spain", "subsidiary": "Weber Iberica"}]


def test_scoped_admin_cannot_write(client):
    response = client.post(
        "/api/v1/subsidiaries/countries",
        json={"country": "Indonesia", "subsidiary": "Weber Italy"},
        headers=ITALY_NARROWED,
    )
    assert response.status_code == 403


def test_admin_without_narrowing_operates_globally(client):
    # Documents the scope model: any admin who has not narrowed the scope
    # is effectively a global admin (security._resolve_scope).
    response = client.post(
        "/api/v1/subsidiaries/countries",
        json={"country": "Indonesia", "subsidiary": "Weber Italy"},
        headers=ITALY_ADMIN,
    )
    assert response.status_code == 201


def test_viewer_cannot_write(client):
    response = client.post(
        "/api/v1/subsidiaries/countries",
        json={"country": "Indonesia", "subsidiary": "Weber Iberica"},
        headers=VIEWER,
    )
    assert response.status_code == 403


def test_global_admin_creates_and_lists(client):
    created = client.post(
        "/api/v1/subsidiaries/countries",
        json={"country": "Indonesia", "subsidiary": "Weber Italy"},
        headers=ADMIN,
    )
    assert created.status_code == 201
    assert created.json() == {"country": "Indonesia", "subsidiary": "Weber Italy"}
    listing = client.get("/api/v1/subsidiaries/countries", headers=ADMIN)
    assert [row["country"] for row in listing.json()] == ["Indonesia", "Spain"]


def test_duplicate_country_is_conflict_even_with_different_case(client):
    response = client.post(
        "/api/v1/subsidiaries/countries",
        json={"country": "spain", "subsidiary": "Weber Italy"},
        headers=ADMIN,
    )
    assert response.status_code == 409


def test_unknown_target_subsidiary_is_not_found(client):
    response = client.post(
        "/api/v1/subsidiaries/countries",
        json={"country": "Indonesia", "subsidiary": "Weber Nowhere"},
        headers=ADMIN,
    )
    assert response.status_code == 404


def test_move_country(client):
    response = client.patch(
        "/api/v1/subsidiaries/countries/Spain",
        json={"country": "Spain", "subsidiary": "Weber Italy"},
        headers=ADMIN,
    )
    assert response.status_code == 200
    assert response.json() == {"country": "Spain", "subsidiary": "Weber Italy"}


def test_move_unknown_country_is_not_found(client):
    response = client.patch(
        "/api/v1/subsidiaries/countries/Atlantis",
        json={"country": "Atlantis", "subsidiary": "Weber Italy"},
        headers=ADMIN,
    )
    assert response.status_code == 404


def test_move_to_unknown_subsidiary_is_not_found(client):
    response = client.patch(
        "/api/v1/subsidiaries/countries/Spain",
        json={"country": "Spain", "subsidiary": "Weber Nowhere"},
        headers=ADMIN,
    )
    assert response.status_code == 404


def test_delete_then_missing_is_not_found(client):
    deleted = client.delete("/api/v1/subsidiaries/countries/Spain", headers=ADMIN)
    assert deleted.status_code == 204
    again = client.delete("/api/v1/subsidiaries/countries/Spain", headers=ADMIN)
    assert again.status_code == 404
    listing = client.get("/api/v1/subsidiaries/countries", headers=ADMIN)
    assert listing.json() == []


def test_scoped_admin_cannot_delete(client):
    response = client.delete(
        "/api/v1/subsidiaries/countries/Spain", headers=ITALY_NARROWED
    )
    assert response.status_code == 403


def test_stats_requires_authentication(client):
    assert client.get("/api/v1/subsidiaries/stats").status_code == 401


def test_stats_requires_global_admin(client):
    # Counters aggregate every subsidiary: viewer and narrowed admin stay out.
    assert client.get("/api/v1/subsidiaries/stats", headers=VIEWER).status_code == 403
    assert (
        client.get("/api/v1/subsidiaries/stats", headers=ITALY_NARROWED).status_code
        == 403
    )


def test_stats_counts_supervised_countries_and_tagged_customers(client):
    response = client.get("/api/v1/subsidiaries/stats", headers=ADMIN)
    assert response.status_code == 200
    assert response.json() == [
        {"name": "Weber Iberica", "short_label": "Iberica", "countries": 1, "customers": 1},
        {"name": "Weber Italy", "short_label": "Italy", "countries": 0, "customers": 1},
    ]


def test_unassigned_requires_global_admin(client):
    assert (
        client.get("/api/v1/subsidiaries/unassigned-countries", headers=VIEWER).status_code
        == 403
    )
    assert (
        client.get(
            "/api/v1/subsidiaries/unassigned-countries", headers=ITALY_NARROWED
        ).status_code
        == 403
    )


def test_unassigned_lists_customer_countries_outside_the_map_by_volume(client):
    """Only unmapped countries count: Spain is covered, Indonesia and India are not.

    Ordered by customer volume, then name, so the heaviest country is the
    first assignment candidate.
    """
    response = client.get("/api/v1/subsidiaries/unassigned-countries", headers=ADMIN)
    assert response.status_code == 200
    # Same volume: ties break alphabetically (India before Indonesia).
    assert response.json() == [
        {"country": "India", "count": 1},
        {"country": "Indonesia", "count": 1},
    ]


def test_mapping_a_country_removes_it_from_unassigned(client):
    created = client.post(
        "/api/v1/subsidiaries/countries",
        json={"country": "Indonesia", "subsidiary": "Weber Italy"},
        headers=ADMIN,
    )
    assert created.status_code == 201
    response = client.get("/api/v1/subsidiaries/unassigned-countries", headers=ADMIN)
    assert response.json() == [{"country": "India", "count": 1}]


def test_mapping_country_with_its_customers_does_not_move_them(client):
    """Assigning a country only extends the map; customer tagging is a separate
    decision (the import tags rows, this endpoint never rewrites them)."""
    client.post(
        "/api/v1/subsidiaries/countries",
        json={"country": "India", "subsidiary": "Weber Italy"},
        headers=ADMIN,
    )
    response = client.get("/api/v1/subsidiaries/stats", headers=ADMIN)
    italy = next(row for row in response.json() if row["name"] == "Weber Italy")
    assert italy["countries"] == 1
    # C3 keeps subsidiary_id NULL: the map assignment did not touch customers.
    assert italy["customers"] == 1
