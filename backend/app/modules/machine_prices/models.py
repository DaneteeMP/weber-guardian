"""Machine-price table.

Yearly contract price (excl. VAT) and inspections per year for a machine
model, as quoted in Guardian annexes (e.g. "804-227: EUR 2,900/year,
4 inspections"). Seeded per subsidiary need; admin UI edits the rest.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, String, func, Integer, Numeric
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class MachinePrice(Base):
    __tablename__ = "machine_prices"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    model: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    annual_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    inspections_per_year: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="EUR")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
