"""Responsibles table.

One row per person who can own an offer, scoped by subsidiary. Offers store
responsible_person as free text, so renaming or deleting here never breaks
history; this table only feeds the dropdown.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Responsible(Base):
    __tablename__ = "responsibles"
    __table_args__ = (UniqueConstraint("subsidiary_id", "name", name="uq_responsibles_subsidiary_name"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    subsidiary_id: Mapped[str] = mapped_column(String(64), ForeignKey("subsidiaries.name"), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
