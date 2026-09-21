"""Equipment table.

One row per installed component at a customer. Rows are born in the CSV
import (F3). material_no is a PART reference, not an instance id: the same
"MSG 460-2" or "CCW05001" legitimately repeats across customers, machines
and even twice for one customer (same spare in two machines). Identity is
therefore the full-row hash (row_hash UNIQUE): exact duplicate rows are the
same installed instance and collapse; any differing field is a new one.
customer_id references customers.customer_id (the SAP id from the file).
"""
import hashlib
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def row_hash_of(
    customer_id: str | None,
    equipment_name: str | None,
    machine_type: str | None,
    component_type: str | None,
    material_no: str | None,
    purchase_date: str | None,
) -> str:
    """Stable identity of an import row: sha256 over the cleaned fields."""
    joined = "\x1f".join(v or "" for v in (customer_id, equipment_name, machine_type, component_type, material_no, purchase_date))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipment_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    machine_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    component_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    material_no: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    purchase_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    row_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
