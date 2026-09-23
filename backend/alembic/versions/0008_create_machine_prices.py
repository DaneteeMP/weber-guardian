"""create machine_prices

Revision ID: 0008
Revises: 0007
"""
from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "machine_prices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("model", sa.String(64), nullable=False, unique=True),
        sa.Column("annual_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("inspections_per_year", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("machine_prices")
