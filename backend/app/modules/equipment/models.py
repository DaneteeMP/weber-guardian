"""Equipment table.

One row per installed component at a customer. Rows are born in the CSV
import (F3). material_no is a PART reference, not an instance id: the same
"MSG 460-2" or "CCW05001" legitimately repeats across customers, machines
and even twice for one customer (same spare in two machines). Identity is
therefore the full-row hash (row_hash UNIQUE): exact duplicate rows are the
same installed instance and collapse; any differing field is a new one.
material_no is NULLABLE: machine-level rows (equipment + purchase date but
no component breakdown, e.g. "WLN10002-31803" with empty Material No.)
import as equipment with NULL material instead of being rejected.
customer_id references customers.customer_id (the SAP id from the file).
"""
import hashlib
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


def row_hash_of(
    customer_id: str | None,
    equipment_name: str | None,
    machine_type: str | None,
    component_type: str | None,
    material_no: str | None,
    purchase_date: str | None,
    site_hash: str | None = None,
) -> str:
    """Stable identity of an installed component row, including its site."""
    fields = (
        customer_id,
        equipment_name,
        machine_type,
        component_type,
        material_no,
        purchase_date,
    )
    values = tuple(v or "" for v in fields)
    if site_hash:
        values += (site_hash,)
    joined = "\x1f".join(values)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def site_hash_of(
    customer_id: str,
    physical_street: str | None,
    physical_city: str | None,
    physical_postal_code: str | None,
    physical_province: str | None,
    physical_country: str | None,
) -> str | None:
    """Return a stable site identity, or None when no address is present."""
    values = (
        physical_street,
        physical_city,
        physical_postal_code,
        physical_province,
        physical_country,
    )
    normalized = [" ".join((value or "").casefold().split()) for value in values]
    if not any(normalized[:4]):
        return None
    joined = "\x1f".join((customer_id, *normalized))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


class CustomerSite(Base):
    """A physical customer location shared by its installed equipment rows."""

    __tablename__ = "customer_sites"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    site_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    physical_street: Mapped[str | None] = mapped_column(String(255), nullable=True)
    physical_city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    physical_postal_code: Mapped[str | None] = mapped_column(String(24), nullable=True)
    physical_province: Mapped[str | None] = mapped_column(String(128), nullable=True)
    physical_country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    equipment: Mapped[list["Equipment"]] = relationship(back_populates="site")


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipment_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    machine_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    component_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    material_no: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    purchase_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    site_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("customer_sites.id", ondelete="SET NULL"), nullable=True, index=True
    )
    row_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    site: Mapped[CustomerSite | None] = relationship(back_populates="equipment")
