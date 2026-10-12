"""Basic-kit logic. Lookup plus admin create/delete (no updates: delete + recreate).

Kit keys follow the compact machine_type convention: suffix first, no space
("CCL304" = CCL + 304). The reference table and the admin UI spell the same
machine as "Model  Suffix" ("304 CCL"); canonical_model() rewrites that shape
into the compact key so every write (create, upsert) stores a key that the
offer lookup (BasicKit.model == equipment.machine_type) can match.
"""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.basic_kit.models import BasicKit
from app.modules.basic_kit.schemas import BasicKitCreate, BasicKitUpsert

# Slicer/variant codes that prefix the compact machine_type (suffix first).
# The same set the seed uses to build its rows from the reference table.
KIT_VARIANT_CODES = frozenset({"UB", "CCS", "CCL", "MLC", "MCS", "SLC", "RCS", "VPM", "CCB", "WSS"})


def canonical_model(model: str) -> str:
    """Rewrite a "Model  Suffix" key to the compact machine_type form.

    "304 CCL" becomes "CCL304"; the two-token shape is only rewritten when the
    last token is a known variant code. Bare codes ("KSG", "SHA") and proper
    names ("Thera 450-650", "KSG 470") have no rearranged compact form and are
    returned verbatim.
    """
    base, separator, suffix = model.partition(" ")
    if separator and suffix in KIT_VARIANT_CODES:
        return f"{suffix}{base}"
    return model


class KitAlreadyExists(Exception):
    """Domain error: model already registered. Router maps it to 409."""

    def __init__(self, model: str):
        super().__init__(f"Kit already exists: {model}")
        self.model = model


def get_kit(db: Session, model: str) -> BasicKit | None:
    """Fetch kit figures for a model, or None when the model has no kit."""
    return db.scalar(select(BasicKit).where(BasicKit.model == model))


def list_kits(db: Session, limit: int = 50, offset: int = 0) -> list[BasicKit]:
    """List all kits, ordered by model (admin config table)."""
    return list(db.scalars(select(BasicKit).order_by(BasicKit.model).limit(limit).offset(offset)))


def create_kit(db: Session, data: BasicKitCreate) -> BasicKit:
    """Register a new kit. Commits explicitly, rolls back on duplicate."""
    model = canonical_model(data.model)
    row = BasicKit(
        model=model,
        workload_basic_kit=data.workload_basic_kit,
        spare_parts=data.spare_parts,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise KitAlreadyExists(model) from None
    db.refresh(row)
    return row


def upsert_kit(db: Session, model: str, data: BasicKitUpsert) -> BasicKit:
    """Create or replace the kit row (admin config UI edit button)."""
    model = canonical_model(model)
    row = get_kit(db, model)
    if row is None:
        row = BasicKit(model=model, **data.model_dump())
        db.add(row)
    else:
        row.workload_basic_kit = data.workload_basic_kit
        row.spare_parts = data.spare_parts
    db.commit()
    db.refresh(row)
    return row


def delete_kit(db: Session, model: str) -> bool:
    """Remove a kit. False when missing."""
    row = get_kit(db, model)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True
