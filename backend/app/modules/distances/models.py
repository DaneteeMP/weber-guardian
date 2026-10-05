"""Distances table.

Province (free text as it arrives in customer records) to travel
figures the pricing engine needs. Unknown provinces resolve to km 0
(no silent guess: the offer shows zero travel until the table is fed).
"""
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, String, UniqueConstraint, func, Numeric
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Distance(Base):
    __tablename__ = "distances"
    __table_args__ = (
        UniqueConstraint("subsidiary_id", "province", name="uq_distances_subsidiary_province"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    subsidiary_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("subsidiaries.name"), nullable=False, index=True
    )
    province: Mapped[str] = mapped_column(String(128), nullable=False)
    province_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    region: Mapped[str | None] = mapped_column(String(128), nullable=True)
    capital: Mapped[str | None] = mapped_column(String(128), nullable=True)
    reference_city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    service_center: Mapped[str | None] = mapped_column(String(64), nullable=True)
    origin_city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    km: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))
    driving_hours: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    # Total one-way travel time; for Italy this includes ferry time where applicable.
    trip_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    itinerary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    route_data_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
