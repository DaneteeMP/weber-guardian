"""Prices table.

One row per subsidiary with the rates the pricing engine needs.
Seeded with the demo values the UI used to type by hand; each filial
adjusts its own row later (admin CRUD arrives in F4).
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, String, func, Numeric
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class PriceList(Base):
    __tablename__ = "prices"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    subsidiary_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")
    km_rate: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False, default=Decimal("0"))
    tech_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    diet_full_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    diet_half_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    hotel_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0"))
    # Client discount on hours, per subsidiary. Legacy WeberAssistant kept one
    # constant (0.15); each filial now sets its own from Settings.
    discount_rate: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False, default=Decimal("0.15"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
