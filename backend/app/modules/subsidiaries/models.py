"""Subsidiary catalog tables.

subsidiaries: canonical full names + short display labels.
subsidiary_countries: supervision mapping (country -> subsidiary),
seeded from the business list in migration 0009.
"""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Subsidiary(Base):
    __tablename__ = "subsidiaries"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    short_label: Mapped[str] = mapped_column(String(32), nullable=False)


class SubsidiaryCountry(Base):
    __tablename__ = "subsidiary_countries"

    country: Mapped[str] = mapped_column(String(128), primary_key=True)
    subsidiary: Mapped[str] = mapped_column(String(64), ForeignKey("subsidiaries.name"), nullable=False)
