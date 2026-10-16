"""merge duplicate equipment rows left by address-changing re-imports

Revision ID: 0027
Revises: 0026

Repeated imports that changed the address (or filled a field later) created
a second row for the same installed component, because the old matching only
fired when the stored row had no site yet. The import now matches on the
installed identity (customer, equipment, component, material, purchase) and
updates in place, so this one-shot cleanup merges the twins the old rule
left behind: per identity group keep the sited row, then the newest data.

Fails loudly when anything is left over instead of half-merging.
"""
import sqlalchemy as sa
from alembic import op

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None

# Same fields as instance_hash_of() in app/modules/equipment/models.py: the
# site and the machine family are attributes, not identity. NULLs group
# together in GROUP BY / PARTITION BY on both Postgres and SQLite.
IDENTITY_COLUMNS = (
    "customer_id",
    "equipment_name",
    "component_type",
    "material_no",
    "purchase_date",
)

_DUPLICATE_GROUPS = f"""
SELECT {", ".join(IDENTITY_COLUMNS)}
FROM equipment
GROUP BY {", ".join(IDENTITY_COLUMNS)}
HAVING count(*) > 1
"""


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM equipment
            WHERE id IN (
                SELECT id FROM (
                    SELECT
                        id,
                        ROW_NUMBER() OVER (
                            PARTITION BY customer_id, equipment_name,
                                         component_type, material_no,
                                         purchase_date
                            ORDER BY (site_id IS NULL), created_at DESC, id DESC
                        ) AS rn
                    FROM equipment
                ) ranked
                WHERE rn > 1
            )
            """
        )
    )
    leftover_check = sa.text(f"SELECT count(*) FROM ({_DUPLICATE_GROUPS}) t")
    bind = op.get_bind()
    result = bind.execute(leftover_check) if bind is not None else None
    if result is None:
        # Offline (--sql) render: statements print, nothing to check against.
        return
    leftover = result.scalar()
    if leftover:
        raise RuntimeError(f"0027 left {leftover} duplicate equipment groups behind")


def downgrade() -> None:
    # Irreversible on purpose and harmless: the schema is untouched, only
    # duplicate rows are gone, so there is nothing to rebuild. Reverting only
    # moves the version marker back; a re-upgrade is a no-op then.
    pass
