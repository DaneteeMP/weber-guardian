"""Store the Guardian type on each offer.

The type (Inspection / Off-Guardian / Basic Kit) drives pricing and is printed
on the contract's commercial breakdown page. Until now it lived only in the
pricing request and was never persisted.

Revision ID: 0030
Revises: 0029
"""
from alembic import op
import sqlalchemy as sa


revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "offers",
        sa.Column(
            "offer_type",
            sa.String(length=16),
            nullable=False,
            server_default="audit",
        ),
    )


def downgrade() -> None:
    op.drop_column("offers", "offer_type")
