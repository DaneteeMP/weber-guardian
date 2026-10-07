"""Restore the legacy module workloads keyed by type_code.

Revision ID: 0022
Revises: 0021

Migration 0018 seeded the business workloads keyed by ``component_names.type_code``
(the legacy ``TblWorkLoad.[Component Description]`` key). Migration 0020/0021
later re-keyed that table by *product* (component type / slicer model), which is
right for slicers but merged every ordinary code that shared a component type.
When the merged values disagreed the result became NULL, so codes like KSG, CCE
and CMB lost their real hours even though the business had supplied them.

This migration restores that legacy source of truth in its own table, without
touching any historical migration:

* ``module_workloads`` is keyed by ``type_code`` exactly like the legacy
  ``TblWorkLoad`` table, so a component resolves through
  ``component_names.type_code -> module_workloads.workload``.
* ``component_workloads`` stays as the product/editing layer (slicer models).

Values are copied verbatim from the 0018 seed list, including the codes that are
deliberately unresolved (NULL + needs_review) because the business gave
conflicting numbers or none at all.
"""
from alembic import op
import sqlalchemy as sa


revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


# (type_code, business label, workload or None) copied from 0018_component_workloads.py
SEED = [
    ("CBS", "Bandsystem CBS", "0.5"),
    ("CCW", "checkweigher CCW 200 mono / 200 multi-track / 500 multi-track / LC-WEB99", None),
    ("CPB", "Compactbuffer CPB", "1.5"),
    ("CCE", "infeed conveyor CCE", "1.5"),
    ("MOV", "infeed conveyor MOV", "1.5"),
    ("CTE", "infeed cycle CTE", None),
    ("CCA", "infeeder CCA / CPL / CRL / ESA / FED, and CCA 600/800", None),
    ("CPL", "infeeder CPL", "1.5"),
    ("CRL", "infeeder CRL", "1.5"),
    ("ESA", "infeeder ESA", "1.5"),
    ("FED", "infeeder FED", "1.5"),
    ("CCI", "interleaver CCI", "1.5"),
    ("KSG", "knife sharpener KSG", "1.0"),
    ("SSG", "knife sharpener SSG", "1.0"),
    ("SSM", "knife sharpener SSM", "1.5"),
    ("SHA", "sharpening centre weSHARP", "1.5"),
    ("CHB", "lift-loading conveyor CHB", "0.5"),
    ("CBM", "loading magazine CBM", "0.5"),
    ("CMB", "marking conveyor CMB", "1.5"),
    ("CMP", "multi-buffer", "4.0"),
    ("CCO", "overlapper CCO 100/200/300", "1.5"),
    ("TOX", "overlapper / Textor overlapper", "1.5"),
    ("WPR", "pick robot WPR (1 / 2 / 4)", None),
    ("CCR", "rocker CCR", "0.5"),
    ("CTR", "rocker CTR", "0.5"),
    ("CCU", "turntable CCU", None),
    ("CPS", "scanner CPS", "1.5"),
    ("WCS", "shingle stack loader WCS", "1.0"),
    ("TQB", "shingle stacker", "1.0"),
    ("WSL", "shuttle loader WSL", "0.5"),
    ("CGE", "shuttle loader CGE", "0.5"),
    ("WSS", "shuttle system WSS", "2.0"),
    ("TL6", "smart loader TL660", "1.0"),
    ("CSA", "sorting and erecting station CSA", "1.0"),
    ("CTM", "spurverteiler CTM", "0.5"),
    ("TSX", "Textor TS500/700", "4.0"),
    ("UND", "underleaver", "2.0"),
    ("CUL", "underleaver CUL", "2.0"),
    ("PPI", "underleaver PPI", "2.0"),
    ("VPM", "VMAX packing machine", "5.0"),
    ("PAC", "packaging machine wePACK", "5.0"),
    ("VMA", "VMAX-5501", "5.0"),
    ("DIV", "weDIVIDE", "3.0"),
    ("SOR", "weSORT", "2.0"),
    ("CSL", "StreamLoader", "2.0"),
    ("SLI", "Slicer S6 / weSLICE 4000 / weSLICE 9500", None),
    ("DEN", "tray denester", None),
    ("GRB", "vario gripper", None),
    ("TH1", "Thera 450/500/650", None),
    ("TH2", "Thera 100/250", None),
]


def upgrade() -> None:
    op.create_table(
        "module_workloads",
        sa.Column("type_code", sa.String(16), primary_key=True),
        # Business wording from the legacy list, so the code is readable.
        sa.Column("label", sa.String(128), nullable=False),
        sa.Column("workload", sa.Numeric(10, 2), nullable=True),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    table = sa.table(
        "module_workloads",
        sa.column("type_code", sa.String(16)),
        sa.column("label", sa.String(128)),
        sa.column("workload", sa.Numeric(10, 2)),
        sa.column("needs_review", sa.Boolean()),
    )
    op.bulk_insert(
        table,
        [
            {
                "type_code": type_code,
                "label": label,
                "workload": workload,
                # A NULL workload is exactly what needs a human decision.
                "needs_review": workload is None,
            }
            for type_code, label, workload in SEED
        ],
    )


def downgrade() -> None:
    op.drop_table("module_workloads")
