"""Catalog amount rules after migration 0019.

Maintenance amounts are workload times the branch technician rate, so the
catalog carries hours only. The dev seed must not invent catalog figures
anymore: migration 0019 wrote the verified legacy workloads, and any demo value
typed over them would masquerade as business data.
"""
import importlib.util
from pathlib import Path

import seed_dev


def _load_migration(name: str):
    path = Path(__file__).resolve().parents[1] / "alembic" / "versions" / name
    spec = importlib.util.spec_from_file_location(name.rstrip(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_line_from_0013_has_a_verified_workload_in_0019():
    migration_0013 = _load_migration("0013_equipment_catalog.py")
    migration_0019 = _load_migration("0019_drop_catalog_price.py")

    assert set(migration_0019.LINE_WORKLOADS) == set(migration_0013.LINE_LABELS)


def test_every_verified_workload_is_positive():
    migration_0019 = _load_migration("0019_drop_catalog_price.py")

    for workload in migration_0019.LINE_WORKLOADS.values():
        assert workload > 0


def test_the_dev_seed_no_longer_invents_catalog_values():
    """The seed used to fill empty price/workload fields with demo figures.

    With amounts computed from workloads, an invented figure would look like
    business data, so the seed must stay out of the equipment catalog.
    """
    assert not hasattr(seed_dev, "EQUIPMENT_CATALOG_VALUES")
    assert not hasattr(seed_dev, "fill_demo_equipment_values")
