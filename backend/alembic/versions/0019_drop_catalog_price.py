"""Drop equipment_catalog price: maintenance amounts come from workloads only.

Revision ID: 0019
Revises: 0018

A maintenance line is priced as workload times the branch technician rate
(prices.tech_rate of the customer's subsidiary, currency included). Machine and
module entries therefore carry no amount of their own anymore:

* price and currency are dropped. They were demo figures from seed_dev, not
  business data, and keeping a dead price column would invite someone to type
  a number the pricing rule ignores.
* The three module entries created in migration 0013 (Bandsystem CBS,
  Checkweigher CCW 200 mono/multi-track) and their material_no matches are
  deleted. Modules are priced through component_workloads keyed by the
  dictionary type code, so a module row in this catalog has nothing to say.
* The line workloads created by demo seed values are replaced with the
  verified legacy values supplied by the business.
* The kind constraint tightens to 'line' and the match constraint to
  'machine_type': schema stops admitting rows that can no longer be priced.

The downgrade recreates the dropped columns but cannot resurrect the deleted
demo module rows: their matches were user-entered and the demo values were
never business data, so a revert leaves the catalog free of modules. In a real
deployment 0019 runs once.
"""
from decimal import Decimal

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Numeric, bindparam


revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


# Verified legacy values supplied by the business, replacing the invented demo
# figures seed_dev used to write into the same field.
LINE_WORKLOADS = {
    "1000": Decimal("2.0"),
    "30x": Decimal("2.0"),
    "40x": Decimal("2.5"),
    "40x+": Decimal("3.5"),
    "4500": Decimal("4.5"),
    "504/505": Decimal("3.0"),
    "602": Decimal("3.0"),
    "604": Decimal("4.5"),
    "7000": Decimal("3.0"),
    "702": Decimal("3.0"),
    "802": Decimal("4.0"),
    "804": Decimal("4.5"),
    "9000": Decimal("4.0"),
    "901": Decimal("4.0"),
    "902": Decimal("4.0"),
    "903": Decimal("4.0"),
    "90x": Decimal("5.0"),
}

MODULE_LABELS = (
    "Bandsystem CBS",
    "Checkweigher CCW 200 mono",
    "Checkweigher CCW 200 multi-track",
)


def upgrade() -> None:
    bind = op.get_bind()

    # Modules are priced through component_workloads, so a module row here has
    # no role left. Delete its matches first to respect the FK.
    module_ids = (
        bind.execute(
            sa.text("SELECT id FROM equipment_catalog WHERE kind = 'module'")
        )
        .scalars()
        .all()
    )
    if module_ids:
        id_list = ", ".join(f"'{entry_id}'" for entry_id in module_ids)
        bind.execute(
            sa.text(f"DELETE FROM equipment_catalog_matches WHERE entry_id IN ({id_list})")
        )
        bind.execute(sa.text("DELETE FROM equipment_catalog WHERE kind = 'module'"))

    # An UPDATE that matches fewer rows than intended still reports success, so
    # compare against the catalog before touching anything.
    line_labels = {
        row for row in bind.execute(
            sa.text("SELECT label FROM equipment_catalog WHERE kind = 'line'")
        ).scalars()
    }
    unknown = sorted(set(LINE_WORKLOADS) - line_labels)
    if unknown:
        raise RuntimeError(
            f"catalog lines listed here are missing from equipment_catalog: {unknown}"
        )
    for label, workload in LINE_WORKLOADS.items():
        statement = (
            sa.text("UPDATE equipment_catalog SET workload = :w WHERE label = :label AND kind = 'line'")
            .bindparams(bindparam("w", type_=Numeric(10, 1)), bindparam("label", type_=sa.String(128)))
        )
        bind.execute(statement, {"w": workload, "label": label})

    # The schema stops admitting rows it cannot price: lines only, matched by
    # machine_type only.
    with op.batch_alter_table("equipment_catalog") as batch:
        batch.drop_column("price")
        batch.drop_column("currency")
        batch.drop_constraint("ck_equipment_catalog_kind")
        batch.create_check_constraint(
            "ck_equipment_catalog_kind", "kind = 'line'"
        )
    with op.batch_alter_table("equipment_catalog_matches") as batch:
        batch.drop_constraint("ck_equipment_catalog_match_field")
        batch.create_check_constraint(
            "ck_equipment_catalog_match_field", "match_field = 'machine_type'"
        )


def downgrade() -> None:
    with op.batch_alter_table("equipment_catalog") as batch:
        batch.create_check_constraint("ck_equipment_catalog_kind", "kind IN ('line', 'module')")
        batch.add_column(sa.Column("currency", sa.String(8), nullable=False, server_default="EUR"))
        batch.add_column(sa.Column("price", sa.Numeric(12, 2), nullable=True))
    with op.batch_alter_table("equipment_catalog_matches") as batch:
        batch.create_check_constraint(
            "ck_equipment_catalog_match_field", "match_field IN ('machine_type', 'material_no')"
        )
