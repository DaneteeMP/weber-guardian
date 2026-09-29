"""Subsidiary logic. Catalog reads plus the in-memory supervision map.

The map ({normalized country key: subsidiary}) is rebuilt per import run
(~110 rows): cheap, always fresh, no cache to invalidate.
"""
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.subsidiaries import _key, COUNTRY_ALIASES, normalize_country, normalize_subsidiary
from app.modules.customers.models import Customer
from app.modules.subsidiaries.models import Subsidiary, SubsidiaryCountry
from app.modules.subsidiaries.schemas import AssignCountriesIn, SubsidiaryStatsOut, UnassignedCountryOut


class UnknownSubsidiary(Exception):
    """Domain error: assignment names a filial outside the catalog. Router maps it to 422."""

    def __init__(self, name: str):
        super().__init__(f"Unknown subsidiary: {name}")
        self.name = name


def list_subsidiaries(db: Session) -> list[Subsidiary]:
    """All filials ordered by name (import page dropdown)."""
    return list(db.scalars(select(Subsidiary).order_by(Subsidiary.name)))


def stats(db: Session) -> list[SubsidiaryStatsOut]:
    """Per-filial supervised countries and assigned customers (admin tab)."""
    countries = {
        row[0]: row[1]
        for row in db.execute(
            select(SubsidiaryCountry.subsidiary, func.count()).group_by(SubsidiaryCountry.subsidiary)
        ).all()
    }
    customers = {
        row[0]: row[1]
        for row in db.execute(
            select(Customer.subsidiary_id, func.count())
            .where(Customer.subsidiary_id.is_not(None))
            .group_by(Customer.subsidiary_id)
        ).all()
    }
    return [
        SubsidiaryStatsOut(
            name=row.name,
            short_label=row.short_label,
            countries=countries.get(row.name, 0),
            customers=customers.get(row.name, 0),
        )
        for row in list_subsidiaries(db)
    ]


def unassigned_countries(db: Session) -> list[UnassignedCountryOut]:
    """Customer countries with no supervising filial (NULL subsidiary), by volume."""
    rows = (
        db.execute(
            select(Customer.country, func.count())
            .where(Customer.subsidiary_id.is_(None), Customer.country.is_not(None))
            .group_by(Customer.country)
            .order_by(func.count().desc())
        ).all()
    )
    return [UnassignedCountryOut(country=country, count=count) for country, count in rows]


def assign_countries(db: Session, data: AssignCountriesIn) -> int:
    """Tag every untagged customer of the given countries. Only NULL rows
    move: already assigned ones are never silently reassigned."""
    names = {row.name for row in list_subsidiaries(db)}
    updated = 0
    for item in data.assignments:
        subsidiary = normalize_subsidiary(item.subsidiary)
        if subsidiary not in names:
            raise UnknownSubsidiary(item.subsidiary)
        result = db.execute(
            Customer.__table__.update()
            .where(Customer.country == item.country, Customer.subsidiary_id.is_(None))
            .values(subsidiary_id=subsidiary)
        )
        updated += result.rowcount
    db.commit()
    return updated


def auto_assign_all(db: Session) -> tuple[int, list[str]]:
    """Reassign EVERY customer from the supervision catalog by country.

    Explicit admin action for (re)distributing bulk imports: rows whose
    country maps elsewhere move, unknown countries stay NULL and are
    reported as warnings (assigned manually afterwards).
    """
    mapping = supervision_map(db)
    countries = [r[0] for r in db.execute(select(Customer.country).distinct()).all() if r[0]]
    updated = 0
    warnings: list[str] = []
    for country in countries:
        subsidiary = subsidiary_for_country(country, mapping)
        if subsidiary is None:
            count = db.scalar(
                select(func.count()).select_from(Customer).where(Customer.country == country)
            )
            warnings.append(f"country '{country}' has no supervising subsidiary ({count} rows kept untagged)")
            continue
        result = db.execute(
            Customer.__table__.update()
            .where(Customer.country == country)
            .where(or_(Customer.subsidiary_id.is_(None), Customer.subsidiary_id != subsidiary))
            .values(subsidiary_id=subsidiary)
        )
        updated += result.rowcount
    db.commit()
    return updated, sorted(warnings)


def supervision_map(db: Session) -> dict[str, str]:
    """Normalized country key -> canonical subsidiary name."""
    return {_key(row.country): row.subsidiary for row in db.scalars(select(SubsidiaryCountry)).all()}


def subsidiary_for_country(country: str | None, mapping: dict[str, str]) -> str | None:
    """Resolve the owning filial for a raw country string, or None."""
    key = normalize_country(country)
    if key is None:
        return None
    return mapping.get(COUNTRY_ALIASES.get(key, key))
