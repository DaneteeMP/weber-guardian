"""Store custom annexes (title + body) on each offer for the print modal.

Revision ID: 0029
Revises: 0028
"""
from alembic import op
import sqlalchemy as sa


revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "offers",
        sa.Column(
            "custom_annexes",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("offers", "custom_annexes")
