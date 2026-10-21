"""Shared subsidiary lookup used by selectors and country imports."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.subsidiaries import COUNTRY_ALIASES, _key, normalize_country
from app.modules.customers.models import Customer
from app.modules.subsidiaries.models import Subsidiary, SubsidiaryCountry
from app.modules.subsidiaries.schemas import SubsidiaryStatsOut, UnassignedCountryOut


class CountryAlreadyMapped(Exception):
    """The country already has a supervising subsidiary."""

    def __init__(self, country: str):
        super().__init__(f"Country already mapped: {country}")
        self.country = country


class CountryNotFound(Exception):
    """The country has no row in the supervision mapping."""

    def __init__(self, country: str):
        super().__init__(f"Country not found in supervision mapping: {country}")
        self.country = country


class SubsidiaryNotFound(Exception):
    """The target subsidiary is not in the catalog."""

    def __init__(self, subsidiary: str):
        super().__init__(f"Unknown subsidiary: {subsidiary}")
        self.subsidiary = subsidiary


def list_subsidiaries(db: Session) -> list[Subsidiary]:
    """List filial names for the TopBar, Config and import selectors."""
    return list(db.scalars(select(Subsidiary).order_by(Subsidiary.name)))


def list_countries(db: Session) -> list[SubsidiaryCountry]:
    """Full supervision mapping ordered by country name."""
    return list(db.scalars(select(SubsidiaryCountry).order_by(SubsidiaryCountry.country)))


def stats(db: Session) -> list[SubsidiaryStatsOut]:
    """Per-filial counters for the admin tab: supervised countries from the
    map, customers tagged with the subsidiary (catalog order)."""
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
    """Customer countries with no supervising subsidiary, ordered by volume.

    The covered check uses the exact resolution the imports use
    (normalize_country + alias table), so a country spelled differently than
    its map key still counts as covered and never shows up here.
    """
    mapping = supervision_map(db)
    rows = db.execute(
        select(Customer.country, func.count())
        .where(Customer.country.is_not(None))
        .group_by(Customer.country)
        .order_by(func.count().desc(), Customer.country)
    ).all()
    return [
        UnassignedCountryOut(country=country, count=count)
        for country, count in rows
        if subsidiary_for_country(country, mapping) is None
    ]


def _require_subsidiary(db: Session, subsidiary: str) -> None:
    if db.get(Subsidiary, subsidiary) is None:
        raise SubsidiaryNotFound(subsidiary)


def add_country(db: Session, country: str, subsidiary: str) -> SubsidiaryCountry:
    """Map a new country to a subsidiary. Case-insensitive duplicate check."""
    country = country.strip()
    _require_subsidiary(db, subsidiary)
    existing = db.scalar(
        select(SubsidiaryCountry).where(SubsidiaryCountry.country.ilike(country))
    )
    if existing is not None:
        raise CountryAlreadyMapped(existing.country)
    row = SubsidiaryCountry(country=country, subsidiary=subsidiary)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def move_country(db: Session, country: str, subsidiary: str) -> SubsidiaryCountry:
    """Reassign an existing country to another subsidiary."""
    _require_subsidiary(db, subsidiary)
    row = db.scalar(
        select(SubsidiaryCountry).where(SubsidiaryCountry.country.ilike(country.strip()))
    )
    if row is None:
        raise CountryNotFound(country)
    row.subsidiary = subsidiary
    db.commit()
    db.refresh(row)
    return row


def delete_country(db: Session, country: str) -> None:
    """Drop a country from the supervision mapping. 404-style error when the
    country is not mapped (same convention as the responsibles module)."""
    row = db.scalar(
        select(SubsidiaryCountry).where(SubsidiaryCountry.country.ilike(country.strip()))
    )
    if row is None:
        raise CountryNotFound(country)
    db.delete(row)
    db.commit()


def supervision_map(db: Session) -> dict[str, str]:
    """Return normalized country key to canonical subsidiary name."""
    return {
        _key(row.country): row.subsidiary
        for row in db.scalars(select(SubsidiaryCountry)).all()
    }


def subsidiary_for_country(country: str | None, mapping: dict[str, str]) -> str | None:
    """Resolve the owning subsidiary for a raw country name, or None."""
    key = normalize_country(country)
    if key is None:
        return None
    return mapping.get(COUNTRY_ALIASES.get(key, key))
