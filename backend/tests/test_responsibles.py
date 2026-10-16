"""Service tests for per-subsidiary responsibles.

The dropdown list is managed data: unknown subsidiaries are refused, names
are unique per subsidiary (not globally), and history is safe because offers
store free text.
"""
import pytest

from app.modules.responsibles import service
from app.modules.responsibles.schemas import ResponsibleCreate, ResponsibleUpdate
from app.modules.subsidiaries.models import Subsidiary


@pytest.fixture
def subsidiaries(db):
    db.add_all(
        [
            Subsidiary(name="Weber Iberica", short_label="Iberica"),
            Subsidiary(name="Weber Italy", short_label="Italy"),
        ]
    )
    db.commit()


def test_create_and_list_orders_active_first_then_name(db, subsidiaries):
    service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Zoe"))
    service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Ana"))
    row = service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Marta"))
    service.update_responsible(db, row.id, ResponsibleUpdate(active=False))

    assert [r.name for r in service.list_responsibles(db, "Weber Iberica")] == ["Ana", "Zoe", "Marta"]


def test_names_repeat_across_subsidiaries(db, subsidiaries):
    service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Ana"))
    other = service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Italy", name="Ana"))
    assert other.subsidiary_id == "Weber Italy"


def test_duplicate_name_in_same_subsidiary_conflicts(db, subsidiaries):
    service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Ana"))
    with pytest.raises(service.ResponsibleAlreadyExists):
        service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Ana"))


def test_unknown_subsidiary_is_refused(db):
    with pytest.raises(service.SubsidiaryNotFound):
        service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Nowhere", name="Ana"))


def test_rename_collision_conflicts(db, subsidiaries):
    service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Ana"))
    row = service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Marta"))
    with pytest.raises(service.ResponsibleAlreadyExists):
        service.update_responsible(db, row.id, ResponsibleUpdate(name="Ana"))


def test_update_and_delete_missing_return_sentinels(db, subsidiaries):
    import uuid

    missing = uuid.uuid4()
    assert service.update_responsible(db, missing, ResponsibleUpdate(name="Ana")) is None
    assert service.delete_responsible(db, missing) is False


def test_delete_removes_the_row(db, subsidiaries):
    row = service.create_responsible(db, ResponsibleCreate(subsidiary_id="Weber Iberica", name="Ana"))
    assert service.delete_responsible(db, row.id) is True
    assert service.list_responsibles(db, "Weber Iberica") == []
