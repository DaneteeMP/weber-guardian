"""Convert component workloads from type-code based to product based.

Revision ID: 0020
Revises: 0019

The legacy workload table was keyed by component_names.type_code. That is too
coarse for products whose maintenance workload depends on the actual model.

Examples:

    CCS -> Slicer 302 / 304 / 405 / 604 / ...
    SLI -> Slicer S6 / weSLICE 4000 / weSLICE 5500 / ...
    TSX -> Slicer TS500 / TS700

This migration changes component_workloads so that a workload is an explicit,
editable product definition instead of a type-code definition.

Existing workload values are preserved where possible. The old type_code is
temporarily copied into legacy_type_code so that the migration remains
traceable. The legacy column can be removed after the new importer has been
validated.
"""

from alembic import op
import sqlalchemy as sa


revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Create the new table.
    #
    # We deliberately create a new table instead of trying to mutate the
    # primary key in-place. This is much safer because the existing table
    # contains business data from migration 0018.
    # ------------------------------------------------------------------

    op.create_table(
        "component_workloads_new",
        sa.Column(
            "id",
            sa.Uuid(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(256),
            nullable=False,
        ),
        sa.Column(
            "component_type",
            sa.String(128),
            nullable=False,
        ),
        sa.Column(
            "workload",
            sa.Numeric(10, 2),
            nullable=True,
        ),
        sa.Column(
            "needs_review",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "legacy_type_code",
            sa.String(16),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ------------------------------------------------------------------
    # 2. Copy the existing workload rows.
    #
    # We retain their labels and values. component_type is resolved from
    # component_names where possible.
    #
    # For old rows that have no component_names match, use "Others".
    # They remain editable and their legacy_type_code tells us where
    # they came from.
    # ------------------------------------------------------------------

    rows = bind.execute(
        sa.text(
            """
            SELECT
                cw.type_code,
                cw.label,
                cw.workload,
                cw.needs_review,
                cn.component_type
            FROM component_workloads cw
            LEFT JOIN (
                SELECT
                    type_code,
                    MIN(component_type) AS component_type
                FROM component_names
                WHERE component_type IS NOT NULL
                  AND TRIM(component_type) <> ''
                GROUP BY type_code
            ) cn
                ON cn.type_code = cw.type_code
            ORDER BY cw.type_code
            """
        )
    ).mappings().all()

    # PostgreSQL UUID generation is preferable here because the migration
    # should not depend on Python-side UUID generation.
    insert = sa.text(
        """
        INSERT INTO component_workloads_new (
            id,
            name,
            component_type,
            workload,
            needs_review,
            legacy_type_code
        )
        VALUES (
            gen_random_uuid(),
            :name,
            :component_type,
            :workload,
            :needs_review,
            :legacy_type_code
        )
        """
    )

    for row in rows:
        component_type = row["component_type"]

        if not component_type:
            component_type = "Others"

        bind.execute(
            insert,
            {
                "name": row["label"],
                "component_type": component_type,
                "workload": row["workload"],
                "needs_review": row["needs_review"],
                "legacy_type_code": row["type_code"],
            },
        )

    # ------------------------------------------------------------------
    # 3. Replace the old table.
    # ------------------------------------------------------------------

    op.drop_table("component_workloads")

    op.rename_table(
        "component_workloads_new",
        "component_workloads",
    )


def downgrade() -> None:
    bind = op.get_bind()

    # ------------------------------------------------------------------
    # Recreate the original table structure.
    # ------------------------------------------------------------------

    op.create_table(
        "component_workloads_old",
        sa.Column(
            "type_code",
            sa.String(16),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "label",
            sa.String(128),
            nullable=False,
        ),
        sa.Column(
            "workload",
            sa.Numeric(10, 2),
            nullable=True,
        ),
        sa.Column(
            "needs_review",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # A product-based table can contain several products sharing the same
    # legacy type_code. The old schema cannot represent that. Therefore the
    # downgrade only keeps the first product for each legacy type_code.
    #
    # This is intentionally conservative: it avoids inventing values.
    bind.execute(
        sa.text(
            """
            INSERT INTO component_workloads_old (
                type_code,
                label,
                workload,
                needs_review,
                created_at
            )
            SELECT DISTINCT ON (legacy_type_code)
                legacy_type_code,
                name,
                workload,
                needs_review,
                created_at
            FROM component_workloads
            WHERE legacy_type_code IS NOT NULL
            ORDER BY legacy_type_code, created_at, id
            """
        )
    )

    op.drop_table("component_workloads")

    op.rename_table(
        "component_workloads_old",
        "component_workloads",
    )