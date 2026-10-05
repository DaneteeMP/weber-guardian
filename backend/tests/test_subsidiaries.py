"""Tests for the subsidiary catalog and the country-import mapping helpers."""
from app.modules.subsidiaries.models import Subsidiary, SubsidiaryCountry
from app.modules.subsidiaries.service import (
    list_subsidiaries,
    subsidiary_for_country,
    supervision_map,
)


def test_selector_catalog_is_ordered_by_name(db):
    db.add_all(
        [
            Subsidiary(name="Weber Italy", short_label="Italy"),
            Subsidiary(name="Weber Iberica", short_label="Iberica"),
        ]
    )
    db.commit()

    assert [row.name for row in list_subsidiaries(db)] == ["Weber Iberica", "Weber Italy"]


def test_import_mapping_resolves_country_aliases(db):
    db.add(
        SubsidiaryCountry(
            country="Spain",
            subsidiary="Weber Iberica",
        )
    )
    db.commit()
    mapping = supervision_map(db)

    assert subsidiary_for_country("Spain", mapping) == "Weber Iberica"
    assert subsidiary_for_country(None, mapping) is None
    assert subsidiary_for_country("Unknown country", mapping) is None
