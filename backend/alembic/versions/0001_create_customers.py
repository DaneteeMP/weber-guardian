"""create customers

Revision ID: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("customer_id", sa.String(64), nullable=False, unique=True),
        sa.Column("account_name", sa.String(255), nullable=False),
        sa.Column("city", sa.String(128), nullable=True),
        sa.Column("province", sa.String(128), nullable=True),
        sa.Column("country", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("customers")
