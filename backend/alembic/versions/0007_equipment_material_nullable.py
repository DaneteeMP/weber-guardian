"""equipment.material_no nullable (machine-level rows)

Revision ID: 0007
Revises: 0006

Machine-level CSV rows carry equipment + purchase date but no component
breakdown (empty Material No.). Rejecting them loses installed base, so
they import as equipment with NULL material instead.
"""
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("equipment", "material_no", nullable=True)


def downgrade() -> None:
    # Fails if NULL-material rows exist: delete or fix them first.
    op.alter_column("equipment", "material_no", nullable=False)
