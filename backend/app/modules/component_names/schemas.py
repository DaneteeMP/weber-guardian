"""Pydantic contracts for the cleaned component name dictionary."""
from datetime import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field


class ComponentNameOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    material_no: str
    name_en: str
    type_code: str | None
    component_type: str | None
    description: str | None
    source_rows: int
    has_conflict: bool
    created_at: datetime


class ComponentNameUpdateIn(BaseModel):
    """Manual edit of a cleaned row, used to settle conflicting entries."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name_en: str | None = Field(default=None, min_length=1, max_length=256)
    type_code: str | None = Field(default=None, max_length=64)
    component_type: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    has_conflict: bool | None = None


class ImportReportOut(BaseModel):
    """What one dictionary import did, so a bad file is visible, not silent.

    The file is the legacy German/English export, so every number here can go
    wrong in a way that must be read, not guessed at.
    """

    encoding: str
    rows_read: int
    rows_blank: int
    rows_without_material_no: int
    material_numbers_without_name: int
    entries_written: int
    entries_total_after: int
    entries_with_conflict: int
    duplicate_rows_collapsed: int
    stale_entries_deleted: int
    unmapped_material_numbers: list[str] = Field(default_factory=list)
