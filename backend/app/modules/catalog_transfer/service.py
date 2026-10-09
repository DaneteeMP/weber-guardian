"""Read and write the portable catalog snapshot (workload rules + lines).

Export walks the two edited tables and the dictionary links. Import is an
idempotent upsert by natural key inside a single transaction:

    rule         -> name (UNIQUE)
    material link-> material_no (UNIQUE)
    line         -> label (UNIQUE)
    match        -> (match_field, match_value) (UNIQUE)

It is deliberately non-destructive: rows absent from the document are left
untouched, because an absence is not a delete instruction. A material whose
dictionary row does not exist in the target database is skipped and reported,
so the dictionary can be imported before the catalog.
"""
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.catalog_transfer.schemas import (
    CatalogDocument,
    CatalogImportReport,
    CatalogLine,
    CatalogRule,
)
from app.modules.component_names.models import ComponentName
from app.modules.equipment_catalog.models import EquipmentCatalogEntry, EquipmentCatalogMatch
from app.modules.workload_rules.models import WorkloadRule, WorkloadRuleMaterial


class CatalogImportError(Exception):
    """The document cannot be applied (it would break a catalog invariant)."""


def _hours(value: Decimal | None) -> str | None:
    """Decimal -> exact string, so the JSON keeps the stored scale."""
    return None if value is None else str(value)


def _parse_hours(value: str | None) -> Decimal | None:
    return None if value is None else Decimal(value)


def export_catalog(db: Session) -> CatalogDocument:
    """Snapshot every rule (with its materials) and every line (with its matches)."""
    rules = list(db.scalars(select(WorkloadRule).order_by(WorkloadRule.name)))
    links = db.execute(
        select(WorkloadRuleMaterial.workload_rule_id, WorkloadRuleMaterial.material_no).order_by(
            WorkloadRuleMaterial.material_no
        )
    ).all()
    materials_by_rule: dict[object, list[str]] = {}
    for rule_id, material_no in links:
        materials_by_rule.setdefault(rule_id, []).append(material_no)

    lines = list(
        db.scalars(
            select(EquipmentCatalogEntry)
            .options(selectinload(EquipmentCatalogEntry.matches))
            .order_by(EquipmentCatalogEntry.label)
        )
    )
    return CatalogDocument(
        workload_rules=[
            CatalogRule(
                name=rule.name,
                workload=_hours(rule.workload),
                legacy_type_code=rule.legacy_type_code,
                category=rule.category,
                needs_review=rule.needs_review,
                note=rule.note,
                materials=materials_by_rule.get(rule.id, []),
            )
            for rule in rules
        ],
        equipment_catalog=[
            CatalogLine(
                label=entry.label,
                workload=_hours(entry.workload),
                matches=[
                    {
                        "match_field": match.match_field,
                        "match_value": match.match_value,
                        "is_confirmed": match.is_confirmed,
                    }
                    for match in entry.matches
                ],
            )
            for entry in lines
        ],
    )


def import_catalog(db: Session, document: CatalogDocument) -> CatalogImportReport:
    """Apply the snapshot. One transaction: all of it lands, or none of it does."""
    report = CatalogImportReport()
    try:
        _import_rules(db, document.workload_rules, report)
        _import_lines(db, document.equipment_catalog, report)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise CatalogImportError(
            "the catalog changed concurrently, retry the import"
        ) from exc
    except Exception:
        db.rollback()
        raise
    return report


def _import_rules(
    db: Session, incoming: list[CatalogRule], report: CatalogImportReport
) -> None:
    existing = {rule.name: rule for rule in db.scalars(select(WorkloadRule))}
    rules_by_name: dict[str, WorkloadRule] = {}

    for item in incoming:
        workload = _parse_hours(item.workload)
        if workload is None and not item.needs_review:
            raise CatalogImportError(
                f"rule {item.name!r} has no hours and is not marked for review"
            )
        rule = existing.get(item.name)
        if rule is None:
            rule = WorkloadRule(
                name=item.name,
                workload=workload,
                legacy_type_code=item.legacy_type_code,
                category=item.category,
                needs_review=item.needs_review,
                note=item.note,
            )
            db.add(rule)
            existing[item.name] = rule
            report.rules_created += 1
        elif _apply_rule(rule, item, workload):
            report.rules_updated += 1
        rules_by_name[item.name] = rule

    # Assign ids to the new rules before linking materials to them.
    db.flush()
    _import_materials(db, incoming, rules_by_name, report)


def _apply_rule(rule: WorkloadRule, item: CatalogRule, workload: Decimal | None) -> bool:
    """Copy the file fields onto the stored rule. Returns True when something moved."""
    changed = False
    if rule.workload != workload:
        rule.workload = workload
        changed = True
    if rule.legacy_type_code != item.legacy_type_code:
        rule.legacy_type_code = item.legacy_type_code
        changed = True
    if rule.category != item.category:
        rule.category = item.category
        changed = True
    if rule.needs_review != item.needs_review:
        rule.needs_review = item.needs_review
        changed = True
    if rule.note != item.note:
        rule.note = item.note
        changed = True
    return changed


def _import_materials(
    db: Session,
    incoming: list[CatalogRule],
    rules_by_name: dict[str, WorkloadRule],
    report: CatalogImportReport,
) -> None:
    # A material belongs to exactly one rule, so the document may not list it twice.
    owner_of: dict[str, str] = {}
    for item in incoming:
        for material_no in item.materials:
            owner = owner_of.get(material_no)
            if owner is not None and owner != item.name:
                raise CatalogImportError(
                    f"material {material_no!r} is linked to two rules "
                    f"({owner!r} and {item.name!r})"
                )
            owner_of[material_no] = item.name

    wanted = set(owner_of)
    dictionary: set[str] = set()
    existing_links: dict[str, WorkloadRuleMaterial] = {}
    if wanted:
        dictionary = set(
            db.scalars(select(ComponentName.material_no).where(ComponentName.material_no.in_(wanted)))
        )
        existing_links = {
            link.material_no: link
            for link in db.scalars(
                select(WorkloadRuleMaterial).where(WorkloadRuleMaterial.material_no.in_(wanted))
            )
        }

    processed: set[str] = set()
    for item in incoming:
        rule = rules_by_name[item.name]
        for material_no in item.materials:
            if material_no in processed:
                continue  # duplicate inside the same rule
            processed.add(material_no)
            if material_no not in dictionary:
                report.materials_skipped.append(material_no)
                continue
            link = existing_links.get(material_no)
            if link is None:
                db.add(WorkloadRuleMaterial(workload_rule_id=rule.id, material_no=material_no))
                report.materials_linked += 1
            elif link.workload_rule_id == rule.id:
                report.materials_unchanged += 1
            else:
                link.workload_rule_id = rule.id
                report.materials_moved += 1


def _import_lines(
    db: Session, incoming: list[CatalogLine], report: CatalogImportReport
) -> None:
    existing = {
        entry.label: entry
        for entry in db.scalars(
            select(EquipmentCatalogEntry).options(selectinload(EquipmentCatalogEntry.matches))
        )
    }
    # A machine_type resolves to exactly one line: the match is unique catalog-wide.
    matches_by_key: dict[tuple[str, str], EquipmentCatalogMatch] = {}
    for entry in existing.values():
        for match in entry.matches:
            matches_by_key[(match.match_field, match.match_value)] = match

    owner_of: dict[tuple[str, str], str] = {}
    for item in incoming:
        for match in item.matches:
            key = (match.match_field, match.match_value)
            owner = owner_of.get(key)
            if owner is not None and owner != item.label:
                raise CatalogImportError(
                    f"match {match.match_value!r} points at two lines "
                    f"({owner!r} and {item.label!r})"
                )
            owner_of[key] = item.label

    for item in incoming:
        workload = _parse_hours(item.workload)
        entry = existing.get(item.label)
        if entry is None:
            entry = EquipmentCatalogEntry(label=item.label, workload=workload)
            db.add(entry)
            existing[item.label] = entry
            report.lines_created += 1
        elif entry.workload != workload:
            entry.workload = workload
            report.lines_updated += 1

        # Assign an id to a brand new entry before pointing matches at it.
        db.flush()

        for match in item.matches:
            key = (match.match_field, match.match_value)
            stored = matches_by_key.get(key)
            if stored is None:
                stored = EquipmentCatalogMatch(
                    entry_id=entry.id,
                    match_field=match.match_field,
                    match_value=match.match_value,
                    is_confirmed=match.is_confirmed,
                )
                db.add(stored)
                matches_by_key[key] = stored
                report.matches_created += 1
            elif stored.entry_id == entry.id:
                stored.is_confirmed = match.is_confirmed
                report.matches_unchanged += 1
            else:
                stored.entry_id = entry.id
                stored.is_confirmed = match.is_confirmed
                report.matches_moved += 1
