"""offers.offer_date editable business date

Revision ID: 0010
Revises: 0009

Until now the only date on an offer was created_at, a database audit stamp set
at INSERT time. The PDF and the monitoring home showed that stamp as the offer
date, so the date could not be corrected and could not be typed when creating
an offer by hand.

offer_date is the business date (day precision) that users can set and edit.
Existing rows are backfilled from created_at so history keeps showing the day
the row was created. created_at stays untouched as the audit stamp: listing
order, "created" audits and the customer ranking still use it.
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("offers", sa.Column("offer_date", sa.Date(), nullable=True))
    op.execute("UPDATE offers SET offer_date = created_at::date")


def downgrade() -> None:
    op.drop_column("offers", "offer_date")
