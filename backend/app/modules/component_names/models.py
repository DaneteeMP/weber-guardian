"""Cleaned component name dictionary, one row per material number.

Populated by uploading names_dictionary.csv through the import endpoint. The
raw file repeats each material number many times, so this table stores the
collapsed form: the material number, the English name, the short code used to
look up a module workload, the component family and the German description.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ComponentName(Base):
    """One dictionary entry, keyed by the external material number."""

    __tablename__ = "component_names"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    material_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(256), nullable=False)
    # The file "Type" column: the short code the module workload table keys on.
    type_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    component_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # German text from the file. Kept because it is what the legacy workload
    # import was written against, so the two can be compared row by row.
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # How many raw file rows collapsed into this entry. Proves the cleanup and
    # makes a shrinking re-import visible instead of silent.
    source_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Set when the same material number arrived with more than one set of
    # values. Left unresolved on purpose: the importer shows these for review
    # rather than picking an arbitrary row.
    has_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ComponentWorkload(Base):
    __tablename__ = "component_workloads"
    __table_args__ = (
        UniqueConstraint("source_key", name="uq_component_workloads_source_key"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    component_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    # Stable technical identity. Unlike name, this is never edited when the
    # visible label is corrected or translated.
    source_key: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
    )

    workload: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    needs_review: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    legacy_type_code: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
