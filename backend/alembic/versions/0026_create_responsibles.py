"""responsibles per subsidiary for the offer Responsible dropdown

Revision ID: 0026
Revises: 0025

The people who can own an offer, scoped by subsidiary. Offers keep storing
responsible_person as free text (history never breaks when someone is
renamed or removed); this table is the managed list the dropdown offers.
"""
import sqlalchemy as sa
from alembic import op

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "responsibles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("subsidiary_id", sa.String(64), sa.ForeignKey("subsidiaries.name"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("subsidiary_id", "name", name="uq_responsibles_subsidiary_name"),
    )


def downgrade() -> None:
    op.drop_table("responsibles")
