"""CSV import service. Parses the SAP export, validates every row first,
then inserts everything in one transaction (or nothing on any error).

Encoding: utf-8-sig first, cp1252 fallback (legacy exports carry mojibake
like "B�seler" otherwise). Empty strings become NULL, never stored as "".
"""
import csv
import io

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.equipment.models import Equipment
from app.modules.imports.schemas import ImportReport, RowError

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


def _clean(value: str | None) -> str | None:
    """Empty/blank strings become NULL; values are stripped."""
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def run_import(db: Session, content: bytes, subsidiary_id: str | None, dry_run: bool) -> ImportReport:
    """Validate the whole file, then insert atomically unless dry_run."""
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
    customers: dict[str, dict] = {}
    seen_materials: set[str] = set()
    pending_equipment: list[dict] = []
    total_rows = 0

    for lineno, raw in enumerate(reader, start=2):
        if all((v or "").strip() == "" for v in raw.values()):
            continue
        total_rows += 1
        sap_id = _clean(raw.get(HEADER_SAP))
        account = _clean(raw.get(HEADER_ACCOUNT))
        material = _clean(raw.get(HEADER_MATERIAL))
        if not sap_id:
            errors.append(RowError(line=lineno, reason="empty SAP Debitor ID"))
            continue
        if not account:
            errors.append(RowError(line=lineno, reason=f"{sap_id}: empty Account Name"))
            continue
        if not material:
            errors.append(RowError(line=lineno, reason=f"{sap_id}: empty Material No."))
            continue
        known = customers.get(sap_id)
        if known is None:
            customers[sap_id] = {
                "account_name": account,
                "country": _clean(raw.get(HEADER_COUNTRY)),
                "subsidiary_id": subsidiary_id,
            }
        elif known["account_name"] != account:
            errors.append(
                RowError(line=lineno, reason=f"{sap_id}: conflicting Account Name ('{account}')")
            )
            continue
        if material in seen_materials:
            errors.append(RowError(line=lineno, reason=f"{sap_id}: duplicate Material No. in file ('{material}')"))
            continue
        seen_materials.add(material)
        pending_equipment.append(
            {
                "customer_id": sap_id,
                "equipment_name": _clean(raw.get(HEADER_EQUIPMENT)),
                "machine_type": _clean(raw.get(HEADER_MACHINE)),
                "component_type": _clean(raw.get(HEADER_COMPONENT)),
                "material_no": material,
                "purchase_date": _clean(raw.get(HEADER_PURCHASE)),
            }
        )

    if errors:
        return ImportReport(
            dry_run=dry_run,
            total_rows=total_rows,
            customers_created=0,
            customers_skipped=0,
            equipment_created=0,
            equipment_skipped=0,
            errors=errors,
        )

    existing_customers = set(
        db.scalars(select(Customer.customer_id).where(Customer.customer_id.in_(customers.keys()))).all()
    )
    existing_materials = set(
        db.scalars(select(Equipment.material_no).where(Equipment.material_no.in_(seen_materials))).all()
    )

    report = ImportReport(
        dry_run=dry_run,
        total_rows=total_rows,
        customers_created=0,
        customers_skipped=0,
        equipment_created=0,
        equipment_skipped=0,
        errors=[],
    )
    new_customers = {cid: data for cid, data in customers.items() if cid not in existing_customers}
    report.customers_skipped = len(customers) - len(new_customers)
    report.customers_created = len(new_customers)
    new_equipment = [e for e in pending_equipment if e["material_no"] not in existing_materials]
    report.equipment_skipped = len(pending_equipment) - len(new_equipment)
    report.equipment_created = len(new_equipment)

    if dry_run:
        return report

    for cid, data in new_customers.items():
        db.add(Customer(customer_id=cid, **data))
    for item in new_equipment:
        db.add(Equipment(**item))
    db.commit()
    return report
