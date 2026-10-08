"""CSV import tests. Real SAP sample shapes, SQLite only."""
from sqlalchemy import func, select

from app.core.subsidiaries import normalize_subsidiary
from app.modules.customers.models import Customer
from app.modules.equipment.models import CustomerSite, Equipment
from app.modules.imports.service import run_import

LEGACY_HEADER = (
    '"SAP Debitor ID";"Parent Account: Account Name";"Account Name";"Equipment Name";'
    '"Component Type";"Purchase Date";"Material No.";"Partner Account: Account Name";'
    '"Machine Type";"Physical Country"\n'
)
HEADER = (
    '"SAP Debitor ID";"Parent Account: Account Name";"Account Name";"Equipment Name";'
    '"Component Type";"Purchase Date";"Material No.";"Partner Account: Account Name";'
    '"Machine Type";"Physical Street";"Physical City";"Physical Zip/Postal Code";'
    '"Physical State/Province";"Physical Country"\n'
)

ROW_ES = '"0001012933";"";"UAB Riela servisas";"304-565";"Slicer";"";"CCS 304-565";"";"CCS304";"Calle 1";"Vilnius";"01234";"Vilnius";"Lithuania"\n'
ROW_ES_2 = '"0001012933";"";"UAB Riela servisas";"304-565";"Checkweigher";"";"CCW-3565";"";"CCS304";"Calle 1";"Vilnius";"01234";"Vilnius";"Lithuania"\n'
ROW_DE = '"0001035313";"";"Walowsky Int. Maschinenhandel GmbH";"305-220";"Slicer";"";"CCS 305-220";"";"CCS305";"Twegtje 1";"Katlenburg-Lindau";"037191";"Niedersachsen";"Germany"\n'


def test_dry_run_writes_nothing(db):
    report = run_import(db, (HEADER + ROW_ES + ROW_ES_2).encode(), subsidiary_id="Weber Iberica", dry_run=True)
    assert report.dry_run is True
    assert report.errors == []
    assert report.customers_created == 1
    assert report.equipment_created == 2
    assert report.sites_created == 1
    assert db.scalar(select(func.count()).select_from(Customer)) == 0
    assert db.scalar(select(func.count()).select_from(Equipment)) == 0
    assert db.scalar(select(func.count()).select_from(CustomerSite)) == 0


def test_real_run_is_idempotent(db):
    content = (HEADER + ROW_ES + ROW_DE).encode()
    first = run_import(db, content, subsidiary_id=None, dry_run=False)
    assert first.errors == []
    assert (first.customers_created, first.sites_created, first.equipment_created) == (2, 2, 2)
    second = run_import(db, content, subsidiary_id=None, dry_run=False)
    assert second.errors == []
    assert (second.customers_created, second.sites_created, second.equipment_created) == (0, 0, 0)
    assert (second.customers_skipped, second.sites_skipped, second.equipment_skipped) == (2, 2, 2)
    stored = db.scalar(select(Customer).where(Customer.customer_id == "0001012933"))
    assert stored is not None and stored.account_name == "UAB Riela servisas"
    site = db.scalar(select(CustomerSite).where(CustomerSite.customer_id == "0001012933"))
    assert site is not None
    assert site.physical_postal_code == "01234"
    assert site.physical_province == "Vilnius"
    assert db.scalar(select(func.count()).select_from(CustomerSite)) == 2


def test_unpadded_sap_id_imports_padded_and_does_not_split(db):
    """A CSV that sends "1052152" must land as "0001052152"; re-importing the
    padded form must not create a second customer for the same company."""
    unpadded = '"1052152";"";"Rosso S.p.A.";"305-100";"Slicer";"";"CCS 305-100";"";"CCS305";"";"Parma";"43012";"Parma";"Italy"\n'
    report = run_import(db, (HEADER + unpadded).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.customers_created == 1
    assert db.scalar(select(Customer).where(Customer.customer_id == "0001052152")) is not None

    padded = unpadded.replace('"1052152"', '"0001052152"', 1)
    again = run_import(db, (HEADER + padded).encode(), subsidiary_id=None, dry_run=False)
    assert again.errors == []
    assert again.customers_created == 0
    assert db.scalar(select(func.count()).select_from(Customer)) == 1


def test_any_row_error_aborts_everything(db):
    bad = '"0001012933";"";"";"304-565";"Slicer";"";"CCS 304-565";"";"CCS304";"Lithuania"\n'
    report = run_import(db, (HEADER + ROW_ES + bad).encode(), subsidiary_id=None, dry_run=False)
    assert len(report.errors) == 1
    assert report.errors[0].line == 3
    assert "empty Account Name" in report.errors[0].reason
    assert db.scalar(select(func.count()).select_from(Customer)) == 0
    assert db.scalar(select(func.count()).select_from(Equipment)) == 0
    assert db.scalar(select(func.count()).select_from(CustomerSite)) == 0


def test_machine_level_row_imports_equipment_with_null_material(db):
    row = '"0001059335";"";"Fresh and Ready Foods Lenexa";"WLN10002-31803";"";"15/9/2025";"";"";"WLN10002";"";"Lenexa";"66215";"Kansas";"USA"\n'
    report = run_import(db, (HEADER + row).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.equipment_created == 1
    stored = db.scalar(select(Equipment).where(Equipment.customer_id == "0001059335"))
    assert stored is not None
    assert stored.material_no is None
    assert stored.equipment_name == "WLN10002-31803"
    assert stored.purchase_date == "15/9/2025"
    assert stored.site is not None and stored.site.physical_postal_code == "66215"


def test_cp1252_fallback_reads_legacy_bytes(db):
    row = '"0001055594";"";"Bizerba Tart? \xf6z\xfcmeleri San.";"305-268";"Slicer";"";"CCS 305-268";"";"CCS305";"Sokak 1";"Istanbul";"34000";"Istanbul";"Turkey"\n'
    report = run_import(db, (HEADER + row).encode("cp1252"), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    stored = db.scalar(select(Customer).where(Customer.customer_id == "0001055594"))
    assert stored is not None and "Bizerba" in stored.account_name


def test_repeated_part_numbers_across_customers_are_kept(db):
    """material_no is a part reference, not an instance id: the same
    'MSG 460-2' at two customers (or twice at one) imports as two rows."""
    row_a = '"0001012933";"";"UAB Riela servisas";"304-565";"Slicer";"";"MSG 460-2";"";"CCS304";"Calle 1";"Vilnius";"01234";"Vilnius";"Lithuania"\n'
    row_b = '"0001035313";"";"Walowsky Int. Maschinenhandel GmbH";"305-220";"Slicer";"";"MSG 460-2";"";"CCS305";"Twegtje 1";"Katlenburg-Lindau";"037191";"Niedersachsen";"Germany"\n'
    report = run_import(db, (HEADER + row_a + row_b).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.equipment_created == 2


def test_exact_duplicate_rows_are_skipped_not_errors(db):
    report = run_import(db, (HEADER + ROW_ES + ROW_ES).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.equipment_created == 1
    assert report.equipment_skipped == 1
    assert db.scalar(select(func.count()).select_from(Equipment)) == 1


def test_new_address_enriches_existing_locationless_equipment(db):
    legacy_row = '"0001035313";"";"Walowsky Int. Maschinenhandel GmbH";"305-220";"Slicer";"";"CCS 305-220";"";"CCS305";"Germany"\n'
    old_import = run_import(db, (LEGACY_HEADER + legacy_row).encode(), subsidiary_id="Weber Germany", dry_run=False)
    assert old_import.errors == [] and old_import.equipment_created == 1

    enriched_import = run_import(db, (HEADER + ROW_DE).encode(), subsidiary_id="Weber Germany", dry_run=False)
    assert enriched_import.errors == []
    assert enriched_import.equipment_created == 0
    assert enriched_import.equipment_updated == 1
    assert enriched_import.sites_created == 1
    assert db.scalar(select(func.count()).select_from(Equipment)) == 1

    equipment = db.scalar(select(Equipment))
    assert equipment is not None and equipment.site is not None
    assert equipment.site.physical_street == "Twegtje 1"
    assert equipment.site.physical_postal_code == "037191"

    repeated_import = run_import(db, (HEADER + ROW_DE).encode(), subsidiary_id="Weber Germany", dry_run=False)
    assert repeated_import.errors == []
    assert repeated_import.equipment_created == 0
    assert repeated_import.equipment_updated == 0


def test_one_customer_can_have_equipment_at_multiple_physical_sites(db):
    second_site_row = ROW_DE.replace("Twegtje 1", "Göttinger Straße 2").replace(
        "Katlenburg-Lindau", "Rosdorf"
    ).replace("037191", "37124")
    report = run_import(
        db,
        (HEADER + ROW_DE + second_site_row).encode(),
        subsidiary_id="Weber Germany",
        dry_run=False,
    )
    assert report.errors == []
    assert report.customers_created == 1
    assert report.sites_created == 2
    assert report.equipment_created == 2
    assert db.scalar(select(func.count()).select_from(CustomerSite)) == 2
    assert db.scalar(select(func.count()).select_from(Equipment)) == 2


def test_missing_columns_rejected(db):
    report = run_import(db, b"foo;bar\n1;2\n", subsidiary_id=None, dry_run=True)
    assert len(report.errors) == 1
    assert report.errors[0].line == 1


def test_normalize_subsidiary():
    assert normalize_subsidiary(None) is None
    assert normalize_subsidiary("  ") is None
    assert normalize_subsidiary("España") == "Weber Iberica"
    assert normalize_subsidiary("deutschland") == "Weber Germany"
    assert normalize_subsidiary("Weber Iberica") == "Weber Iberica"
    assert normalize_subsidiary("Weber Argentina") == "Weber Argentina"
    assert normalize_subsidiary("ZM") == "ZM"


def test_import_normalizes_subsidiary_param(db):
    report = run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id="España", dry_run=False)
    assert report.errors == []
    stored = db.scalar(select(Customer).where(Customer.customer_id == "0001012933"))
    assert stored is not None and stored.subsidiary_id == "Weber Iberica"


ROW_ES_UNPADDED = ROW_ES.replace('"0001012933"', '"1012933"')


def test_padded_row_reuses_the_customer_stored_without_padding(db):
    """SAP sends 0001012933 in one export and 1012933 in the next one. Both
    land on the same canonical padded customer, never a twin."""
    first = run_import(db, (HEADER + ROW_ES_UNPADDED).encode(), subsidiary_id=None, dry_run=False)
    assert first.errors == [] and first.customers_created == 1

    padded = run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id=None, dry_run=False)
    assert padded.errors == []
    assert padded.customers_created == 0
    assert padded.customers_skipped == 1
    assert db.scalar(select(func.count()).select_from(Customer)) == 1
    assert db.scalar(select(Customer)).customer_id == "0001012933"


def test_unpadded_row_reuses_the_customer_stored_padded(db):
    """The reverse direction: the padded customer already on file keeps its
    ID, so reloading the historical export stays idempotent."""
    first = run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id=None, dry_run=False)
    assert first.errors == [] and first.customers_created == 1

    unpadded = run_import(db, (HEADER + ROW_ES_UNPADDED).encode(), subsidiary_id=None, dry_run=False)
    assert unpadded.errors == []
    assert unpadded.customers_created == 0
    assert db.scalar(select(func.count()).select_from(Customer)) == 1
    assert db.scalar(select(Customer)).customer_id == "0001012933"


def test_loading_the_other_format_does_not_copy_the_machines(db):
    """The customer ID feeds the row hash, so a twin would get a second copy
    of every machine. Both loads must end up on the same single row."""
    run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id=None, dry_run=False)
    run_import(db, (HEADER + ROW_ES_UNPADDED).encode(), subsidiary_id=None, dry_run=False)
    assert db.scalar(select(func.count()).select_from(Customer)) == 1
    assert db.scalar(select(func.count()).select_from(Equipment)) == 1


def test_exact_id_wins_when_both_padding_variants_are_stored(db):
    db.add(Customer(customer_id="1012933", account_name="UAB Riela servisas", country="Lithuania"))
    db.add(Customer(customer_id="0001012933", account_name="UAB Riela servisas", country="Lithuania"))
    db.commit()

    report = run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.customers_created == 0
    equipment = db.scalar(select(Equipment))
    assert equipment is not None and equipment.customer_id == "0001012933"


def test_unknown_id_is_stored_exactly_as_the_file_sends_it(db):
    padded = run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id=None, dry_run=False)
    assert padded.errors == [] and padded.customers_created == 1
    assert db.scalar(select(Customer)).customer_id == "0001012933"


def test_non_numeric_ids_do_not_share_their_digits(db):
    """Digit matching only applies to numeric debitors: an alphanumeric key
    that happens to embed the same number is a different account."""
    db.add(Customer(customer_id="X1012933", account_name="Altra S.p.A.", country="Italy"))
    db.commit()

    report = run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id=None, dry_run=False)
    assert report.errors == []
    assert report.customers_created == 1
    assert db.scalar(select(func.count()).select_from(Customer)) == 2


def test_dry_run_does_not_resolve_away_a_pending_customer(db):
    report = run_import(db, (HEADER + ROW_ES).encode(), subsidiary_id=None, dry_run=True)
    assert report.errors == []
    assert report.customers_created == 1
    assert db.scalar(select(func.count()).select_from(Customer)) == 0
