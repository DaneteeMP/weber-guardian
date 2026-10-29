"""Add per-band service rates (with/without maintenance contract) to prices.

Each subsidiary sets the customer-facing rates for the three contract time
bands (I/II/III) printed in the agreement annex. NULL means "not configured":
the PDF omits the whole rates block for that subsidiary.

Revision ID: 0031
Revises: 0030
"""
from alembic import op
import sqlalchemy as sa


revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None

BAND_COLUMNS = (
    "band1_rate_without",
    "band1_rate_with",
    "band2_rate_without",
    "band2_rate_with",
    "band3_rate_without",
    "band3_rate_with",
)


def upgrade() -> None:
    for column in BAND_COLUMNS:
        op.add_column("prices", sa.Column(column, sa.Numeric(10, 2), nullable=True))
    # Germany's customer-facing bands from the approved subsidiary rate sheet.
    op.execute(
        sa.text(
            """
            UPDATE prices
            SET band1_rate_without = 120.00, band1_rate_with = 98.00,
                band2_rate_without = 210.00, band2_rate_with = 171.50,
                band3_rate_without = 270.00, band3_rate_with = 220.50
            WHERE subsidiary_id = 'Weber Germany'
            """
        )
    )


def downgrade() -> None:
    for column in reversed(BAND_COLUMNS):
        op.drop_column("prices", column)
