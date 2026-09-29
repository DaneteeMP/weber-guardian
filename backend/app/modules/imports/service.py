"""CSV import service. Parses the SAP export, validates every row first,
then inserts everything in one transaction (or nothing on any error).

Encoding: utf-8-sig first, cp1252 fallback (legacy exports carry mojibake
like "B�seler" otherwise). Empty strings become NULL, never stored as "".
"""
import csv
import io

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.subsidiaries import normalize_subsidiary
from app.modules.customers.models import Customer
from app.modules.equipment.models import Equipment, row_hash_of
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


def _clean(value: str | None) -> str | None:
    """Empty/blank strings become NULL; values are stripped."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


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
        }
        item_hash = row_hash_of(
            item["customer_id"],
            item["equipment_name"],
            item["machine_type"],
            item["component_type"],
            item["material_no"],
            item["purchase_date"],
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
    existing_hashes = _known_values(db, Equipment.row_hash, {e["row_hash"] for e in pending_equipment})

    report = ImportReport(
        dry_run=dry_run,
        total_rows=total_rows,
        customers_created=0,
        customers_skipped=0,
        equipment_created=0,
        equipment_skipped=0,
        errors=[],
        warnings=warnings,
    )
    new_customers = {cid: data for cid, data in customers.items() if cid not in existing_customers}
    report.customers_skipped = len(customers) - len(new_customers)
    report.customers_created = len(new_customers)
    new_equipment = [e for e in pending_equipment if e["row_hash"] not in existing_hashes]
    report.equipment_skipped = len(pending_equipment) - len(new_equipment) + file_dup_skipped + bare_skipped
    report.equipment_created = len(new_equipment)

    if dry_run:
        return report

    for cid, data in new_customers.items():
        db.add(Customer(customer_id=cid, **data))
    for item in new_equipment:
        db.add(Equipment(**item))
    db.commit()
    return report
