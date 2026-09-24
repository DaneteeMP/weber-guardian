"""CSV import tests. Real SAP sample shapes, SQLite only."""
from sqlalchemy import func, select

from app.core.subsidiaries import normalize_subsidiary
from app.modules.customers.models import Customer
from app.modules.equipment.models import Equipment
from app.modules.imports.service import run_import

HEADER = (
    '"SAP Debitor ID";"Parent Account: Account Name";"Account Name";"Equipment Name";'
    '"Component Type";"Purchase Date";"Material No.";"Partner Account: Account Name";'
    '"Machine Type";"Physical Country"\n'
)

ROW_ES = '"0001012933";"";"UAB Riela servisas";"304-565";"Slicer";"";"CCS 304-565";"";"CCS304";"Lithuania"\n'
ROW_ES_2 = '"0001012933";"";"UAB Riela servisas";"304-565";"Checkweigher";"";"CCW-3565";"";"CCS304";"Lithuania"\n'
ROW_DE = '"0001035313";"";"Walowsky Int. Maschinenhandel GmbH";"305-220";"Slicer";"";"CCS 305-220";"";"CCS305";"Germany"\n'


def test_dry_run_writes_nothing(db):
    report = run_import(db, (HEADER + ROW_ES + ROW_ES_2).encode(), subsidiary_id="ES", dry_run=True)
    assert report.dry_run is True
    assert report.errors == []
    assert report.customers_created == 1
    assert report.equipment_created == 2
    assert db.scalar(select(func.count()).select_from(Customer)) == 0
    assert db.scalar(select(func.count()).select_from(Equipment)) == 0


def test_real_run_is_idempotent(db):
    content = (HEADER + ROW_ES + ROW_DE).encode()
    first = run_import(db, content, subsidiary_id=None, dry_run=False)
    assert first.errors == []
    assert (first.customers_created, first.equipment_created) == (2, 2)
    second = run_import(db, content, subsidiary_id=None, dry_run=False)
    assert second.errors == []
    assert (second.customers_created, second.equipment_created) == (0, 0)
    assert (second.customers_skipped, second.equipment_skipped) == (2, 2)
    stored = db.scalar(select(Customer).where(Customer.customer_id == "0001012933"))
    assert stored is not None and stored.account_name == "UAB Riela servisas"


def test_any_row_error_aborts_everything(db):
    bad = '"0001012933";"";"";"304-565";"Slicer";"";"CCS 304-565";"";"CCS304";"Lithuania"\n'
    report = run_import(db, (HEADER + ROW_ES + bad).encode(), subsidiary_id=None, dry_run=False)
    assert len(report.errors) == 1
    assert report.errors[0].line == 3
    assert "empty Account Name" in report.errors[0].reason
    assert db.scalar(select(func.count()).select_from(Customer)) == 0
    assert db.scalar(select(func.count()).select_from(Equipment)) == 0


def test_machine_level_row_imports_equipment_with_null_material(db):
    row = '"0001059335";"";"Fresh and Ready Foods Lenexa";"WLN10002-31803";"";"15/9/2025";"";"";"WLN10002";"USA"\n'
    report = run_import(db, (HEADER + row).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.equipment_created == 1
    stored = db.scalar(select(Equipment).where(Equipment.customer_id == "0001059335"))
    assert stored is not None
    assert stored.material_no is None
    assert stored.equipment_name == "WLN10002-31803"
    assert stored.purchase_date == "15/9/2025"


def test_cp1252_fallback_reads_legacy_bytes(db):
    row = '"0001055594";"";"Bizerba Tart? \xf6z\xfcmeleri San.";"305-268";"Slicer";"";"CCS 305-268";"";"CCS305";"Turkey"\n'
    report = run_import(db, (HEADER + row).encode("cp1252"), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    stored = db.scalar(select(Customer).where(Customer.customer_id == "0001055594"))
    assert stored is not None and "Bizerba" in stored.account_name


def test_repeated_part_numbers_across_customers_are_kept(db):
    """material_no is a part reference, not an instance id: the same
    'MSG 460-2' at two customers (or twice at one) imports as two rows."""
    row_a = '"0001012933";"";"UAB Riela servisas";"304-565";"Slicer";"";"MSG 460-2";"";"CCS304";"Lithuania"\n'
    row_b = '"0001035313";"";"Walowsky Int. Maschinenhandel GmbH";"305-220";"Slicer";"";"MSG 460-2";"";"CCS305";"Germany"\n'
    report = run_import(db, (HEADER + row_a + row_b).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.equipment_created == 2


def test_exact_duplicate_rows_are_skipped_not_errors(db):
    report = run_import(db, (HEADER + ROW_ES + ROW_ES).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.equipment_created == 1
    assert report.equipment_skipped == 1
    assert db.scalar(select(func.count()).select_from(Equipment)) == 1


def test_missing_columns_rejected(db):
    report = run_import(db, b"foo;bar\n1;2\n", subsidiary_id=None, dry_run=True)
    assert len(report.errors) == 1
    assert report.errors[0].line == 1


def test_normalize_subsidiary():
    assert normalize_subsidiary(None) is None
    assert normalize_subsidiary("  ") is None
    assert normalize_subsidiary("España") == "ES"
    assert normalize_subsidiary("deutschland") == "DE"
    assert normalize_subsidiary("ZM") == "ZM"


def test_import_normalizes_subsidiary_param(db):
    report = run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id="España", dry_run=False)
    assert report.errors == []
    stored = db.scalar(select(Customer).where(Customer.customer_id == "0001012933"))
    assert stored is not None and stored.subsidiary_id == "ES"
