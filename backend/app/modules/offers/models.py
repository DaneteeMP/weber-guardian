"""Offers tables.

- Offer: header + pricing snapshot (all money Numeric, EUR explicit).
  customer_id references customers.customer_id (the external SAP id used
  in URLs), so offers stay linked even if internal UUIDs change layers.
- OfferItem: lines of one offer. FK with ON DELETE CASCADE: deleting an
  offer removes its items.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Offer(Base):
    __tablename__ = "offers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    id_guardian_offer: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    customer_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="Draft")
    responsible_person: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    inspection_frequency: Mapped[str | None] = mapped_column(String(32), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")

    work_hours: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))
    bk_hours: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))
    report_hours: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))
    total_hours: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))
    trip_hours: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))

    trip_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    diets: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    hotel_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    hours_import: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    bk_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    total_end: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))

    general_comments: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    items: Mapped[list["OfferItem"]] = relationship(
        back_populates="offer", cascade="all, delete-orphan", passive_deletes=True
    )


class OfferItem(Base):
    __tablename__ = "offer_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    offer_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    row_no: Mapped[int] = mapped_column(nullable=False, default=1)
    equipment: Mapped[str | None] = mapped_column(String(64), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    import_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    workload: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))

    offer: Mapped[Offer] = relationship(back_populates="items")
