"""HTTP contract tests for the catalog export/import snapshot.

These cover the flow the deployed app uses to receive catalog work done
elsewhere: export is a read, import is an admin|sales write, is idempotent
(re-importing what was exported changes nothing) and never deletes.
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
import app.modules.component_names.models  # noqa: F401
import app.modules.equipment_catalog.models  # noqa: F401
import app.modules.subsidiaries.models  # noqa: F401
import app.modules.users.models  # noqa: F401
import app.modules.workload_rules.models  # noqa: F401
from app.modules.component_names.models import ComponentName
from app.modules.equipment_catalog.models import EquipmentCatalogEntry, EquipmentCatalogMatch
from app.modules.users.models import User
from app.modules.workload_rules.models import WorkloadRule, WorkloadRuleMaterial

ADMIN = {"X-Dev-User": "oid-admin"}
VIEWER = {"X-Dev-User": "oid-viewer"}
API = "/api/v1/catalog"


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
                material_no="CCW01001", name_en="Checkweigher CW 100", type_code="CCW",
                component_type="Checkweigher",
            ),
            ComponentName(
                material_no="CFV06002", name_en="folding device 905", type_code="CFV",
                component_type="Folding Device",
            ),
        ]
    )
    seed.flush()
    rule = WorkloadRule(
        name="Checkweigher 100", workload=Decimal("1.00"), legacy_type_code="CCW", category="legacy"
    )
    seed.add(rule)
    seed.flush()
    seed.add(WorkloadRuleMaterial(workload_rule_id=rule.id, material_no="CCW01001"))
    entry = EquipmentCatalogEntry(label="1000", workload=Decimal("2.0"))
    entry.matches.append(
        EquipmentCatalogMatch(match_field="machine_type", match_value="WLN01001", is_confirmed=True)
    )
    seed.add(entry)
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def _doc(*rules, lines=()):
    return {"workload_rules": list(rules), "equipment_catalog": list(lines)}


def test_export_requires_authentication(client):
    assert client.get(f"{API}/export").status_code == 401


def test_import_requires_admin_or_sales(client):
    response = client.post(f"{API}/import", json=_doc(), headers=VIEWER)
    assert response.status_code == 403


def test_export_returns_rules_with_materials_and_lines_with_matches(client):
    body = client.get(f"{API}/export", headers=ADMIN).json()

    assert body["format"] == "weberguardian.catalog"
    assert body["workload_rules"] == [
        {
            "name": "Checkweigher 100",
            "workload": "1.00",
            "legacy_type_code": "CCW",
            "category": "legacy",
            "needs_review": False,
            "note": None,
            "materials": ["CCW01001"],
        }
    ]
    assert body["equipment_catalog"] == [
        {
            "label": "1000",
            "workload": "2.0",
            "matches": [
                {"match_field": "machine_type", "match_value": "WLN01001", "is_confirmed": True}
            ],
        }
    ]


def test_reimporting_the_export_changes_nothing(client):
    document = client.get(f"{API}/export", headers=ADMIN).json()

    report = client.post(f"{API}/import", json=document, headers=ADMIN).json()

    assert report["rules_created"] == 0
    assert report["rules_updated"] == 0
    assert report["materials_unchanged"] == 1
    assert report["materials_linked"] == 0
    assert report["lines_created"] == 0
    assert report["lines_updated"] == 0
    assert report["matches_unchanged"] == 1
    assert report["matches_moved"] == 0


def test_import_creates_a_rule_and_skips_materials_outside_the_dictionary(client):
    document = _doc(
        {
            "name": "Folding Station CFV",
            "workload": "5.00",
            "materials": ["CFV06002", "NOPE-1"],
        }
    )

    report = client.post(f"{API}/import", json=document, headers=ADMIN).json()

    assert report["rules_created"] == 1
    assert report["materials_linked"] == 1
    assert report["materials_skipped"] == ["NOPE-1"]
    _, detail = _export_rule(client, "Folding Station CFV")
    assert detail["workload"] == "5.00"
    assert detail["category"] == "manual"
    assert detail["materials"] == ["CFV06002"]


def test_import_updates_the_hours_of_an_existing_rule(client):
    client.post(
        f"{API}/import",
        json=_doc({"name": "Folding Station CFV", "workload": None, "needs_review": True}),
        headers=ADMIN,
    )

    report = client.post(
        f"{API}/import",
        json=_doc({"name": "Folding Station CFV", "workload": "5.00", "needs_review": False}),
        headers=ADMIN,
    ).json()

    assert report["rules_created"] == 0
    assert report["rules_updated"] == 1
    _, detail = _export_rule(client, "Folding Station CFV")
    assert detail["workload"] == "5.00"
    assert detail["needs_review"] is False


def test_import_rejects_a_rule_without_hours_that_is_not_under_review(client):
    response = client.post(
        f"{API}/import",
        json=_doc({"name": "Peeling Machine CCP", "workload": None, "needs_review": False}),
        headers=ADMIN,
    )

    assert response.status_code == 422
    assert "review" in response.json()["detail"]


def test_import_rejects_a_material_linked_to_two_rules(client):
    response = client.post(
        f"{API}/import",
        json=_doc(
            {"name": "Rule A", "workload": "1.00", "materials": ["CFV06002"]},
            {"name": "Rule B", "workload": "2.00", "materials": ["CFV06002"]},
        ),
        headers=ADMIN,
    )

    assert response.status_code == 422
    assert "two rules" in response.json()["detail"]


def test_import_moves_a_match_to_another_line(client):
    document = _doc(
        lines=[
            {
                "label": "90x",
                "workload": "5.0",
                "matches": [{"match_value": "WLN01001", "is_confirmed": True}],
            }
        ]
    )

    report = client.post(f"{API}/import", json=document, headers=ADMIN).json()

    assert report["lines_created"] == 1
    assert report["matches_moved"] == 1
    body = client.get(f"{API}/export", headers=ADMIN).json()
    lines = {line["label"]: line for line in body["equipment_catalog"]}
    assert lines["90x"]["matches"][0]["match_value"] == "WLN01001"
    assert lines["1000"]["matches"] == []


def _export_rule(client, name):
    body = client.get(f"{API}/export", headers=ADMIN).json()
    for rule in body["workload_rules"]:
        if rule["name"] == name:
            return body, rule
    raise AssertionError(f"rule {name!r} not found in export")
