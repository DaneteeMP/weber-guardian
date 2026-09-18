"""create offers + offer_items

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "offers",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("id_guardian_offer", sa.String(64), nullable=False, unique=True),
        sa.Column("customer_id", sa.String(64), sa.ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("responsible_person", sa.String(128), nullable=True),
        sa.Column("language", sa.String(32), nullable=True),
        sa.Column("inspection_frequency", sa.String(32), nullable=True),
        sa.Column("currency", sa.String(8), nullable=False),
        sa.Column("work_hours", sa.Numeric(10, 1), nullable=False),
        sa.Column("bk_hours", sa.Numeric(10, 1), nullable=False),
        sa.Column("report_hours", sa.Numeric(10, 1), nullable=False),
        sa.Column("total_hours", sa.Numeric(10, 1), nullable=False),
        sa.Column("trip_hours", sa.Numeric(10, 1), nullable=False),
        sa.Column("trip_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("diets", sa.Numeric(12, 2), nullable=False),
        sa.Column("hotel_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("expenses", sa.Numeric(12, 2), nullable=False),
        sa.Column("hours_import", sa.Numeric(12, 2), nullable=False),
        sa.Column("discount", sa.Numeric(12, 2), nullable=False),
        sa.Column("bk_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("total", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_end", sa.Numeric(12, 2), nullable=False),
        sa.Column("general_comments", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_offers_customer_id", "offers", ["customer_id"])

    op.create_table(
        "offer_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("offer_id", sa.Uuid(), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("row_no", sa.Integer(), nullable=False),
        sa.Column("equipment", sa.String(64), nullable=True),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("import_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("workload", sa.Numeric(10, 2), nullable=False),
    )
    op.create_index("ix_offer_items_offer_id", "offer_items", ["offer_id"])


def downgrade() -> None:
    op.drop_index("ix_offer_items_offer_id", table_name="offer_items")
    op.drop_table("offer_items")
    op.drop_index("ix_offers_customer_id", table_name="offers")
    op.drop_table("offers")
