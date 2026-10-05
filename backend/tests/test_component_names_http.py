"""HTTP tests for the component name dictionary.

Full stack (router + security + service) on shared in-memory SQLite, so the
import report, the grid filters, the export download and the role rules are
covered without Postgres.
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


def dictionary(*rows: str) -> bytes:
    return (HEADER + "\r\n" + "\r\n".join(rows) + "\r\n").encode("cp1252")


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
            User(external_id="oid-viewer", role="viewer", subsidiary_id="Weber Iberica"),
        ]
    )
    seed.commit()
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client
    api_app.dependency_overrides.clear()


def upload(client, payload: bytes, headers=ADMIN):
    return client.post(
        "/api/v1/component-names/import",
        files={"file": ("names_dictionary.csv", payload, "text/csv")},
        headers=headers,
    )


def test_import_returns_the_cleanup_report(client):
    row = "Rocker CCR 100;CCR;CCR01001;Rocker;Wippe CCR 100 mit Rückwärtsförderer"
    res = upload(client, dictionary(row, row, row))
    assert res.status_code == 200, res.text
    report = res.json()
    # An umlaut is not valid utf-8, so the cp1252 decoder must be the one used.
    assert report["encoding"] == "cp1252"
    assert report["rows_read"] == 3
    assert report["duplicate_rows_collapsed"] == 2
    assert report["entries_written"] == 1
    assert report["entries_total_after"] == 1
    assert report["entries_with_conflict"] == 0


def test_import_reports_what_it_refused_to_invent(client):
    res = upload(
        client,
        dictionary(
            "; ;71511969-02;;BGE Universalband",
            "Multivac R 535;VPM;;Packaging Machine;",
            "",
        ),
    )
    report = res.json()
    assert report["rows_blank"] == 1
    assert report["rows_without_material_no"] == 1
    assert report["material_numbers_without_name"] == 1
    assert report["unmapped_material_numbers"] == ["71511969"]
    assert report["entries_written"] == 0


def test_import_flags_conflicting_entries_for_review(client):
    upload(
        client,
        dictionary(
            "Infeeder CCA;CCA;CCA06001;Infeeder;Infeeder CCA",
            "Infeeder CCA 600;CCA;CCA06001;Infeeder;Infeeder CCA 600",
        ),
    )
    # Re-importing a file without those material numbers removes them as stale.
    assert upload(client, dictionary()).json()["stale_entries_deleted"] == 1
    upload(
        client,
        dictionary(
            "Infeeder CCA;CCA;CCA06001;Infeeder;Infeeder CCA",
            "Infeeder CCA 600;CCA;CCA06001;Infeeder;Infeeder CCA 600",
        ),
    )
    res = client.get("/api/v1/component-names?only_conflicts=true", headers=ADMIN)
    assert [row["material_no"] for row in res.json()] == ["CCA06001"]
    assert res.headers["X-Total-Count"] == "1"


def test_wrong_file_is_refused_with_a_readable_message(client):
    res = upload(client, b"alpha;beta;gamma;delta;epsilon\r\n1;2;3;4;5\r\n")
    assert res.status_code == 422
    assert "unexpected header" in res.json()["detail"]


def test_empty_upload_is_refused(client):
    res = client.post(
        "/api/v1/component-names/import", files={"file": ("empty.csv", b"", "text/csv")}, headers=ADMIN
    )
    assert res.status_code == 422


def test_viewer_cannot_import_or_edit(client):
    assert upload(client, dictionary("Rocker;CCR;CCR01001;Rocker;Wippe"), VIEWER).status_code == 403
    res = client.patch(
        "/api/v1/component-names/CCR01001", json={"name_en": "Nope"}, headers=VIEWER
    )
    assert res.status_code == 403


def test_unauthenticated_access_is_401(client):
    assert client.get("/api/v1/component-names").status_code == 401
    assert client.get("/api/v1/component-names/export").status_code == 401


def test_grid_search_and_total_agree(client):
    upload(
        client,
        dictionary(
            "Rocker CCR 100;CCR;CCR01001;Rocker;Wippe CCR 100",
            "Checkweigher CCW-500;CCW;CCW05001;Checkweigher;Kontrollwaage CCW 500",
        ),
    )
    res = client.get("/api/v1/component-names?search=Wippe", headers=ADMIN)
    assert [row["material_no"] for row in res.json()] == ["CCR01001"]
    assert res.headers["X-Total-Count"] == "1"

    res = client.get("/api/v1/component-names?component_type=Checkweigher", headers=ADMIN)
    assert [row["material_no"] for row in res.json()] == ["CCW05001"]


def test_edit_settles_a_conflict_and_keeps_other_columns(client):
    upload(
        client,
        dictionary(
            "Infeeder CCA;CCA;CCA06001;Infeeder;Infeeder CCA",
            "Infeeder CCA 600;CCA;CCA06001;Infeeder;Infeeder CCA 600",
        ),
    )
    res = client.patch(
        "/api/v1/component-names/CCA06001",
        json={"name_en": "Infeeder CCA 600", "has_conflict": False},
        headers=ADMIN,
    )
    assert res.status_code == 200, res.text
    assert res.json()["name_en"] == "Infeeder CCA 600"
    assert res.json()["has_conflict"] is False
    # Editing one field must not blank the untouched ones.
    assert res.json()["component_type"] == "Infeeder"
    assert res.json()["description"] == "Infeeder CCA"


def test_edit_unknown_material_number_is_404(client):
    res = client.patch("/api/v1/component-names/NOPE", json={"name_en": "x"}, headers=ADMIN)
    assert res.status_code == 404
    assert "NOPE" in res.json()["detail"]


def test_export_downloads_the_clean_dictionary_as_a_download(client):
    upload(client, dictionary("Rocker CCR 100;CCR;CCR01001;Rocker;Wippe CCR 100"))
    res = client.get("/api/v1/component-names/export", headers=ADMIN)
    assert res.status_code == 200
    assert "attachment" in res.headers["content-disposition"]
    assert "names_dictionary_clean.csv" in res.headers["content-disposition"]
    body = res.content.decode("cp1252")
    assert body.splitlines()[0] == HEADER
    assert "CCR01001" in body


def test_export_survives_a_round_trip_through_the_importer(client):
    upload(
        client,
        dictionary(
            "Rocker CCR 100;CCR;CCR01001;Rocker;Wippe CCR 100",
            "Infeeder CCA;CCA;CCA06001;Infeeder;Infeeder CCA",
            "Infeeder CCA 600;CCA;CCA06001;Infeeder;Infeeder CCA 600",
        ),
    )
    download = client.get("/api/v1/component-names/export", headers=ADMIN).content
    report = upload(client, download).json()
    assert report["entries_written"] == 2
    assert report["stale_entries_deleted"] == 0
