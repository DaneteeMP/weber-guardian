"""Import and clean the legacy component dictionary.

The source file is a semicolon-separated export containing equipment/components
that may appear many times because the same product is installed on many
machines.

Important domain rule:
    The part of Material No. after the first "-" is a unit/serial identifier.
    It is NOT part of the catalogue identity.

Examples:
    CCE04001           -> CCE04001
    CCE04001-10591     -> CCE04001
    TSX06001           -> TSX06001
    TSX06001-10261     -> TSX06001

The importer therefore produces one catalogue entry per base material number.

Workloads are deliberately not handled here. They belong to the equipment
catalogue/workload configuration and are preserved independently when the
dictionary is re-imported.
"""

import csv
import io
from collections import Counter
from dataclasses import dataclass, field

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.component_names.models import ComponentName
from app.modules.component_names.schemas import ImportReportOut


EXPECTED_COLUMNS = (
    "component name en",
    "type",
    "material no.",
    "component type",
    "description",
)


class DictionaryFileError(ValueError):
    """The uploaded file is not a valid component dictionary."""


class ComponentNameNotFound(LookupError):
    """No catalogue entry exists for the requested material number."""


@dataclass
class CleanEntry:
    """One normalized catalogue entry."""

    material_no: str
    name_en: str | None
    type_code: str | None
    component_type: str | None
    description: str | None
    source_rows: int
    has_conflict: bool = False


@dataclass
class CleanResult:
    """Result of cleaning the source file before touching the database."""

    encoding: str
    rows_read: int = 0
    rows_blank: int = 0
    rows_without_material_no: int = 0
    material_numbers_without_name: int = 0
    duplicate_rows_collapsed: int = 0
    entries: list[CleanEntry] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    unmapped_material_numbers: list[str] = field(default_factory=list)


def _clean_cell(value: str) -> str:
    """Normalize whitespace without changing the actual content."""
    return " ".join(value.split())


def normalize_material_no(material_no: str) -> str:
    """Return the catalogue material number without a unit/serial suffix.

    The part after the first '-' is a unit/serial only when the part before it
    is a single token. Examples:

        CCE04001-10591  -> CCE04001   (serial suffix stripped)
        TSX06001-10261  -> TSX06001
        CCS 302-376     -> CCS 302-376 (the '-' belongs to the model, kept)
        CCS 302-376-Z   -> CCS 302-376-Z

    A prefix with whitespace (``"CCS 302"``) is a model, not a serial base, so
    the whole material number is the identity. Material numbers without '-' are
    left untouched.
    """
    base, separator, _ = material_no.partition("-")
    base = base.strip()
    if separator and base and " " not in base:
        return base
    return material_no.strip()


def legacy_base_material_no(material_no: str) -> str:
    """Collapse at the first '-' regardless of whitespace.

    Kept only to look up dictionaries that were imported before
    :func:`normalize_material_no` became model-aware. New imports use
    :func:`normalize_material_no`.
    """
    return material_no.split("-", 1)[0].strip()


_base_material_no = normalize_material_no


def decode_dictionary(raw: bytes) -> tuple[str, str]:
    """Decode an exported dictionary.

    UTF-8 is preferred. Legacy exports use cp1252.
    """
    try:
        return raw.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        return raw.decode("cp1252"), "cp1252"


def _header_indexes(header: list[str]) -> tuple[int, int, int, int, int]:
    """Find expected columns independently of their order."""
    normalized = [
        _clean_cell(cell).lower().lstrip("\ufeff")
        for cell in header
    ]

    try:
        return tuple(
            normalized.index(column)
            for column in EXPECTED_COLUMNS
        )  # type: ignore[return-value]
    except ValueError as exc:
        raise DictionaryFileError(
            f"unexpected header {header!r}; "
            f"expected columns {list(EXPECTED_COLUMNS)}"
        ) from exc


def _choose_value(counter: Counter[str]) -> str | None:
    """Choose a deterministic non-empty value.

    This is only used when all non-empty source values agree or when the
    operator has to see a deterministic candidate in the UI.

    Conflicts are still reported separately and are never silently considered
    resolved.
    """
    values = {
        value: count
        for value, count in counter.items()
        if value
    }

    if not values:
        return None

    return sorted(
        values.items(),
        key=lambda item: (-item[1], item[0]),
    )[0][0]


def _field_has_conflict(counter: Counter[str]) -> bool:
    """Whether a field contains more than one distinct non-empty value."""
    values = {
        value
        for value in counter
        if value
    }
    return len(values) > 1


def parse_and_clean(raw: bytes) -> CleanResult:
    """Parse and normalize the legacy dictionary.

    No database access happens here.

    The important normalization is:
        material_no -> material_no.split("-", 1)[0]

    Thus all unit/serial variants of the same product become one catalogue
    entry.

    Material numbers without a Component Name EN are reported and excluded
    from the cleaned catalogue because ComponentName.name_en is required.
    """
    text, encoding = decode_dictionary(raw)

    reader = csv.reader(
        io.StringIO(text, newline=""),
        delimiter=";",
    )

    try:
        header = next(reader)
    except StopIteration as exc:
        raise DictionaryFileError("file is empty") from exc

    (
        i_name,
        i_type,
        i_material,
        i_component_type,
        i_description,
    ) = _header_indexes(header)

    # material_no -> field -> Counter(values)
    groups: dict[str, dict[str, Counter[str]]] = {}
    source_row_counts: Counter[str] = Counter()

    result = CleanResult(encoding=encoding)

    required_index = max(
        i_name,
        i_type,
        i_material,
        i_component_type,
        i_description,
    )

    for row_number, row in enumerate(reader, start=2):
        result.rows_read += 1

        cells = [_clean_cell(cell) for cell in row]

        if not any(cells):
            result.rows_blank += 1
            continue

        if len(cells) <= required_index:
            raise DictionaryFileError(
                f"row {row_number} has {len(cells)} columns; "
                f"expected at least {required_index + 1}: {row!r}"
            )

        raw_material_no = cells[i_material]

        if not raw_material_no:
            result.rows_without_material_no += 1
            continue

        material_no = _base_material_no(raw_material_no)

        if not material_no:
            result.rows_without_material_no += 1
            continue

        source_row_counts[material_no] += 1

        values = {
            "name_en": cells[i_name],
            "type_code": cells[i_type],
            "component_type": cells[i_component_type],
            "description": cells[i_description],
        }

        counters = groups.setdefault(
            material_no,
            {
                field_name: Counter()
                for field_name in values
            },
        )

        for field_name, value in values.items():
            if value:
                counters[field_name][value] += 1

    for material_no, counters in sorted(groups.items()):
        name_en = _choose_value(counters["name_en"])

        # A catalogue entry requires an English component name.
        if not name_en:
            result.material_numbers_without_name += 1
            result.unmapped_material_numbers.append(material_no)
            continue

        field_conflicts = any(
            _field_has_conflict(counter)
            for counter in counters.values()
        )

        if field_conflicts:
            result.conflicts.append(material_no)

        entry = CleanEntry(
            material_no=material_no,
            name_en=name_en,
            type_code=_choose_value(counters["type_code"]),
            component_type=_choose_value(
                counters["component_type"]
            ),
            description=_choose_value(
                counters["description"]
            ),
            source_rows=source_row_counts[material_no],
            has_conflict=field_conflicts,
        )

        result.entries.append(entry)

    result.duplicate_rows_collapsed = (
        result.rows_read
        - result.rows_blank
        - result.rows_without_material_no
        - result.material_numbers_without_name
        - len(result.entries)
    )

    return result


def _filtered(
    db: Session,
    search: str | None,
    component_type: str | None,
    only_conflicts: bool,
):
    """Shared filtering for catalogue listing and count."""
    statement = select(ComponentName)

    if search:
        pattern = f"%{_clean_cell(search)}%"

        statement = statement.where(
            ComponentName.material_no.ilike(pattern)
            | ComponentName.name_en.ilike(pattern)
            | ComponentName.description.ilike(pattern)
        )

    if component_type:
        statement = statement.where(
            ComponentName.component_type == component_type
        )

    if only_conflicts:
        statement = statement.where(
            ComponentName.has_conflict.is_(True)
        )

    return statement


def list_component_names(
    db: Session,
    search: str | None = None,
    component_type: str | None = None,
    only_conflicts: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[ComponentName]:
    """Return one page of the normalized catalogue."""
    statement = (
        _filtered(
            db,
            search,
            component_type,
            only_conflicts,
        )
        .order_by(ComponentName.material_no)
        .limit(limit)
        .offset(offset)
    )

    return list(db.scalars(statement))


def count_component_names(
    db: Session,
    search: str | None = None,
    component_type: str | None = None,
    only_conflicts: bool = False,
) -> int:
    """Return the number of catalogue entries matching the filters."""
    statement = _filtered(
        db,
        search,
        component_type,
        only_conflicts,
    ).order_by(None)

    return (
        db.scalar(
            select(func.count())
            .select_from(statement.subquery())
        )
        or 0
    )


def get_component_name(
    db: Session,
    material_no: str,
) -> ComponentName:
    """Get one normalized catalogue entry."""
    material_no = _base_material_no(material_no)

    row = db.scalar(
        select(ComponentName).where(
            ComponentName.material_no == material_no
        )
    )

    if row is None:
        raise ComponentNameNotFound(material_no)

    return row


EDITABLE_FIELDS = (
    "name_en",
    "type_code",
    "component_type",
    "description",
    "has_conflict",
)


def update_component_name(
    db: Session,
    material_no: str,
    changes: dict,
) -> ComponentName:
    """Apply a manual correction to a catalogue entry."""
    unexpected = sorted(
        set(changes) - set(EDITABLE_FIELDS)
    )

    if unexpected:
        raise ValueError(
            f"cannot edit fields: {unexpected}"
        )

    row = get_component_name(db, material_no)

    for field_name in EDITABLE_FIELDS:
        if field_name in changes:
            value = changes[field_name]

            if field_name != "has_conflict" and isinstance(value, str):
                value = _clean_cell(value)

            setattr(row, field_name, value)

    db.commit()
    db.refresh(row)

    return row


def export_component_names(db: Session) -> str:
    """Export the normalized catalogue."""
    buffer = io.StringIO()

    writer = csv.writer(
        buffer,
        delimiter=";",
        lineterminator="\r\n",
    )

    writer.writerow(
        [
            "Component Name EN",
            "Type",
            "Material No.",
            "Component Type",
            "Description",
        ]
    )

    statement = select(ComponentName).order_by(
        ComponentName.material_no
    )

    for row in db.scalars(statement):
        writer.writerow(
            [
                row.name_en or "",
                row.type_code or "",
                row.material_no,
                row.component_type or "",
                row.description or "",
            ]
        )

    return buffer.getvalue()


def import_dictionary(
    db: Session,
    raw: bytes,
    *,
    commit: bool = True,
) -> ImportReportOut:
    """Import the legacy dictionary atomically.

    The source file owns the descriptive catalogue fields.

    Workload data is intentionally not touched here. The workload import
    endpoint passes commit=False so dictionary replacement and workload
    reconciliation share one database transaction.
    """
    cleaned = parse_and_clean(raw)

    incoming = {
        entry.material_no
        for entry in cleaned.entries
    }

    existing = {
        row.material_no: row
        for row in db.scalars(
            select(ComponentName)
        )
    }

    for entry in cleaned.entries:
        row = existing.get(entry.material_no)

        if row is None:
            db.add(
                ComponentName(
                    material_no=entry.material_no,
                    name_en=entry.name_en,
                    type_code=entry.type_code,
                    component_type=entry.component_type,
                    description=entry.description,
                    source_rows=entry.source_rows,
                    has_conflict=entry.has_conflict,
                )
            )
            continue

        row.name_en = entry.name_en
        row.type_code = entry.type_code
        row.component_type = entry.component_type
        row.description = entry.description
        row.source_rows = entry.source_rows
        row.has_conflict = entry.has_conflict

    stale_material_numbers = [
        material_no
        for material_no in existing
        if material_no not in incoming
    ]

    for material_no in stale_material_numbers:
        db.delete(existing[material_no])

    db.flush()

    total_after = (
        db.scalar(
            select(func.count())
            .select_from(ComponentName)
        )
        or 0
    )

    conflicts_after = (
        db.scalar(
            select(func.count())
            .select_from(ComponentName)
            .where(ComponentName.has_conflict.is_(True))
        )
        or 0
    )

    if commit:
        db.commit()
    else:
        db.flush()

    return ImportReportOut(
        encoding=cleaned.encoding,
        rows_read=cleaned.rows_read,
        rows_blank=cleaned.rows_blank,
        rows_without_material_no=cleaned.rows_without_material_no,
        material_numbers_without_name=(
            cleaned.material_numbers_without_name
        ),
        entries_written=len(cleaned.entries),
        entries_total_after=total_after,
        entries_with_conflict=conflicts_after,
        duplicate_rows_collapsed=cleaned.duplicate_rows_collapsed,
        stale_entries_deleted=len(stale_material_numbers),
        unmapped_material_numbers=(
            cleaned.unmapped_material_numbers
        ),
    )
