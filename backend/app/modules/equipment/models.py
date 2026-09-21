"""Equipment table.

One row per machine installed at a customer. Rows are born in the CSV
import (F3): several rows may share equipment_name (e.g. "304-565") while
material_no stays unique per component ("CCS 304-565", "304-565-Z").
customer_id references customers.customer_id (the SAP id from the file).
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False, index=True
    )
    equipment_name: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    machine_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    component_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    material_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    purchase_date: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
