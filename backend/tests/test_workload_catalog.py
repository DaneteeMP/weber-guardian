"""Workload Catalog identity, reconciliation and CRUD tests."""
from decimal import Decimal

import pytest

from app.modules.component_names.models import ComponentName, ComponentWorkload
from app.modules.component_names.schemas import ComponentWorkloadCreateIn
from app.modules.component_names.workloads import (
    ComponentWorkloadConflict,
    ComponentWorkloadNotFound,
    create_workload,
    delete_workload,
    discover_products,
    import_workload_catalog,
    list_workloads,
    normalize_slicer_model,
    update_workload,
    workload_identity,
)
from sqlalchemy import select


HEADER = "Component Name EN;Type;Material No.;Component Type;Description"


def csv_bytes(*rows: str, encoding: str = "utf-8") -> bytes:
    return (HEADER + "\r\n" + "\r\n".join(rows) + "\r\n").encode(encoding)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Slicer 405-Basic", "Slicer 405"),
        ("Slicer 405-Extended", "Slicer 405"),
        ("Slicer 604-1", "Slicer 604"),
        ("Slicer 604-2", "Slicer 604"),
        ("Slicer 904-1", "Slicer 904"),
        ("Slicer 904-2", "Slicer 904"),
        ("CCS 7000 E2", "Slicer 7000"),
        ("CCS 7000 M6", "Slicer 7000"),
        ("Slicer CCS 7000", "Slicer 7000"),
        ("Slicer weSLICE 9500", "weSLICE 9500"),
        ("weSLICE 2000/2500", "weSLICE 2000/2500"),
        ("weSLICE 7X00", "weSLICE 7X00"),
        ("Textor TS700 Slicer", "Textor Slicer TS700"),
    ],
)
def test_slicer_model_normalization(source: str, expected: str):
    assert normalize_slicer_model(source) == expected


def test_accessory_code_is_not_guessed_into_a_slicer_model():
    assert normalize_slicer_model("CCS 302 | accessories") is None
    source_key, name, needs_review = workload_identity(
        "Slicer", "CCS 302 | accessories"
    )
    assert source_key == "slicer-review:ccs 302 | accessories"
    assert name == "CCS 302 | accessories"
    assert needs_review is True


def test_normal_component_types_share_one_identity_regardless_of_material():
    first = workload_identity(" Checkweigher  ", "Checkweigher CCW 500")
    second = workload_identity("checkweigher", "Checkweigher CCW 200")
    assert first[0] == second[0] == "component:checkweigher"


def test_discovery_groups_many_material_numbers_into_one_component_type():
    names = [
        ComponentName(
            material_no=f"CCW{i:05}",
            name_en=f"Checkweigher {i}",
            type_code=f"T{i % 10}",
            component_type="Checkweigher",
            source_rows=1,
        )
        for i in range(300)
    ]

    products, missing_types, ambiguous_slicers = discover_products(names)

    assert len(products) == 1
    assert products[0].source_key == "component:checkweigher"
    assert products[0].name == "Checkweigher"
    assert products[0].component_type == "Checkweigher"
    assert products[0].needs_review is False
    assert missing_types == 0
    assert ambiguous_slicers == 0


def test_import_collapses_material_serials_and_creates_normalized_slicer_models(db):
    report = import_workload_catalog(
        db,
        csv_bytes(
            "Checkweigher CCW-500;CCW;CCW04001;Checkweigher;Kontrollwaage",
            "Checkweigher CCW-500;CCW;CCW04001-10591;Checkweigher;Kontrollwaage",
            "Slicer 405-Basic;CCS;CCS04051;Slicer;Computerslicer 405 Basic",
            "Slicer 405-Extended;CCS;CCS04051-11745;Slicer;Computerslicer 405 Extended",
            "Slicer 604-1;CCS;CCS06041;Slicer;Computer Slicer 604-1",
            "Slicer 604-2;CCS;CCS06042;Slicer;Computer Slicer 604-2",
        ),
    )

    names = list(db.scalars(select(ComponentName).order_by(ComponentName.material_no)))
    assert [row.material_no for row in names] == ["CCS04051", "CCS06041", "CCS06042", "CCW04001"]
    assert next(row for row in names if row.material_no == "CCW04001").source_rows == 2

    workloads = list_workloads(db, limit=100)
    by_key = {row.source_key: row for row in workloads}
    assert by_key["component:checkweigher"].needs_review is True
    assert by_key["slicer:slicer 405"].needs_review is True
    assert by_key["slicer:slicer 604"].needs_review is True
    assert report.products_discovered == 3
    assert report.workloads_created == 3


def test_import_is_idempotent_and_preserves_a_manual_workload(db):
    raw = csv_bytes(
        "Checkweigher CCW-500;CCW;CCW04001;Checkweigher;Kontrollwaage",
    )
    first_report = import_workload_catalog(db, raw)
    workload = db.scalar(
        select(ComponentWorkload).where(
            ComponentWorkload.source_key == "component:checkweigher"
        )
    )
    assert workload is not None
    original_id = workload.id

    workload.workload = 1.5
    workload.needs_review = False
    workload.name = "Checkweigher (manually named)"
    db.commit()

    second_report = import_workload_catalog(db, raw)
    saved = db.scalar(
        select(ComponentWorkload).where(
            ComponentWorkload.source_key == "component:checkweigher"
        )
    )

    assert first_report.workloads_created == 1
    assert second_report.workloads_created == 0
    assert second_report.workloads_preserved == 1
    assert saved.id == original_id
    assert saved.workload == 1.5
    assert saved.name == "Checkweigher (manually named)"
    assert saved.needs_review is False
    assert len(list_workloads(db)) == 1


def test_reimport_adds_a_new_product_without_touching_existing_manual_values(db):
    import_workload_catalog(
        db,
        csv_bytes("Checkweigher CCW-500;CCW;CCW04001;Checkweigher;Kontrollwaage"),
    )
    old = db.scalar(select(ComponentWorkload))
    old.workload = 1.25
    old.needs_review = False
    db.commit()

    report = import_workload_catalog(
        db,
        csv_bytes(
            "Checkweigher CCW-500;CCW;CCW04001;Checkweigher;Kontrollwaage",
            "Portioning Conveyor;CCU;CCU04051;Portioning Conveyor;Portioniereinheit",
        ),
    )

    rows = {row.source_key: row for row in list_workloads(db)}
    assert report.workloads_created == 1
    assert rows["component:checkweigher"].workload == 1.25
    assert rows["component:checkweigher"].needs_review is False
    assert rows["component:portioning conveyor"].workload is None
    assert rows["component:portioning conveyor"].needs_review is True


def test_slicer_accessories_get_a_review_product_not_a_model_association(db):
    report = import_workload_catalog(
        db,
        csv_bytes("CCS 302 | accessories;CCS;CCS03002;Slicer;CCS 302 accessories"),
    )

    rows = list_workloads(db)
    assert len(rows) == 1
    assert rows[0].source_key == "slicer-review:ccs 302 | accessories"
    assert rows[0].needs_review is True
    assert not any(row.source_key == "slicer:slicer 302" for row in rows)
    assert report.workloads_needing_review_created == 1


def test_crud_keeps_source_key_when_editing_the_visible_name(db):
    created = create_workload(
        db,
        ComponentWorkloadCreateIn(
            name="Checkweigher",
            component_type="Checkweigher",
            workload=None,
        ),
    )
    original_key = created.source_key

    updated = update_workload(
        db,
        created.id,
        {"name": "Checkweigher global workload", "workload": Decimal("1.50")},
    )

    assert updated.source_key == original_key == "component:checkweigher"
    assert updated.name == "Checkweigher global workload"
    assert updated.workload == Decimal("1.50")
    assert updated.needs_review is False


def test_create_rejects_duplicate_product_identity(db):
    payload = ComponentWorkloadCreateIn(name="Rocker", component_type="Rocker")
    create_workload(db, payload)

    with pytest.raises(ComponentWorkloadConflict):
        create_workload(db, payload)


def test_delete_removes_the_product(db):
    created = create_workload(
        db,
        ComponentWorkloadCreateIn(name="Rocker", component_type="Rocker"),
    )

    assert delete_workload(db, created.id) is True
    assert delete_workload(db, created.id) is False
    with pytest.raises(ComponentWorkloadNotFound):
        update_workload(db, created.id, {"workload": 2})


def test_workload_cannot_be_marked_reviewed_without_hours(db):
    with pytest.raises(ValueError, match="must remain marked for review"):
        create_workload(
            db,
            ComponentWorkloadCreateIn(
                name="Rocker",
                component_type="Rocker",
                workload=None,
                needs_review=False,
            ),
        )


@pytest.mark.parametrize("encoding", ["utf-8", "cp1252"])
def test_import_supports_utf8_and_cp1252(encoding: str, db):
    raw = csv_bytes(
        "Rocker;CCR;CCR01001;Rocker;Wippe mit Rückwärtsförderer",
        encoding=encoding,
    )

    report = import_workload_catalog(db, raw)

    assert report.encoding == encoding
    assert list_workloads(db)[0].source_key == "component:rocker"
