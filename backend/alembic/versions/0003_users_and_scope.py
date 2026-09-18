"""users + subsidiary scope + offer audit

Revision ID: 0003
Revises: 0002

- users: Guardian-side authorization (role, subsidiary_id) keyed by
  the external Entra oid. No passwords, no hashes: Microsoft owns identity.
- customers.subsidiary_id: NULL means visible to every scope (legacy rows).
- offers.created_by: author reference, SET NULL if the user is removed.
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("external_id", sa.String(128), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("role", sa.String(16), nullable=False),
        sa.Column("subsidiary_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.add_column("customers", sa.Column("subsidiary_id", sa.String(64), nullable=True))
    op.create_index("ix_customers_subsidiary_id", "customers", ["subsidiary_id"])
    op.add_column(
        "offers",
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("offers", "created_by")
    op.drop_index("ix_customers_subsidiary_id", table_name="customers")
    op.drop_column("customers", "subsidiary_id")
    op.drop_table("users")
