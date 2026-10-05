"""Add Italian route metadata while retaining the shared route fields.

Revision ID: 0014
Revises: 0013

Distance.km remains the road distance used by pricing. Distance.trip_hours
continues to hold total one-way travel time, including ferry time where used.
"""
from alembic import op
import sqlalchemy as sa


revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


NEW_COLUMNS = (
    "province_code",
    "region",
    "reference_city",
    "origin_city",
    "driving_hours",
    "itinerary",
    "route_data_date",
)


def upgrade() -> None:
    op.add_column("distances", sa.Column("province_code", sa.String(8), nullable=True))
    op.add_column("distances", sa.Column("region", sa.String(128), nullable=True))
    op.add_column("distances", sa.Column("reference_city", sa.String(128), nullable=True))
    op.add_column("distances", sa.Column("origin_city", sa.String(128), nullable=True))
    op.add_column("distances", sa.Column("driving_hours", sa.Numeric(10, 2), nullable=True))
    op.add_column("distances", sa.Column("itinerary", sa.String(255), nullable=True))
    op.add_column("distances", sa.Column("route_data_date", sa.Date(), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    has_route_details = bind.execute(
        sa.text(
            "SELECT count(*) FROM distances WHERE "
            "province_code IS NOT NULL OR region IS NOT NULL OR reference_city IS NOT NULL "
            "OR origin_city IS NOT NULL OR driving_hours IS NOT NULL OR itinerary IS NOT NULL "
            "OR route_data_date IS NOT NULL"
        )
    ).scalar_one()
    if has_route_details:
        raise RuntimeError(
            "Cannot downgrade 0014 while extended route details exist; "
            "the previous schema cannot retain these fields."
        )
    for column in reversed(NEW_COLUMNS):
        op.drop_column("distances", column)
