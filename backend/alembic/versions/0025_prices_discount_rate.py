"""prices.discount_rate per-subsidiary client discount

Revision ID: 0025
Revises: 0024

The discount applied to hours was a constant (0.15) in WeberAssistant and a
hardcoded value in the frontend. It is now a per-subsidiary setting like the
other rates in the same row. Existing rows keep the legacy 0.15 so history is
not re-priced.
"""
from alembic import op
import sqlalchemy as sa

revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "prices",
        sa.Column(
            "discount_rate",
            sa.Numeric(10, 4),
            nullable=False,
            server_default=sa.text("0.15"),
        ),
    )


def downgrade() -> None:
    op.drop_column("prices", "discount_rate")