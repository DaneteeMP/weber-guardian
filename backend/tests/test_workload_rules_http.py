"""HTTP contract tests for global workload rules and material links.

These are the endpoints the Workload Catalog and the offer badge use. They
check authentication, roles, validation, the one-rule-per-material invariant
and the error mapping (no raw database errors reach the client).
"""
import uuid
from decimal import Decimal

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
import app.modules.workload_rules.models  # noqa: F401
from app.modules.component_names.models import ComponentName
from app.modules.equipment.models import Equipment
from app.modules.users.models import User

ADMIN = {"X-Dev-User": "oid-admin"}
VIEWER = {"X-Dev-User": "oid-viewer"}
API = "/api/v1/workload-rules"


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
            ComponentName(
                material_no="CCW01001", name_en="Checkweigher CCW 100", type_code="CCW",
                component_type="Checkweigher",
            ),
            ComponentName(
                material_no="CCW02001", name_en="Checkweigher 200", type_code="CCW",
                component_type="Checkweigher",
            ),
            ComponentName(
                material_no="CMB01001", name_en="Marking Conveyor", type_code="CMB",
                component_type="Transport Conveyor", has_conflict=True,
            ),
            Equipment(
                customer_id="0001017849", equipment_name="WLN04051-23050",
                material_no="CCW02001", row_hash="seed-ccw02001",
            ),
        ]
    )
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def _create(client, name: str = "Checkweigher 100", workload: str | None = "1.00"):
    return client.post(API, json={"name": name, "workload": workload}, headers=ADMIN)


def test_rules_read_requires_authentication(client):
    assert client.get(API).status_code == 401


def test_rule_write_requires_admin_or_sales(client):
    response = client.post(API, json={"name": "X", "workload": "1"}, headers=VIEWER)
    assert response.status_code == 403


def test_create_then_list_returns_the_real_rule_name(client):
    created = _create(client)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["name"] == "Checkweigher 100"
    assert Decimal(body["workload"]) == Decimal("1.00")
    assert body["category"] == "manual"
    assert body["legacy_type_code"] is None
    assert body["linked_materials"] == 0

    listed = client.get(API, headers=ADMIN)
    assert listed.status_code == 200
    assert listed.headers["X-Total-Count"] == "1"
    assert listed.json()[0]["name"] == "Checkweigher 100"


def test_create_keeps_the_optional_legacy_code(client):
    response = client.post(
        API,
        json={"name": "Turning Station CCD", "workload": None, "legacy_type_code": "CCD"},
        headers=ADMIN,
    )

    assert response.status_code == 201, response.text
    assert response.json()["legacy_type_code"] == "CCD"


def test_patch_sets_and_clears_the_legacy_code_without_touching_hours(client):
    rule_id = _create(client).json()["id"]

    tagged = client.patch(f"{API}/{rule_id}", json={"legacy_type_code": "CCD"}, headers=ADMIN)
    assert tagged.status_code == 200, tagged.text
    assert tagged.json()["legacy_type_code"] == "CCD"
    assert Decimal(tagged.json()["workload"]) == Decimal("1.00")

    cleared = client.patch(f"{API}/{rule_id}", json={"legacy_type_code": None}, headers=ADMIN)
    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["legacy_type_code"] is None


def test_legacy_code_longer_than_16_chars_is_rejected(client):
    response = client.post(
        API,
        json={"name": "Too long", "workload": "1", "legacy_type_code": "X" * 17},
        headers=ADMIN,
    )

    assert response.status_code == 422


def test_negative_hours_are_rejected(client):
    response = _create(client, workload="-1")
    assert response.status_code == 422


def test_duplicate_rule_name_is_a_conflict_not_a_database_error(client):
    assert _create(client).status_code == 201
    response = _create(client)
    assert response.status_code == 409
    # No raw database error may leak to the client.
    assert "sqlalchemy" not in response.text.lower()
    assert "constraint" not in response.text.lower()


def test_patch_changes_the_global_hours_and_keeps_the_name(client):
    rule_id = _create(client).json()["id"]

    changed = client.patch(f"{API}/{rule_id}", json={"workload": "2.50"}, headers=ADMIN)

    assert changed.status_code == 200, changed.text
    assert Decimal(changed.json()["workload"]) == Decimal("2.50")
    assert changed.json()["name"] == "Checkweigher 100"


def test_patch_cannot_mark_a_rule_without_hours_as_reviewed(client):
    rule_id = _create(client).json()["id"]

    response = client.patch(
        f"{API}/{rule_id}", json={"workload": None, "needs_review": False}, headers=ADMIN
    )

    assert response.status_code == 422


def test_unknown_rule_is_404(client):
    response = client.patch(f"{API}/{uuid.uuid4()}", json={"workload": "1"}, headers=ADMIN)
    assert response.status_code == 404


def test_link_moves_a_material_and_reports_the_previous_rule(client):
    first = _create(client, "Checkweigher 100", "1.00").json()["id"]
    second = _create(client, "Checkweigher 200 mono", "1.50").json()["id"]

    linked = client.put(f"{API}/materials/CCW01001", json={"workload_rule_id": first}, headers=ADMIN)
    assert linked.status_code == 200, linked.text
    assert linked.json()["changed"] is True
    assert linked.json()["previous_rule_id"] is None

    moved = client.put(f"{API}/materials/CCW01001", json={"workload_rule_id": second}, headers=ADMIN)
    assert moved.status_code == 200, moved.text
    assert moved.json()["previous_rule_id"] == first
    assert moved.json()["previous_rule_name"] == "Checkweigher 100"

    old_detail = client.get(f"{API}/{first}", headers=ADMIN).json()
    new_detail = client.get(f"{API}/{second}", headers=ADMIN).json()
    assert old_detail["linked_materials"] == 0
    assert [row["material_no"] for row in new_detail["materials"]] == ["CCW01001"]


def test_linking_an_unknown_material_is_404_with_domain_message(client):
    rule_id = _create(client).json()["id"]

    response = client.put(f"{API}/materials/NOPE-000", json={"workload_rule_id": rule_id}, headers=ADMIN)

    assert response.status_code == 404
    assert response.json()["detail"] == "material is not in the component dictionary"


def test_unlink_removes_the_link_then_is_404(client):
    rule_id = _create(client).json()["id"]
    client.put(f"{API}/materials/CCW01001", json={"workload_rule_id": rule_id}, headers=ADMIN)

    removed = client.delete(f"{API}/materials/CCW01001", headers=ADMIN)
    again = client.delete(f"{API}/materials/CCW01001", headers=ADMIN)

    assert removed.status_code == 204
    assert again.status_code == 404


def test_resolve_explains_a_serial_number_through_its_rule(client):
    rule_id = _create(client).json()["id"]
    client.put(f"{API}/materials/CCW01001", json={"workload_rule_id": rule_id}, headers=ADMIN)

    response = client.get(f"{API}/materials/resolve", params={"material_no": "CCW01001-10901"}, headers=ADMIN)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["state"] == "resolved"
    assert body["dictionary_material_no"] == "CCW01001"
    assert body["rule"]["name"] == "Checkweigher 100"


def test_resolve_marks_an_unlinked_material_as_no_rule(client):
    response = client.get(f"{API}/materials/resolve", params={"material_no": "CCW02001"}, headers=ADMIN)

    assert response.json()["state"] == "no_rule"
    assert response.json()["rule"] is None


def test_unresolved_list_reports_reasons_and_total(client):
    response = client.get(f"{API}/unresolved", headers=ADMIN)

    assert response.status_code == 200
    rows = {row["material_no"]: row["reason"] for row in response.json()}
    assert rows == {"CCW02001": "no_rule"}
    assert response.headers["X-Total-Count"] == "1"


def test_unresolved_reports_a_linked_rule_that_still_has_no_hours(client):
    rule_id = _create(client, name="Folding Bar CFV", workload=None).json()["id"]
    client.put(f"{API}/materials/CCW02001", json={"workload_rule_id": rule_id}, headers=ADMIN)

    response = client.get(f"{API}/unresolved", headers=ADMIN)

    rows = {row["material_no"]: row["reason"] for row in response.json()}
    assert rows == {"CCW02001": "no_hours"}


def test_category_filter_rejects_unknown_values(client):
    response = client.get(API, params={"category": "made-up"}, headers=ADMIN)
    assert response.status_code == 422


def test_delete_rule_requires_authentication_and_roles(client):
    rule_id = _create(client).json()["id"]

    anonymous = client.delete(f"{API}/{rule_id}")
    viewer = client.delete(f"{API}/{rule_id}", headers=VIEWER)

    assert anonymous.status_code == 401
    assert viewer.status_code == 403


def test_delete_removes_an_unused_rule(client):
    rule_id = _create(client).json()["id"]

    deleted = client.delete(f"{API}/{rule_id}", headers=ADMIN)

    assert deleted.status_code == 204
    assert client.get(f"{API}/{rule_id}", headers=ADMIN).status_code == 404
    assert client.get(API, headers=ADMIN).json() == []


def test_delete_drops_links_of_materials_nobody_has_installed(client):
    rule_id = _create(client).json()["id"]
    client.put(f"{API}/materials/CCW01001", json={"workload_rule_id": rule_id}, headers=ADMIN)

    deleted = client.delete(f"{API}/{rule_id}", headers=ADMIN)

    assert deleted.status_code == 204
    # CCW01001 is installed nowhere, so serials simply fall back to "no rule".
    resolved = client.get(
        f"{API}/materials/resolve", params={"material_no": "CCW01001-10901"}, headers=ADMIN
    )
    assert resolved.json()["state"] == "no_rule"


def test_delete_is_blocked_while_a_customer_owns_its_material(client):
    # The fixture installs CCW02001 at customer 0001017849.
    rule_id = _create(client).json()["id"]
    client.put(f"{API}/materials/CCW02001", json={"workload_rule_id": rule_id}, headers=ADMIN)

    blocked = client.delete(f"{API}/{rule_id}", headers=ADMIN)

    assert blocked.status_code == 409
    assert "1 customer(s)" in blocked.json()["detail"]
    assert client.get(f"{API}/{rule_id}", headers=ADMIN).status_code == 200


def test_delete_unknown_rule_is_404(client):
    response = client.delete(f"{API}/{uuid.uuid4()}", headers=ADMIN)
    assert response.status_code == 404
