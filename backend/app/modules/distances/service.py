"""Distance logic. Route rows are keyed by subsidiary and province."""
import csv
import io
import re
import unicodedata
from datetime import date
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.subsidiaries import normalize_subsidiary
from app.modules.distances.models import Distance
from app.modules.distances.schemas import DistanceImportReport, DistanceImportRowError, DistanceUpdate
from app.modules.subsidiaries.models import Subsidiary

GERMAN_SERVICE_CENTERS = ("Oldenburg", "Werther", "Frankfurt", "Wolfertschwenden")
MAX_DISTANCE_FILE_BYTES = 2 * 1024 * 1024
MAX_DISTANCE_ROWS = 1000
REQUIRED_ROUTE_FIELDS = (
    "province",
    "province_code",
    "region",
    "reference_city",
    "km",
    "driving_hours",
    "trip_hours",
)
ROUTE_HEADER_ALIASES = {
    "provinciaareaequivalente": "province",
    "provinceequivalentarea": "province",
    "sigla": "province_code",
    "abbreviation": "province_code",
    "regione": "region",
    "region": "region",
    "ciudaddereferencia": "reference_city",
    "referencecity": "reference_city",
    "cityofreference": "reference_city",
    "kmcarretera": "km",
    "roadkm": "km",
    "conduccionhmm": "driving_hours",
    "drivinghmm": "driving_hours",
    "drivingtimehmm": "driving_hours",
    "totalviajehmm": "trip_hours",
    "totaltravelhmm": "trip_hours",
    "totaljourneyhmm": "trip_hours",
    "itinerario": "itinerary",
    "itinerary": "itinerary",
}


class DistanceImportConflict(Exception):
    """Raised when route rows conflict with concurrent catalog writes."""


class UnknownSubsidiary(Exception):
    """A distance row references a filial outside the catalog."""

    def __init__(self, name: str):
        super().__init__(f"Unknown subsidiary: {name}")


class InvalidServiceCenter(Exception):
    """A German route row uses a service center outside the approved list."""

    def __init__(self, name: str | None):
        super().__init__(f"Invalid German service center: {name or '(empty)'}")


def get_distance(db: Session, subsidiary_id: str, province: str) -> Distance | None:
    """Fetch one route row for an exact filial/province pair."""
    return db.scalar(
        select(Distance).where(
            Distance.subsidiary_id == subsidiary_id,
            Distance.province == province,
        )
    )


def validate_subsidiary(db: Session, subsidiary_id: str) -> str:
    """Return the canonical subsidiary name or raise a domain error."""
    canonical = normalize_subsidiary(subsidiary_id)
    if canonical is None or db.get(Subsidiary, canonical) is None:
        raise UnknownSubsidiary(subsidiary_id)
    return canonical


def list_distances(
    db: Session, subsidiary_id: str | None = None, limit: int = 50, offset: int = 0
) -> list[Distance]:
    """List routes, optionally narrowed to a filial."""
    stmt = select(Distance).order_by(Distance.subsidiary_id, Distance.province)
    if subsidiary_id is not None:
        stmt = stmt.where(Distance.subsidiary_id == subsidiary_id)
    return list(db.scalars(stmt.limit(limit).offset(offset)))


def upsert_distance(
    db: Session, subsidiary_id: str, province: str, data: DistanceUpdate
) -> Distance:
    """Create or replace one route row after validating its filial."""
    canonical_subsidiary = validate_subsidiary(db, subsidiary_id)
    if canonical_subsidiary == "Weber Germany" and data.service_center not in GERMAN_SERVICE_CENTERS:
        raise InvalidServiceCenter(data.service_center)

    row = get_distance(db, canonical_subsidiary, province)
    if row is None:
        row = Distance(
            subsidiary_id=canonical_subsidiary,
            province=province,
            capital=data.capital,
            service_center=data.service_center,
            province_code=data.province_code,
            region=data.region,
            reference_city=data.reference_city,
            origin_city=data.origin_city,
            km=data.km,
            driving_hours=data.driving_hours,
            trip_hours=data.trip_hours,
            itinerary=data.itinerary,
            route_data_date=data.route_data_date,
        )
        db.add(row)
    else:
        row.capital = data.capital
        row.service_center = data.service_center
        row.province_code = data.province_code
        row.region = data.region
        row.reference_city = data.reference_city
        row.origin_city = data.origin_city
        row.km = data.km
        row.driving_hours = data.driving_hours
        row.trip_hours = data.trip_hours
        row.itinerary = data.itinerary
        row.route_data_date = data.route_data_date
    db.commit()
    db.refresh(row)
    return row


def delete_distance(db: Session, subsidiary_id: str, province: str) -> bool:
    """Delete a filial/province route row. False when it does not exist."""
    row = get_distance(db, subsidiary_id, province)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True


def _route_header_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]", "", ascii_text.lower())


def _decode_route_file(content: bytes) -> str:
    """Decode the route file without introducing an encoding dependency."""
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("File must be encoded as UTF-8 or Windows-1252")


def _parse_road_km(value: str) -> Decimal:
    """Parse kilometres, accepting dot thousands separators and comma decimals."""
    normalized = value.strip().replace("\u00a0", "").replace(" ", "")
    if not normalized:
        raise ValueError("Road km is required")
    if "," in normalized and "." in normalized:
        normalized = normalized.replace(".", "").replace(",", ".")
    elif "," in normalized:
        normalized = normalized.replace(",", ".")
    elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", normalized):
        normalized = normalized.replace(".", "")
    try:
        result = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError("Road km must be a number") from exc
    if result < 0:
        raise ValueError("Road km must not be negative")
    return result


def _parse_clock_hours(value: str, field_label: str) -> Decimal:
    """Convert h:mm to Decimal hours, requiring quarter-hour increments."""
    match = re.fullmatch(r"\s*(\d{1,3}):([0-5]\d)\s*", value)
    if match is None:
        raise ValueError(f"{field_label} must use h:mm format")
    hours = int(match.group(1))
    minutes = int(match.group(2))
    if minutes not in (0, 15, 30, 45):
        raise ValueError(f"{field_label} must use 15-minute increments")
    return Decimal(hours) + Decimal(minutes) / Decimal(60)


def import_route_csv(
    db: Session,
    content: bytes,
    subsidiary_id: str,
    origin_city: str,
    route_data_date: date,
    dry_run: bool,
) -> DistanceImportReport:
    """Validate and optionally upsert a whole route CSV atomically."""
    canonical_subsidiary = validate_subsidiary(db, subsidiary_id)
    errors: list[DistanceImportRowError] = []
    if not origin_city.strip():
        errors.append(DistanceImportRowError(line=1, reason="Origin city is required"))
    if len(content) > MAX_DISTANCE_FILE_BYTES:
        errors.append(DistanceImportRowError(line=1, reason="File exceeds 2 MB"))
        return DistanceImportReport(dry_run=dry_run, total_rows=0, created=0, updated=0, errors=errors)

    try:
        text = _decode_route_file(content)
    except ValueError as exc:
        errors.append(DistanceImportRowError(line=1, reason=str(exc)))
        return DistanceImportReport(dry_run=dry_run, total_rows=0, created=0, updated=0, errors=errors)

    parsed_file: list[list[str]] | None = None
    header_index: int | None = None
    column_indexes: dict[str, int] = {}
    duplicate_columns: list[str] = []
    for delimiter in (";", "\t", ","):
        candidate_rows = list(csv.reader(io.StringIO(text), delimiter=delimiter, quotechar='"'))
        for index, header_row in enumerate(candidate_rows):
            candidate_indexes: dict[str, int] = {}
            duplicates: list[str] = []
            for column_index, header in enumerate(header_row):
                canonical = ROUTE_HEADER_ALIASES.get(_route_header_key(header))
                if canonical is None:
                    continue
                if canonical in candidate_indexes:
                    duplicates.append(canonical)
                candidate_indexes[canonical] = column_index
            if set(REQUIRED_ROUTE_FIELDS).issubset(candidate_indexes):
                parsed_file = candidate_rows
                header_index = index
                column_indexes = candidate_indexes
                duplicate_columns = duplicates
                break
        if parsed_file is not None:
            break
    if parsed_file is None or header_index is None:
        errors.append(
            DistanceImportRowError(
                line=1,
                reason="Could not find the route table header with the required Italian columns",
            )
        )
        return DistanceImportReport(dry_run=dry_run, total_rows=0, created=0, updated=0, errors=errors)
    if duplicate_columns:
        errors.extend(
            DistanceImportRowError(line=header_index + 1, reason=f"Duplicate column for {column}")
            for column in duplicate_columns
        )
        return DistanceImportReport(dry_run=dry_run, total_rows=0, created=0, updated=0, errors=errors)

    parsed: list[dict[str, object]] = []
    seen_provinces: set[str] = set()
    total_rows = 0
    for row_index in range(header_index + 1, len(parsed_file)):
        row = parsed_file[row_index]
        line = row_index + 1
        values = {
            key: (row[column_index] if column_index < len(row) else "").strip()
            for key, column_index in column_indexes.items()
        }
        if not any(values.values()):
            continue
        total_rows += 1
        if total_rows > MAX_DISTANCE_ROWS:
            errors.append(DistanceImportRowError(line=line, reason=f"File exceeds {MAX_DISTANCE_ROWS} data rows"))
            break
        try:
            province = " ".join(values["province"].split())
            province_code = values["province_code"].strip()
            region = " ".join(values["region"].split())
            reference_city = " ".join(values["reference_city"].split())
            if not province or not province_code or not region or not reference_city:
                raise ValueError("Province, code, region and reference city are required")
            province_key = province.casefold()
            if province_key in seen_provinces:
                raise ValueError(f"Duplicate province in file: {province}")
            seen_provinces.add(province_key)

            km = _parse_road_km(values["km"])
            driving_hours = _parse_clock_hours(values["driving_hours"], "Driving time")
            trip_hours = _parse_clock_hours(values["trip_hours"], "Total travel time")
            if trip_hours < driving_hours:
                raise ValueError("Total travel time cannot be shorter than driving time")

            parsed.append(
                {
                    "province": province,
                    "province_code": province_code,
                    "region": region,
                    "reference_city": reference_city,
                    "origin_city": origin_city.strip(),
                    "km": km,
                    "driving_hours": driving_hours,
                    "trip_hours": trip_hours,
                    "itinerary": values.get("itinerary") or None,
                    "route_data_date": route_data_date,
                }
            )
        except (InvalidOperation, ValueError) as exc:
            errors.append(DistanceImportRowError(line=line, reason=str(exc)))

    if total_rows == 0 and not errors:
        errors.append(DistanceImportRowError(line=1, reason="File has no route rows"))
    if errors:
        db.rollback()
        return DistanceImportReport(dry_run=dry_run, total_rows=total_rows, created=0, updated=0, errors=errors)

    existing_rows = list(
        db.scalars(select(Distance).where(Distance.subsidiary_id == canonical_subsidiary))
    )
    existing_by_province = {" ".join(row.province.split()).casefold(): row for row in existing_rows}
    created = sum(1 for item in parsed if item["province"].casefold() not in existing_by_province)
    updated = len(parsed) - created
    if dry_run:
        db.rollback()
        return DistanceImportReport(
            dry_run=True, total_rows=total_rows, created=created, updated=updated, errors=[]
        )

    try:
        for item in parsed:
            row = existing_by_province.get(str(item["province"]).casefold())
            if row is None:
                row = Distance(subsidiary_id=canonical_subsidiary, province=str(item["province"]))
                db.add(row)
            else:
                row.province = str(item["province"])
            row.province_code = str(item["province_code"])
            row.region = str(item["region"])
            row.reference_city = str(item["reference_city"])
            row.origin_city = str(item["origin_city"])
            row.km = item["km"]  # type: ignore[assignment]
            row.driving_hours = item["driving_hours"]  # type: ignore[assignment]
            row.trip_hours = item["trip_hours"]  # type: ignore[assignment]
            row.itinerary = item["itinerary"]  # type: ignore[assignment]
            row.route_data_date = item["route_data_date"]  # type: ignore[assignment]
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DistanceImportConflict("Route import conflicted with another catalog update") from None

    return DistanceImportReport(
        dry_run=False, total_rows=total_rows, created=created, updated=updated, errors=[]
    )
