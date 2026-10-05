"""Add stable product identity to component workloads.

Revision ID: 0021
Revises: 0020

Revision 0020 changes the workload master from a Type-code row to a product
row. Import reconciliation needs an identity that survives a user editing the
visible name, so source_key is a technical identity:

* ordinary products use component:<normalized component type>, one row per
  component type;
* old slicer rows retain a legacy:slicer:<legacy type code> identity until the
  SAP import discovers their individual model products. They remain flagged
  for review instead of being guessed into a model;
* rows with no useful component type retain a legacy:<code> identity and are
  flagged rather than collapsed into an invented "Others" workload.

When several old codes collapse into one ordinary component type, equal known
workloads are retained. Conflicting values become NULL + needs_review; choosing
one would silently invent the shared product workload.
"""
from decimal import Decimal

from alembic import op
import sqlalchemy as sa


revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def _normalized_component_type(value: str) -> str:
    """Normalize whitespace and case for the stable component-type key."""
    return " ".join(value.split()).casefold()


def _legacy_key(row) -> str:
    """Keep an old slicer/unknown row traceable without guessing its product."""
    legacy_code = row["legacy_type_code"] or str(row["id"])
    if _normalized_component_type(row["component_type"] or "") == "slicer":
        return f"legacy:slicer:{legacy_code}"
    return f"legacy:{legacy_code}"


def upgrade() -> None:
    op.add_column(
        "component_workloads",
        sa.Column("source_key", sa.String(256), nullable=True),
    )

    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            """
            SELECT id, name, component_type, workload, needs_review,
                   legacy_type_code, created_at
            FROM component_workloads
            ORDER BY created_at, id
            """
        )
    ).mappings().all()

    ordinary_groups: dict[str, list] = {}
    legacy_rows: list = []

    for row in rows:
        component_type = " ".join((row["component_type"] or "").split())
        normalized_type = _normalized_component_type(component_type)
        if not normalized_type or normalized_type == "slicer" or normalized_type == "others":
            legacy_rows.append(row)
            continue
        source_key = f"component:{normalized_type}"
        ordinary_groups.setdefault(source_key, []).append(row)

    update_statement = sa.text(
        """
        UPDATE component_workloads
        SET name = :name,
            component_type = :component_type,
            workload = :workload,
            needs_review = :needs_review,
            legacy_type_code = :legacy_type_code,
            source_key = :source_key
        WHERE id = :id
        """
    )

    for source_key, group in ordinary_groups.items():
        representative = group[0]
        display_types = sorted(
            {" ".join((row["component_type"] or "").split()) for row in group},
            key=lambda value: (value.casefold(), value),
        )
        component_type = display_types[0]
        workloads = {
            Decimal(row["workload"])
            for row in group
            if row["workload"] is not None
        }

        if len(workloads) == 1:
            workload = next(iter(workloads))
            known_rows = [row for row in group if row["workload"] is not None]
            # Any previously verified workload wins over unresolved duplicate
            # records that had no value. If none were verified, retain review.
            needs_review = all(row["needs_review"] for row in known_rows)
        else:
            # No value or conflicting values: a single shared workload cannot
            # be selected safely, so leave it for a human.
            workload = None
            needs_review = True

        legacy_codes = sorted(
            {row["legacy_type_code"] for row in group if row["legacy_type_code"]}
        )
        bind.execute(
            update_statement,
            {
                "id": representative["id"],
                "name": component_type,
                "component_type": component_type,
                "workload": workload,
                "needs_review": needs_review,
                "legacy_type_code": legacy_codes[0] if len(legacy_codes) == 1 else None,
                "source_key": source_key,
            },
        )
        duplicate_ids = [row["id"] for row in group[1:]]
        if duplicate_ids:
            bind.execute(
                sa.text("DELETE FROM component_workloads WHERE id = ANY(:ids)"),
                {"ids": duplicate_ids},
            )

    for row in legacy_rows:
        # These entries cannot safely be mapped to a shared type or slicer
        # model. Keep the old value for review, but flag the identity explicitly.
        bind.execute(
            update_statement,
            {
                "id": row["id"],
                "name": row["name"],
                "component_type": row["component_type"] or "Others",
                "workload": row["workload"],
                "needs_review": True,
                "legacy_type_code": row["legacy_type_code"],
                "source_key": _legacy_key(row),
            },
        )

    op.alter_column("component_workloads", "source_key", nullable=False)
    op.create_unique_constraint(
        "uq_component_workloads_source_key",
        "component_workloads",
        ["source_key"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_component_workloads_source_key",
        "component_workloads",
        type_="unique",
    )
    op.drop_column("component_workloads", "source_key")
