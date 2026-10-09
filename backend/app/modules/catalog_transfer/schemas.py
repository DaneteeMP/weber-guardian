"""Portable JSON contract for moving the editable catalog between databases.

This is a file format, not an HTTP resource: a snapshot of the two tables an
administrator edits live (``workload_rules`` with its material links, and the
machine ``equipment_catalog`` lines with their matches). The dictionary
(``component_names``) has its own CSV import/export and is not duplicated here.

Hours travel as strings ("5.00"), never as JSON numbers: the round trip must
return the same Decimal the database stored, and a float cannot promise that.

Why it exists: the legacy baseline is seeded by migrations, but the rules and
lines edited afterwards only live in one database. Export/import lets a new
environment (the deployed app) receive that work without retyping it.
"""
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _valid_hours(value: str | None) -> str | None:
    """Accept only a non-negative decimal string, or None (pending hours)."""
    if value is None:
        return None
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"workload is not a number: {value!r}") from exc
    if parsed < 0:
        raise ValueError("workload must be >= 0")
    return value


class CatalogRule(BaseModel):
    """One workload rule and the dictionary materials linked to it."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    name: str = Field(min_length=1, max_length=128)
    # None means "waiting for hours", exactly like a rule with workload NULL.
    workload: str | None = None
    legacy_type_code: str | None = Field(default=None, max_length=16)
    category: Literal["legacy", "carried_over", "manual"] = "manual"
    needs_review: bool = False
    note: str | None = Field(default=None, max_length=512)
    materials: list[str] = Field(default_factory=list)

    @field_validator("workload")
    @classmethod
    def _check_workload(cls, value: str | None) -> str | None:
        return _valid_hours(value)


class CatalogMatch(BaseModel):
    """One exact equipment code of a catalog line (only machine_type today)."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    match_field: Literal["machine_type"] = "machine_type"
    match_value: str = Field(min_length=1, max_length=64)
    is_confirmed: bool = False


class CatalogLine(BaseModel):
    """One machine line: its hours and the equipment codes that resolve to it."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    label: str = Field(min_length=1, max_length=128)
    workload: str | None = None
    matches: list[CatalogMatch] = Field(default_factory=list)

    @field_validator("workload")
    @classmethod
    def _check_workload(cls, value: str | None) -> str | None:
        return _valid_hours(value)


class CatalogDocument(BaseModel):
    """The whole snapshot. ``version`` lets a reader reject a newer format."""

    model_config = ConfigDict(extra="forbid")

    format: Literal["weberguardian.catalog"] = "weberguardian.catalog"
    version: int = 1
    workload_rules: list[CatalogRule] = Field(default_factory=list)
    equipment_catalog: list[CatalogLine] = Field(default_factory=list)


class CatalogImportReport(BaseModel):
    """What the import changed. Nothing is deleted, so there is no delete count."""

    rules_created: int = 0
    rules_updated: int = 0
    materials_linked: int = 0
    materials_moved: int = 0
    materials_unchanged: int = 0
    materials_skipped: list[str] = Field(default_factory=list)
    lines_created: int = 0
    lines_updated: int = 0
    matches_created: int = 0
    matches_moved: int = 0
    matches_unchanged: int = 0
