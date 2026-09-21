"""create prices, distances, basic_kit catalogs

Revision ID: 0005
Revises: 0004
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prices",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("subsidiary_id", sa.String(64), nullable=False, unique=True),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("km_rate", sa.Numeric(10, 4), nullable=False),
        sa.Column("tech_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("diet_full_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("diet_half_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("hotel_rate", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "distances",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("province", sa.String(128), nullable=False, unique=True),
        sa.Column("km", sa.Numeric(10, 1), nullable=False),
        sa.Column("trip_hours", sa.Numeric(10, 1), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "basic_kit",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("model", sa.String(64), nullable=False, unique=True),
        sa.Column("workload_basic_kit", sa.Numeric(10, 1), nullable=False),
        sa.Column("spare_parts", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("basic_kit")
    op.drop_table("distances")
    op.drop_table("prices")
