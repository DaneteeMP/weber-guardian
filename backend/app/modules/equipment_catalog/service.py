"""Global equipment-catalog operations and exact code resolution."""
from decimal import Decimal
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.equipment_catalog.models import EquipmentCatalogEntry, EquipmentCatalogMatch
from app.modules.equipment_catalog.schemas import EquipmentCatalogEntryIn


class EquipmentCatalogConflict(Exception):
    """Raised when a label or external equipment code is already assigned."""


def list_entries(db: Session) -> list[EquipmentCatalogEntry]:
    """List global catalog entries and their code associations."""
    statement = (
        select(EquipmentCatalogEntry)
        .options(selectinload(EquipmentCatalogEntry.matches))
        .order_by(EquipmentCatalogEntry.kind, EquipmentCatalogEntry.label)
    )
    return list(db.scalars(statement))


def get_entry(db: Session, entry_id: uuid.UUID) -> EquipmentCatalogEntry | None:
    """Fetch one catalog entry with its code associations."""
    statement = (
        select(EquipmentCatalogEntry)
        .options(selectinload(EquipmentCatalogEntry.matches))
        .where(EquipmentCatalogEntry.id == entry_id)
    )
    return db.scalar(statement)


def _new_matches(data: EquipmentCatalogEntryIn) -> list[EquipmentCatalogMatch]:
    return [
        EquipmentCatalogMatch(
            match_field=match.match_field,
            match_value=match.match_value,
            is_confirmed=match.is_confirmed,
        )
        for match in data.matches
    ]


def create_entry(db: Session, data: EquipmentCatalogEntryIn) -> EquipmentCatalogEntry:
    """Create a catalog entry and its associations in one transaction."""
    row = EquipmentCatalogEntry(
        kind=data.kind,
        label=data.label,
        workload=data.workload,
        matches=_new_matches(data),
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EquipmentCatalogConflict("Catalog label or equipment code is already assigned") from None
    db.refresh(row)
    return row


def update_entry(
    db: Session, entry_id: uuid.UUID, data: EquipmentCatalogEntryIn
) -> EquipmentCatalogEntry | None:
    """Replace entry fields and associations atomically."""
    row = get_entry(db, entry_id)
    if row is None:
        return None

    row.kind = data.kind
    row.label = data.label
    row.workload = data.workload
    row.matches.clear()
    try:
        db.flush()
        row.matches = _new_matches(data)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EquipmentCatalogConflict("Catalog label or equipment code is already assigned") from None
    db.refresh(row)
    return row


def delete_entry(db: Session, entry_id: uuid.UUID) -> bool:
    """Delete one entry and its associations. False when it does not exist."""
    row = get_entry(db, entry_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


def upsert_line_workload(
    db: Session,
    machine_type: str,
    workload: Decimal | None,
    label: str | None = None,
) -> EquipmentCatalogEntry:
    """Set the hours of one machine line, creating the entry when it is new.

    Used from the Offer badge when a line shows "Workload not configured":
    the entry's machine_type match is confirmed at the same time, so a
    configured line stops asking for review.
    """
    match = db.scalar(
        select(EquipmentCatalogMatch).where(
            EquipmentCatalogMatch.match_field == "machine_type",
            EquipmentCatalogMatch.match_value == machine_type,
        )
    )
    if match is not None:
        entry = get_entry(db, match.entry_id)
        entry.workload = workload
        match.is_confirmed = True
        db.commit()
        db.refresh(entry)
        return entry

    entry = EquipmentCatalogEntry(
        kind="line",
        label=(label or machine_type).strip(),
        workload=workload,
        matches=[
            EquipmentCatalogMatch(
                match_field="machine_type",
                match_value=machine_type,
                is_confirmed=True,
            )
        ],
    )
    db.add(entry)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise EquipmentCatalogConflict("Catalog label or equipment code is already assigned") from None
    db.refresh(entry)
    return entry


def resolve_line(
    db: Session, machine_type: str | None
) -> tuple[EquipmentCatalogEntry | None, bool] | None:
    """Resolve one machine_type to its catalog line.

    Returns None when the code means nothing to the catalog, otherwise the
    entry plus whether the match was confirmed. Unconfirmed entries are
    candidates the administrator still has to validate.
    """
    if not machine_type:
        return None
    statement = (
        select(EquipmentCatalogMatch.is_confirmed, EquipmentCatalogEntry)
        .join(EquipmentCatalogEntry, EquipmentCatalogMatch.entry_id == EquipmentCatalogEntry.id)
        .options(selectinload(EquipmentCatalogEntry.matches))
        .where(
            EquipmentCatalogEntry.kind == "line",
            EquipmentCatalogMatch.match_field == "machine_type",
            EquipmentCatalogMatch.match_value == machine_type,
        )
    )
    row = db.execute(statement).first()
    if row is None:
        return None
    is_confirmed, entry = row
    return entry, is_confirmed
