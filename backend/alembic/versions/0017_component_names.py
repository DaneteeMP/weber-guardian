"""Create the cleaned component name dictionary.

Revision ID: 0017
Revises: 0015

names_dictionary.csv lists one row per component per material number, but the
same material number repeats with the same values thousands of times: 51,857
non-empty rows collapse to 22,582 distinct material numbers. Storing the raw
file row by row would be noise, and looking the name up by scanning rows at
request time would be slow, so the importer collapses the file and this table
holds one row per material number.

material_no is the business key and the join to equipment.material_no, which
matches 6,048 of the 6,049 Italian equipment rows exactly. type_code keeps the
file "Type" column because the module workload table will key on it.

A material number that appears with more than one distinct set of values is
not resolved by guessing: has_conflict marks it so the importer can show it for
manual review instead of silently keeping an arbitrary row.
"""
from alembic import op
import sqlalchemy as sa


revision = "0017"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "component_names",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("material_no", sa.String(64), nullable=False),
        sa.Column("name_en", sa.String(256), nullable=False),
        sa.Column("type_code", sa.String(64), nullable=True),
        sa.Column("component_type", sa.String(128), nullable=True),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("source_rows", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("has_conflict", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("material_no", name="uq_component_names_material_no"),
    )


def downgrade() -> None:
    op.drop_table("component_names")
