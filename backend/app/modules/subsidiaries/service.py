"""Shared subsidiary lookup used by selectors and country imports."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.subsidiaries import COUNTRY_ALIASES, _key, normalize_country
from app.modules.subsidiaries.models import Subsidiary, SubsidiaryCountry


def list_subsidiaries(db: Session) -> list[Subsidiary]:
    """List filial names for the TopBar, Config and import selectors."""
    return list(db.scalars(select(Subsidiary).order_by(Subsidiary.name)))


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
