"""Cleaned component name dictionary, one row per material number.

Populated by uploading names_dictionary.csv through the import endpoint. The
raw file repeats each material number many times, so this table stores the
collapsed form: the material number, the English name, the short code used to
look up a legacy workload, the component family and the German description.

This table is a data source for resolution, not a workload catalog. A material
gets its hours through ``workload_rule_materials`` (see app.modules.workload_rules).
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ComponentName(Base):
    """One dictionary entry, keyed by the external material number."""

    __tablename__ = "component_names"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    material_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name_en: Mapped[str] = mapped_column(String(256), nullable=False)
    # The file "Type" column: the legacy short code (TblWorkLoad key). Used for
    # traceability and to recognise slicer codes; never the identity of a rule.
    type_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    component_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # German text from the file, kept for row-by-row comparison with the legacy data.
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)
    # How many raw file rows collapsed into this entry. Proves the cleanup and
    # makes a shrinking re-import visible instead of silent.
    source_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Set when the same material number arrived with more than one set of
    # values. Left unresolved on purpose: the importer shows these for review
    # rather than picking an arbitrary row.
    has_conflict: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
