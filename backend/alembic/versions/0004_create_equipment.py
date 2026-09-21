"""create equipment

Revision ID: 0004
Revises: 0003
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "equipment",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("customer_id", sa.String(64), sa.ForeignKey("customers.customer_id", ondelete="CASCADE"), nullable=False),
        sa.Column("equipment_name", sa.String(64), nullable=True),
        sa.Column("machine_type", sa.String(32), nullable=True),
        sa.Column("material_no", sa.String(64), nullable=False, unique=True),
        sa.Column("component_type", sa.String(64), nullable=True),
        sa.Column("purchase_date", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_equipment_customer_id", "equipment", ["customer_id"])
    op.create_index("ix_equipment_equipment_name", "equipment", ["equipment_name"])


def downgrade() -> None:
    op.drop_index("ix_equipment_equipment_name", table_name="equipment")
    op.drop_index("ix_equipment_customer_id", table_name="equipment")
    op.drop_table("equipment")
