"""Basic-kit table.

Machine configuration (e.g. "CCS304") to the kit workload and the spare
parts price the pricing engine adds when the offer includes a basic kit.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, String, func, Numeric
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class BasicKit(Base):
    __tablename__ = "basic_kit"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    model: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    workload_basic_kit: Mapped[Decimal] = mapped_column(Numeric(10, 1), nullable=False, default=Decimal("0"))
    spare_parts: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
