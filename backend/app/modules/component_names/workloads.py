"""Workload Catalog identity, CSV reconciliation and CRUD.

The SAP dictionary is a source of product identity, not a place to store
workloads. This module turns it into a small workload master:

* ordinary products have one identity per normalized Component Type;
* Slicers have one identity per pure model, normalized by
  :func:`normalize_slicer_model`;
* ambiguous Slicer names become separate review rows rather than being guessed
  into a nearby model.

The technical source_key is derived from product identity and never from the
editable display name. Reimport only inserts missing keys; it does not update or
delete an existing workload row, so manual hours and labels survive imports.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
import re
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.component_names import service as component_name_service
from app.modules.component_names.models import ComponentName, ComponentWorkload
from app.modules.component_names.schemas import (
    ComponentWorkloadCreateIn,
    WorkloadImportReportOut,
)


class ComponentWorkloadNotFound(LookupError):
    """No workload product exists for the requested id."""


class ComponentWorkloadConflict(Exception):
    """Another workload product already uses the same stable identity."""


@dataclass(frozen=True)
class WorkloadProduct:
    """One product discovered from the internal component dictionary."""

    source_key: str
    name: str
    component_type: str
    legacy_type_code: str | None
    needs_review: bool


def _clean_text(value: str | None) -> str:
    return " ".join((value or "").split()).strip()


def _component_type_key(value: str) -> str:
    return _clean_text(value).casefold()


def _key_text(value: str) -> str:
    """Stable comparison form, independent of case and repeated whitespace."""
    return _clean_text(value).casefold()


def normalize_slicer_model(name_en: str | None, description: str | None = None) -> str | None:
    """Extract a pure Slicer product/model name without aggressive matching.

    Known variants are collapsed:

    * Slicer 405-Basic / Slicer 405-Extended -> Slicer 405
    * Slicer 604-1 / Slicer 604-2 -> Slicer 604
    * CCS 7000 E2 / CCS 7000 M6 / Slicer CCS 7000 -> Slicer 7000
    * Slicer weSLICE 4000 -> weSLICE 4000

    Any accessory wording rejects the candidate before matching. A bare CCS
    number is accepted only when it is not marked as accessories. If both
    source fields contain conflicting model candidates, the result is None.
    """
    primary = _clean_text(name_en)
    secondary = _clean_text(description)
    candidates = [value for value in (primary, secondary) if value]
    if not candidates:
        return None

    if any(re.search(r"\baccessor(?:y|ies)\b", value, re.IGNORECASE) for value in candidates):
        return None

    def parse(value: str) -> str | None:
        match = re.search(
            r"\bwe\s*slice\s+((?:\d{3,4})(?:\s*/\s*\d{3,4})?|7\s*x\s*00)\b",
            value,
            flags=re.IGNORECASE,
        )
        if match:
            model = re.sub(r"\s+", "", match.group(1)).upper()
            return f"weSLICE {model}"

        # CCS is an explicit Slicer model family in this dictionary. Ignore
        # suffixes like E2/M6 after the numeric model, but never accessory rows.
        match = re.search(r"\bCCS\s*([0-9]{3,4})\b", value, flags=re.IGNORECASE)
        if match:
            return f"Slicer {match.group(1)}"

        match = re.search(
            r"\b(?:computer\s*-?\s*slicer|slicer)\s+(?:CCS\s+)?([0-9]{3,4})"
            r"(?:\s*[-–]\s*(?:basic|extended|[12]))?\b",
            value,
            flags=re.IGNORECASE,
        )
        if match:
            return f"Slicer {match.group(1)}"

        match = re.search(r"\bTextor\s+TS\s*([0-9]{3})\s+Slicer\b", value, flags=re.IGNORECASE)
        if match:
            return f"Textor Slicer TS{match.group(1)}"

        if re.search(r"\bTextor\s+Slicer\b", value, flags=re.IGNORECASE):
            return "Textor Slicer"
        return None

    # The English product name is authoritative when it identifies a model.
    # The German description is only a fallback, never a conflicting override.
    for candidate in candidates:
        model = parse(candidate)
        if model is not None:
            return model
    return None


def workload_identity(
    component_type: str,
    name_en: str,
    description: str | None = None,
) -> tuple[str, str, bool]:
    """Return (source_key, canonical visible name, needs_review).

    Ordinary workload identity is the normalized Component Type. Slicer
    identity is the pure model. An ambiguous Slicer name uses a review key
    based on its normalized source name; it is not associated to a guessed
    model or to a material number.
    """
    display_type = _clean_text(component_type)
    normalized_type = _component_type_key(display_type)
    if not normalized_type:
        raise ValueError("component_type is required for a workload identity")

    if normalized_type == "slicer":
        model = normalize_slicer_model(name_en, description)
        if model is not None:
            return f"slicer:{_key_text(model)}", model, False
        review_name = _clean_text(name_en)
        if not review_name:
            review_name = "Slicer needs review"
        return f"slicer-review:{_key_text(review_name)}", review_name, True

    return f"component:{normalized_type}", display_type, False


def discover_products(names: list[ComponentName]) -> tuple[list[WorkloadProduct], int, int]:
    """Collapse dictionary material rows into stable workload products.

    Component Name rows are weighted by source_rows to choose stable display
    casing. Workloads are grouped by Component Type, not material number.
    Returns products, rows skipped for missing type, and ambiguous Slicer rows.
    """
    grouped: dict[str, list[tuple[ComponentName, str, str, bool]]] = defaultdict(list)
    missing_component_type = 0
    ambiguous_slicers = 0

    for name in names:
        component_type = _clean_text(name.component_type)
        if not component_type:
            missing_component_type += 1
            continue

        source_key, product_name, needs_review = workload_identity(
            component_type,
            name.name_en,
            name.description,
        )
        if component_type.casefold() == "slicer" and needs_review:
            ambiguous_slicers += 1
        grouped[source_key].append((name, product_name, component_type, needs_review))

    products: list[WorkloadProduct] = []
    for source_key, entries in sorted(grouped.items()):
        names_by_display: Counter[str] = Counter()
        types_by_display: Counter[str] = Counter()
        needs_review = False
        legacy_codes: set[str] = set()
        for name, product_name, component_type, row_needs_review in entries:
            weight = max(name.source_rows, 1)
            names_by_display[product_name] += weight
            types_by_display[component_type] += weight
            needs_review = needs_review or row_needs_review
            if name.type_code:
                legacy_codes.add(name.type_code)

        display_name = sorted(
            names_by_display.items(),
            key=lambda item: (-item[1], item[0].casefold(), item[0]),
        )[0][0]
        display_type = sorted(
            types_by_display.items(),
            key=lambda item: (-item[1], item[0].casefold(), item[0]),
        )[0][0]
        products.append(
            WorkloadProduct(
                source_key=source_key,
                name=display_name,
                component_type=display_type,
                legacy_type_code=next(iter(legacy_codes)) if len(legacy_codes) == 1 else None,
                needs_review=needs_review,
            )
        )

    return products, missing_component_type, ambiguous_slicers


def _filtered(
    db: Session,
    search: str | None,
    component_type: str | None,
    needs_review: bool | None,
):
    statement = select(ComponentWorkload)
    if search:
        pattern = f"%{_clean_text(search)}%"
        statement = statement.where(
            ComponentWorkload.name.ilike(pattern)
            | ComponentWorkload.component_type.ilike(pattern)
        )
    if component_type:
        statement = statement.where(ComponentWorkload.component_type == component_type)
    if needs_review is not None:
        statement = statement.where(ComponentWorkload.needs_review.is_(needs_review))
    return statement


def list_workloads(
    db: Session,
    search: str | None = None,
    component_type: str | None = None,
    needs_review: bool | None = None,
    limit: int = 200,
    offset: int = 0,
) -> list[ComponentWorkload]:
    statement = _filtered(db, search, component_type, needs_review).order_by(
        ComponentWorkload.component_type,
        ComponentWorkload.name,
        ComponentWorkload.id,
    )
    return list(db.scalars(statement.limit(limit).offset(offset)))


def count_workloads(
    db: Session,
    search: str | None = None,
    component_type: str | None = None,
    needs_review: bool | None = None,
) -> int:
    statement = _filtered(db, search, component_type, needs_review).order_by(None)
    return db.scalar(select(func.count()).select_from(statement.subquery())) or 0


def get_workload(db: Session, workload_id: uuid.UUID) -> ComponentWorkload:
    row = db.get(ComponentWorkload, workload_id)
    if row is None:
        raise ComponentWorkloadNotFound(str(workload_id))
    return row


def create_workload(db: Session, data: ComponentWorkloadCreateIn) -> ComponentWorkload:
    source_key, canonical_name, identity_needs_review = workload_identity(
        data.component_type,
        data.name,
    )
    row = ComponentWorkload(
        source_key=source_key,
        name=canonical_name if data.component_type.casefold() == "slicer" and not identity_needs_review else data.name,
        component_type=_clean_text(data.component_type),
        workload=data.workload,
        needs_review=(
            identity_needs_review
            or (
                data.needs_review
                if data.needs_review is not None
                else data.workload is None
            )
        ),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ComponentWorkloadConflict(source_key) from None
    db.refresh(row)
    return row


def update_workload(
    db: Session,
    workload_id: uuid.UUID,
    changes: dict,
) -> ComponentWorkload:
    row = get_workload(db, workload_id)
    next_workload = changes.get("workload", row.workload)
    if changes.get("needs_review") is not None:
        next_needs_review = changes["needs_review"]
    elif "workload" in changes:
        next_needs_review = next_workload is None
    else:
        next_needs_review = row.needs_review
    if next_workload is None and next_needs_review is False:
        raise ValueError("a workload without hours must remain marked for review")

    if "name" in changes and changes["name"] is not None:
        row.name = _clean_text(changes["name"])
    if "workload" in changes:
        row.workload = changes["workload"]
    row.needs_review = next_needs_review
    db.commit()
    db.refresh(row)
    return row


def delete_workload(db: Session, workload_id: uuid.UUID) -> bool:
    row = db.get(ComponentWorkload, workload_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


def import_workload_catalog(db: Session, raw: bytes) -> WorkloadImportReportOut:
    """Import SAP names and create only missing workload products atomically.

    Existing source keys are never updated or deleted: a manually configured
    workload (and manual label/review decision) survives every reimport.
    """
    try:
        dictionary_report = component_name_service.import_dictionary(db, raw, commit=False)
        names = list(db.scalars(select(ComponentName)))
        products, missing_types, _ambiguous_slicers = discover_products(names)
        existing_keys = set(
            db.scalars(select(ComponentWorkload.source_key))
        )

        created = 0
        review_created = 0
        preserved = 0
        for product in products:
            if product.source_key in existing_keys:
                preserved += 1
                continue
            db.add(
                ComponentWorkload(
                    source_key=product.source_key,
                    name=product.name,
                    component_type=product.component_type,
                    workload=None,
                    needs_review=True,
                    legacy_type_code=product.legacy_type_code,
                )
            )
            created += 1
            review_created += 1
            existing_keys.add(product.source_key)

        db.commit()
    except Exception:
        db.rollback()
        raise

    return WorkloadImportReportOut(
        encoding=dictionary_report.encoding,
        rows_read=dictionary_report.rows_read,
        rows_blank=dictionary_report.rows_blank,
        rows_without_material_no=dictionary_report.rows_without_material_no,
        source_entries=dictionary_report.entries_written,
        source_conflicts=dictionary_report.entries_with_conflict,
        products_discovered=len(products),
        workloads_created=created,
        workloads_preserved=preserved,
        workloads_needing_review_created=review_created,
        rows_without_component_type=missing_types,
    )
