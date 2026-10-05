"""Global equipment catalog entries and their exact equipment-code matches."""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class EquipmentCatalogEntry(Base):
    """One catalog line. Maintenance is priced workload times the branch
    technician rate, so an entry carries hours, never an amount."""
    __tablename__ = "equipment_catalog"
    __table_args__ = (
        UniqueConstraint("label", name="uq_equipment_catalog_label"),
        CheckConstraint("kind = 'line'", name="ck_equipment_catalog_kind"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kind: Mapped[str] = mapped_column(String(8), nullable=False, default="line")
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    workload: Mapped[Decimal | None] = mapped_column(Numeric(10, 1), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    matches: Mapped[list["EquipmentCatalogMatch"]] = relationship(
        back_populates="entry", cascade="all, delete-orphan", order_by="EquipmentCatalogMatch.match_value"
    )


class EquipmentCatalogMatch(Base):
    """Exact external equipment code associated with a catalog entry."""

    __tablename__ = "equipment_catalog_matches"
    __table_args__ = (
        UniqueConstraint("match_field", "match_value", name="uq_equipment_catalog_match_value"),
        # Modules resolve through the dictionary table, not this catalog, so
        # only machine_type matches exist.
        CheckConstraint("match_field = 'machine_type'", name="ck_equipment_catalog_match_field"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entry_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("equipment_catalog.id", ondelete="CASCADE"), nullable=False, index=True
    )
    match_field: Mapped[str] = mapped_column(String(16), nullable=False)
    match_value: Mapped[str] = mapped_column(String(64), nullable=False)
    is_confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    entry: Mapped[EquipmentCatalogEntry] = relationship(back_populates="matches")
