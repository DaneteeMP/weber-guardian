"""Distances table.

Province (free text as it arrives in customer records) to travel
figures the pricing engine needs. Unknown provinces resolve to km 0
(no silent guess: the offer shows zero travel until the table is fed).
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, String, func, Numeric
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Distance(Base):
    __tablename__ = "distances"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    province: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    km: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))
    trip_hours: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
