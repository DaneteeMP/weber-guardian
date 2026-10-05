"""Create the global equipment catalog and unconfirmed code candidates.

Revision ID: 0013
Revises: 0012

The workloads and prices remain NULL until entered from verified business
data. Numeric-family candidates are stored unconfirmed and are never resolved
for offers until an administrator validates them.
"""
import uuid

from alembic import op
import sqlalchemy as sa


revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


LINE_LABELS = (
    "1000",
    "30x",
    "40x",
    "40x+",
    "4500",
    "504/505",
    "602",
    "604",
    "7000",
    "702",
    "802",
    "804",
    "9000",
    "901",
    "902",
    "903",
    "90x",
)

MODULE_LABELS = (
    "Bandsystem CBS",
    "Checkweigher CCW 200 mono",
    "Checkweigher CCW 200 multi-track",
)

# Candidates follow the earlier numeric review of imported machine_type codes.
# They require explicit admin confirmation before resolution.
LINE_CANDIDATES = {
    "1000": ("WLN10001", "WLN10002", "WLN01001"),
    "30x": ("CCS302", "CCS304", "CCS305", "WLN03041", "WLN03051"),
    "40x": ("CCS401", "CCS402", "CCS404", "CCS405", "WLN04021", "WLN04041", "WLN04051", "WLN04052"),
    "40x+": ("WLN40001",),
    "4500": ("WLN45001",),
    "504/505": ("CCS504", "CCS505", "TLN05001", "WLN05041", "WLN05051"),
    "602": ("CCS602", "WLN06021"),
    "604": ("CCS604", "WLN06041", "WLN06042"),
    "7000": ("CCS7000", "TLN07001", "WLN70001"),
    "702": ("CCS702", "WLN07021"),
    "802": ("CCS802",),
    "804": ("CCS804", "WLN08041"),
    "9000": ("CCS9000",),
    "901": ("CCS901",),
    "902": ("CCS902",),
    "903": ("CCS903",),
    "90x": ("CCS904", "CCS905", "CCS906", "WLN09021", "WLN09031", "WLN09041", "WLN09042", "WLN09051", "WLN09061"),
}


def upgrade() -> None:
    op.create_table(
        "equipment_catalog",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("kind", sa.String(8), nullable=False),
        sa.Column("label", sa.String(128), nullable=False),
        sa.Column("workload", sa.Numeric(10, 1), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(8), nullable=False, server_default="EUR"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("label", name="uq_equipment_catalog_label"),
        sa.CheckConstraint("kind IN ('line', 'module')", name="ck_equipment_catalog_kind"),
    )
    op.create_table(
        "equipment_catalog_matches",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "entry_id",
            sa.Uuid(),
            sa.ForeignKey("equipment_catalog.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("match_field", sa.String(16), nullable=False),
        sa.Column("match_value", sa.String(64), nullable=False),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("match_field", "match_value", name="uq_equipment_catalog_match_value"),
        sa.CheckConstraint(
            "match_field IN ('machine_type', 'material_no')", name="ck_equipment_catalog_match_field"
        ),
    )
    op.create_index("ix_equipment_catalog_matches_entry_id", "equipment_catalog_matches", ["entry_id"])

    entry_table = sa.table(
        "equipment_catalog",
        sa.column("id", sa.Uuid()),
        sa.column("kind", sa.String(8)),
        sa.column("label", sa.String(128)),
        sa.column("workload", sa.Numeric(10, 1)),
        sa.column("price", sa.Numeric(12, 2)),
        sa.column("currency", sa.String(8)),
    )
    entries = [
        {"id": uuid.uuid4(), "kind": "line", "label": label, "workload": None, "price": None, "currency": "EUR"}
        for label in LINE_LABELS
    ]
    entries.extend(
        {"id": uuid.uuid4(), "kind": "module", "label": label, "workload": None, "price": None, "currency": "EUR"}
        for label in MODULE_LABELS
    )
    op.bulk_insert(entry_table, entries)

    ids_by_label = {entry["label"]: entry["id"] for entry in entries}
    matches = [
        {
            "id": uuid.uuid4(),
            "entry_id": ids_by_label[label],
            "match_field": "machine_type",
            "match_value": machine_type,
            "is_confirmed": False,
        }
        for label, machine_types in LINE_CANDIDATES.items()
        for machine_type in machine_types
    ]
    match_table = sa.table(
        "equipment_catalog_matches",
        sa.column("id", sa.Uuid()),
        sa.column("entry_id", sa.Uuid()),
        sa.column("match_field", sa.String(16)),
        sa.column("match_value", sa.String(64)),
        sa.column("is_confirmed", sa.Boolean()),
    )
    op.bulk_insert(match_table, matches)


def downgrade() -> None:
    op.drop_index("ix_equipment_catalog_matches_entry_id", table_name="equipment_catalog_matches")
    op.drop_table("equipment_catalog_matches")
    op.drop_table("equipment_catalog")
