"""Customers table.

- id: internal PK (UUID). Used by FKs. Never changes.
- customer_id: EXTERNAL identifier (SAP/Salesforce/Weber). UNIQUE, only for
  lookup and sync. Never the PK: if SAP changes it, nothing internal breaks.
- subsidiary_id: owning subsidiary (e.g. "ES"). NULL = visible to every scope.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    province: Mapped[str | None] = mapped_column(String(128), nullable=True)
    country: Mapped[str | None] = mapped_column(String(64), nullable=True)
    subsidiary_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
