"""CSV import service. Parses the SAP export, validates every row first,
then inserts everything in one transaction (or nothing on any error).

Encoding: utf-8-sig first, cp1252 fallback (legacy exports carry mojibake
like "B�seler" otherwise). Empty strings become NULL, never stored as "".

Rows are attached to the customer ID already stored for the account, so the
padded and unpadded SAP Debitor formats coexist without splitting a company
into two customers.
"""
import csv
import io

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.subsidiaries import normalize_subsidiary
from app.modules.customers.models import Customer
from app.modules.customers.service import normalize_customer_id
from app.modules.equipment.models import CustomerSite, Equipment, row_hash_of, site_hash_of
from app.modules.imports.schemas import ImportReport, RowError
from app.modules.subsidiaries.service import subsidiary_for_country, supervision_map

# Real SAP exports reach ~7 MB (tens of thousands of rows). 20 MB caps
# abuse while accepting them; the whole file still fits in memory and the
# single commit stays well within Postgres limits.
MAX_FILE_BYTES = 20 * 1024 * 1024

HEADER_SAP = "SAP Debitor ID"
HEADER_ACCOUNT = "Account Name"
HEADER_EQUIPMENT = "Equipment Name"
HEADER_COMPONENT = "Component Type"
HEADER_PURCHASE = "Purchase Date"
HEADER_MATERIAL = "Material No."
HEADER_MACHINE = "Machine Type"
HEADER_COUNTRY = "Physical Country"
HEADER_PHYSICAL_STREET = "Physical Street"
HEADER_PHYSICAL_CITY = "Physical City"
HEADER_PHYSICAL_POSTAL_CODE = "Physical Zip/Postal Code"
HEADER_PHYSICAL_PROVINCE = "Physical State/Province"

REQUIRED_HEADERS = (HEADER_SAP, HEADER_ACCOUNT, HEADER_MATERIAL)


def _decode(content: bytes) -> str:
    """Decode the upload, tolerating legacy cp1252 exports."""
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return content.decode(encoding)
        except (UnicodeDecodeError, ValueError):
            continue
    raise ValueError("unreadable file: not utf-8 nor cp1252")


def _known_values(db: Session, column, values: set[str]) -> set[str]:
    """DB existence check in 1000-item chunks: a single IN with tens of
    thousands of parameters blows up Postgres statement limits."""
    found: set[str] = set()
    batch = list(values)
    for i in range(0, len(batch), 1000):
        found.update(db.scalars(select(column).where(column.in_(batch[i : i + 1000]))).all())
    return found


def _equipment_by_hash(db: Session, hashes: set[str]) -> dict[str, Equipment]:
    """Fetch existing equipment identities in chunks under Postgres limits."""
    found: dict[str, Equipment] = {}
    batch = list(hashes)
    for i in range(0, len(batch), 1000):
        rows = db.scalars(select(Equipment).where(Equipment.row_hash.in_(batch[i : i + 1000]))).all()
        found.update({row.row_hash: row for row in rows})
    return found


def _site_ids_by_hash(db: Session, hashes: set[str]) -> dict[str, object]:
    """Resolve imported site hashes to primary keys in chunks."""
    found: dict[str, object] = {}
    batch = list(hashes)
    for i in range(0, len(batch), 1000):
        rows = db.execute(
            select(CustomerSite.site_hash, CustomerSite.id).where(
                CustomerSite.site_hash.in_(batch[i : i + 1000])
            )
        ).all()
        found.update({site_hash: site_id for site_hash, site_id in rows})
    return found


def _clean(value: str | None) -> str | None:
    """Empty/blank strings become NULL; values are stripped."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _customer_id_lookup(db: Session) -> tuple[set[str], dict[str, str]]:
    """Read every stored SAP Debitor ID once, for row-to-customer matching.

    Returns the raw IDs and a map from the digits of an ID to the ID already
    on file. Zero padding is not part of the account number, so "0001012933"
    and "1012933" name the same debitor; the shortest variant wins so the
    result does not depend on row order.
    """
    stored: set[str] = set()
    by_digits: dict[str, str] = {}
    for value in db.scalars(select(Customer.customer_id)):
        stored.add(value)
        digits = value.lstrip("0")
        if not value.isdigit() or not digits:
            continue
        current = by_digits.get(digits)
        if current is None or (len(value), value) < (len(current), current):
            by_digits[digits] = value
    return stored, by_digits


def _resolve_customer_id(raw_id: str, stored: set[str], by_digits: dict[str, str]) -> str:
    """Return the stored customer ID a CSV row belongs to.

    SAP has sent the same debitor as both "0001012933" and "1012933", and both
    formats end up in one database. Because the customer ID feeds both row
    hashes, importing the second format silently built a second customer with a
    second copy of the same machines. The ID is canonicalized first (numeric ->
    10 digits): an exact hit wins so a re-import stays idempotent, a legacy
    unpadded variant already on file is reused to avoid splitting it, and an ID
    with no match is stored in the canonical padded form.
    """
    canonical = normalize_customer_id(raw_id)
    if canonical in stored:
        return canonical
    digits = canonical.lstrip("0")
    if not canonical.isdigit() or not digits:
        return canonical
    return by_digits.get(digits, canonical)


def run_import(db: Session, content: bytes, subsidiary_id: str | None, dry_run: bool) -> ImportReport:
    """Validate the whole file, then insert atomically unless dry_run."""
    subsidiary_id = normalize_subsidiary(subsidiary_id)
    if len(content) > MAX_FILE_BYTES:
        return ImportReport(
            dry_run=dry_run,
            total_rows=0,
            customers_created=0,
            customers_skipped=0,
            equipment_created=0,
            equipment_skipped=0,
            errors=[RowError(line=1, reason="file exceeds 20 MB")],
        )
    try:
        text = _decode(content)
    except ValueError as exc:
        return ImportReport(
            dry_run=dry_run,
            total_rows=0,
            customers_created=0,
            customers_skipped=0,
            equipment_created=0,
            equipment_skipped=0,
            errors=[RowError(line=1, reason=str(exc))],
        )

    reader = csv.DictReader(io.StringIO(text), delimiter=";", quotechar='"')
    headers = reader.fieldnames or []
    missing = [h for h in REQUIRED_HEADERS if h not in headers]
    if missing:
        return ImportReport(
            dry_run=dry_run,
            total_rows=0,
            customers_created=0,
            customers_skipped=0,
            equipment_created=0,
            equipment_skipped=0,
            errors=[RowError(line=1, reason=f"missing columns: {', '.join(missing)}")],
        )

    errors: list[RowError] = []
    warnings: list[str] = []
    warned_countries: dict[str, int] = {}
    customers: dict[str, dict] = {}
    sites: dict[str, dict] = {}
    seen_hashes: set[str] = set()
    file_dup_skipped = 0
    bare_skipped = 0
    pending_equipment: list[dict] = []
    total_rows = 0

    mapping = supervision_map(db)
    if subsidiary_id is not None:
        subsidiary_id = normalize_subsidiary(subsidiary_id)

    def resolve_subsidiary(country: str | None) -> str | None:
        """Explicit upload value wins; otherwise the supervision catalog by country."""
        if subsidiary_id is not None:
            return subsidiary_id
        resolved = subsidiary_for_country(country, mapping)
        if resolved is None and country:
            warned_countries[country] = warned_countries.get(country, 0) + 1
        return resolved

    stored_customer_ids, customer_id_by_digits = _customer_id_lookup(db)

    for lineno, raw in enumerate(reader, start=2):
        if all((v or "").strip() == "" for v in raw.values()):
            continue
        total_rows += 1
        sap_id = _clean(raw.get(HEADER_SAP))
        account = _clean(raw.get(HEADER_ACCOUNT))
        material = _clean(raw.get(HEADER_MATERIAL))
        equipment_name = _clean(raw.get(HEADER_EQUIPMENT))
        if not sap_id:
            errors.append(RowError(line=lineno, reason="empty SAP Debitor ID"))
            continue
        if not account:
            errors.append(RowError(line=lineno, reason=f"{sap_id}: empty Account Name"))
            continue
        # Resolved before any hash is built: the customer ID is part of the
        # site and row hashes, so attaching the row to a second copy of an
        # existing account would freeze the duplication into the database.
        sap_id = _resolve_customer_id(sap_id, stored_customer_ids, customer_id_by_digits)
        known = customers.get(sap_id)
        country = _clean(raw.get(HEADER_COUNTRY))
        if known is None:
            customers[sap_id] = {
                "account_name": account,
                "country": country,
                "subsidiary_id": resolve_subsidiary(country),
            }
        elif known["account_name"] != account:
            errors.append(
                RowError(line=lineno, reason=f"{sap_id}: conflicting Account Name ('{account}')")
            )
            continue

        physical_address = {
            "physical_street": _clean(raw.get(HEADER_PHYSICAL_STREET)),
            "physical_city": _clean(raw.get(HEADER_PHYSICAL_CITY)),
            # Postal codes stay strings so leading zeroes are never lost.
            "physical_postal_code": _clean(raw.get(HEADER_PHYSICAL_POSTAL_CODE)),
            "physical_province": _clean(raw.get(HEADER_PHYSICAL_PROVINCE)),
            "physical_country": country,
        }
        site_hash = site_hash_of(sap_id, **physical_address)
        if site_hash is not None:
            sites.setdefault(
                site_hash,
                {"customer_id": sap_id, **physical_address},
            )

        if equipment_name is None and material is None:
            # Customer-only row: nothing installable, keep the customer.
            bare_skipped += 1
            continue
        item = {
            "customer_id": sap_id,
            "equipment_name": equipment_name,
            "machine_type": _clean(raw.get(HEADER_MACHINE)),
            "component_type": _clean(raw.get(HEADER_COMPONENT)),
            "material_no": material,
            "purchase_date": _clean(raw.get(HEADER_PURCHASE)),
            "site_hash": site_hash,
        }
        item["legacy_row_hash"] = row_hash_of(
            item["customer_id"],
            item["equipment_name"],
            item["machine_type"],
            item["component_type"],
            item["material_no"],
            item["purchase_date"],
        )
        item_hash = row_hash_of(
            item["customer_id"],
            item["equipment_name"],
            item["machine_type"],
            item["component_type"],
            item["material_no"],
            item["purchase_date"],
            item["site_hash"],
        )
        if item_hash in seen_hashes:
            # Exact duplicate row in the file (same installed instance listed
            # twice, or overlapping exports): skip, do not fail the import.
            file_dup_skipped += 1
            continue
        seen_hashes.add(item_hash)
        item["row_hash"] = item_hash
        pending_equipment.append(item)

    for country, count in sorted(warned_countries.items()):
        warnings.append(f"country '{country}' has no supervising subsidiary ({count} rows): subsidiary left empty")

    if errors:
        return ImportReport(
            dry_run=dry_run,
            total_rows=total_rows,
            customers_created=0,
            customers_skipped=0,
            equipment_created=0,
            equipment_skipped=0,
            errors=errors,
            warnings=warnings,
        )

    existing_customers = _known_values(db, Customer.customer_id, set(customers.keys()))
    equipment_hashes = {
        hash_value
        for item in pending_equipment
        for hash_value in (item["row_hash"], item["legacy_row_hash"])
    }
    existing_equipment = _equipment_by_hash(db, equipment_hashes)
    existing_site_hashes = _known_values(db, CustomerSite.site_hash, set(sites))
    new_sites = {site_hash: data for site_hash, data in sites.items() if site_hash not in existing_site_hashes}

    new_equipment: list[dict] = []
    site_updates: dict[str, tuple[str, str]] = {}
    used_legacy_hashes: set[str] = set()
    for item in pending_equipment:
        row_hash = item["row_hash"]
        if row_hash in existing_equipment:
            continue
        legacy_hash = item["legacy_row_hash"]
        legacy_row = existing_equipment.get(legacy_hash)
        site_hash = item["site_hash"]
        if (
            site_hash is not None
            and legacy_row is not None
            and legacy_row.site_id is None
            and legacy_hash not in used_legacy_hashes
        ):
            # Enrich a previously imported location-less row instead of
            # creating a second copy when the new export adds address columns.
            site_updates[legacy_hash] = (row_hash, site_hash)
            used_legacy_hashes.add(legacy_hash)
            continue
        new_equipment.append(item)

    report = ImportReport(
        dry_run=dry_run,
        total_rows=total_rows,
        customers_created=0,
        customers_skipped=0,
        sites_created=len(new_sites),
        sites_skipped=len(sites) - len(new_sites),
        equipment_created=0,
        equipment_updated=0,
        equipment_skipped=0,
        errors=[],
        warnings=warnings,
    )
    new_customers = {cid: data for cid, data in customers.items() if cid not in existing_customers}
    report.customers_skipped = len(customers) - len(new_customers)
    report.customers_created = len(new_customers)
    report.equipment_updated = len(site_updates)
    report.equipment_skipped = (
        len(pending_equipment) - len(new_equipment) - len(site_updates) + file_dup_skipped + bare_skipped
    )
    report.equipment_created = len(new_equipment)

    if dry_run:
        return report

    for cid, data in new_customers.items():
        db.add(Customer(customer_id=cid, **data))
    for site_hash, data in new_sites.items():
        db.add(CustomerSite(site_hash=site_hash, **data))
    db.flush()

    site_ids = _site_ids_by_hash(db, set(sites))
    for legacy_hash, (new_hash, site_hash) in site_updates.items():
        existing_equipment[legacy_hash].site_id = site_ids[site_hash]
        existing_equipment[legacy_hash].row_hash = new_hash
    for item in new_equipment:
        equipment_data = {
            key: value
            for key, value in item.items()
            if key not in {"legacy_row_hash", "site_hash"}
        }
        equipment_data["site_id"] = site_ids.get(item["site_hash"])
        db.add(Equipment(**equipment_data))
    db.commit()
    return report
