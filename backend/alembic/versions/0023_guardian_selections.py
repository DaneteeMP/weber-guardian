"""Store selected Guardian modules and service options on each offer.

Revision ID: 0023
Revises: 0022
"""
from alembic import op
import sqlalchemy as sa


revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "offers",
        sa.Column(
            "guardian_selections",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("offers", "guardian_selections")
