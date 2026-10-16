"""Responsible logic. Scoped CRUD: the router enforces admin + subsidiary scope.

Offers store responsible_person as free text, so deleting or renaming here
never breaks history. The dropdown simply stops offering the name.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.responsibles.models import Responsible
from app.modules.responsibles.schemas import ResponsibleCreate, ResponsibleUpdate
from app.modules.subsidiaries.models import Subsidiary


class SubsidiaryNotFound(Exception):
    """Domain error: the subsidiary is not in the catalog. Router maps it to 404."""

    def __init__(self, subsidiary_id: str):
        super().__init__(f"Unknown subsidiary: {subsidiary_id}")
        self.subsidiary_id = subsidiary_id


class ResponsibleAlreadyExists(Exception):
    """Domain error: name already registered for the subsidiary. Router maps it to 409."""

    def __init__(self, subsidiary_id: str, name: str):
        super().__init__(f"Responsible already exists: {name} ({subsidiary_id})")
        self.subsidiary_id = subsidiary_id
        self.name = name


def _require_subsidiary(db: Session, subsidiary_id: str) -> None:
    """Refuse invented subsidiaries instead of letting the FK fail cryptically."""
    if db.scalar(select(Subsidiary).where(Subsidiary.name == subsidiary_id)) is None:
        raise SubsidiaryNotFound(subsidiary_id)


def list_responsibles(db: Session, subsidiary_id: str) -> list[Responsible]:
    """Active first, then by name: the dropdown order."""
    return list(
        db.scalars(
            select(Responsible)
            .where(Responsible.subsidiary_id == subsidiary_id)
            .order_by(Responsible.active.desc(), Responsible.name)
        )
    )


def get_responsible(db: Session, responsible_id: uuid.UUID) -> Responsible | None:
    """Fetch one row by id, or None when missing."""
    return db.scalar(select(Responsible).where(Responsible.id == responsible_id))


def create_responsible(db: Session, data: ResponsibleCreate) -> Responsible:
    """Register a name for a subsidiary. Commits explicitly, rolls back on duplicate."""
    _require_subsidiary(db, data.subsidiary_id)
    row = Responsible(subsidiary_id=data.subsidiary_id, name=data.name.strip(), active=True)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ResponsibleAlreadyExists(data.subsidiary_id, row.name) from None
    db.refresh(row)
    return row


def update_responsible(
    db: Session, responsible_id: uuid.UUID, data: ResponsibleUpdate
) -> Responsible | None:
    """Rename and/or (de)activate. None when missing; 409 on rename collision."""
    row = get_responsible(db, responsible_id)
    if row is None:
        return None
    if data.name is not None:
        row.name = data.name.strip()
    if data.active is not None:
        row.active = data.active
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ResponsibleAlreadyExists(row.subsidiary_id, row.name) from None
    db.refresh(row)
    return row


def delete_responsible(db: Session, responsible_id: uuid.UUID) -> bool:
    """Remove a name. False when missing. Saved offers keep their free text."""
    row = get_responsible(db, responsible_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True
