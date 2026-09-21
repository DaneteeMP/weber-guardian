"""equipment identity is the full-row hash, not material_no

Revision ID: 0006
Revises: 0005

Real SAP data proved material_no is a part reference reused across
customers and machines ("MSG 460-2", "CCW05001"). Identity becomes
row_hash UNIQUE; existing rows are backfilled (frozen hash copy: later
changes to row_hash_of must not rewrite history).
"""
import hashlib

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def _frozen_hash(customer_id, equipment_name, machine_type, component_type, material_no, purchase_date):
    joined = "\x1f".join(v or "" for v in (customer_id, equipment_name, machine_type, component_type, material_no, purchase_date))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def upgrade() -> None:
    op.drop_constraint("equipment_material_no_key", "equipment", type_="unique")
    op.create_index("ix_equipment_material_no", "equipment", ["material_no"])
    op.add_column("equipment", sa.Column("row_hash", sa.String(64), nullable=True))

    bind = op.get_bind()
    rows = bind.execute(
        sa.text('SELECT id, customer_id, equipment_name, machine_type, component_type, material_no, purchase_date FROM equipment')
    ).all()
    for row in rows:
        bind.execute(
            sa.text("UPDATE equipment SET row_hash = :h WHERE id = :i"),
            {"h": _frozen_hash(*row[1:]), "i": row[0]},
        )

    op.alter_column("equipment", "row_hash", nullable=False)
    op.create_unique_constraint("equipment_row_hash_key", "equipment", ["row_hash"])


def downgrade() -> None:
    op.drop_constraint("equipment_row_hash_key", "equipment", type_="unique")
    op.drop_column("equipment", "row_hash")
    op.drop_index("ix_equipment_material_no", table_name="equipment")
    op.create_unique_constraint("equipment_material_no_key", "equipment", ["material_no"])
