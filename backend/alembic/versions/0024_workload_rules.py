"""Global workload rules and material links (replaces module_workloads as source).

Revision ID: 0024
Revises: 0023

What this migration does
------------------------
1. Creates ``workload_rules`` and ``workload_rule_materials``.
2. Inserts the reconstructed legacy TblWorkLoad rules (values supplied by the
   business) plus one ``carried_over`` rule (CCL) that exists only in the
   previous ``module_workloads`` table.
3. Links dictionary materials to rules ONLY where the evidence is strong:

   * type-level links: the legacy code has exactly one rule, so every
     ``component_names`` row with that ``type_code`` belongs to it;
   * explicit links: one material whose dictionary name names the rule
     (``CCW01001`` "Checkweigher CCW 100").

   Everything else stays unlinked and therefore flagged for review at draft
   time. Legacy codes with several rules (CCW, CCA, WPR) are NOT type-linked,
   because the dictionary cannot tell their variants apart.

What this migration does NOT do
-------------------------------
* It does not drop or change ``module_workloads`` or ``component_workloads``.
  They are frozen: the application no longer reads or writes them. Dropping
  them is a separate, later decision after the new system is verified.
* It does not touch ``component_names``, equipment, customers or offers.
* It does not change the CMB value. The legacy source says 0.50, the database
  says 1.50; the database value is kept and the rule is flagged for review.
"""
from decimal import Decimal
import uuid

from alembic import op
import sqlalchemy as sa


revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


# (name, legacy_type_code, workload, category, needs_review, note, link_type)
#
# link_type=True links every component_names row whose type_code equals
# legacy_type_code. Only set it when that legacy code has a single rule.
LEGACY = "legacy"
CARRIED = "carried_over"

RULES = [
    ("Bandsystem CBS", "CBS", "0.50", LEGACY, False, None, True),
    ("Checkweigher 100", "CCW", "1.00", LEGACY, False, "Legacy group LC/WEB99/2000/CCW100/CCW500/weWEIGHT = 1. Split because the dictionary name is 'Checkweigher CCW 100'.", False),
    ("Checkweigher 200 mono", "CCW", "1.50", LEGACY, False, "No dictionary material could be proven to be this variant. Left unlinked on purpose.", False),
    ("Checkweigher 200 multi-track", "CCW", "2.00", LEGACY, False, "No dictionary material could be proven to be this variant. CCW02001 'Checkweigher 200' is ambiguous between mono and multi-track.", False),
    ("Checkweigher 500 multi-track", "CCW", "2.00", LEGACY, False, "Legacy values conflict: 'CCW 500 multi-track' = 2 but group CCW500 = 1. CCW05001 stays unlinked until confirmed.", False),
    ("Checkweigher LC/WEB99/2000/CCW500/weWEIGHT", "CCW", "1.00", LEGACY, False, "Remaining members of legacy group = 1. CCW500 conflicts with the multi-track rule, so no material is linked.", False),
    ("Compactbuffer CPB", "CPB", "1.50", LEGACY, False, None, True),
    ("Infeed conveyor CCE", "CCE", "1.50", LEGACY, False, "Legacy group CCE/MOV = 1.5, split by dictionary type.", True),
    ("Infeed conveyor MOV", "MOV", "1.50", LEGACY, False, "Legacy group CCE/MOV = 1.5, split by dictionary type.", True),
    ("Infeed cycle CTE", "CTE", "1.00", LEGACY, False, None, True),
    ("Infeeder CCA", "CCA", "1.50", LEGACY, False, "CCA materials may be CCA 600/800 (2 h). Cannot be decided from the dictionary, so no material is linked.", False),
    ("Infeeder CCA 600", "CCA", "2.00", LEGACY, False, "No dictionary material could be proven to be the 600 variant.", False),
    ("Infeeder CCA 800", "CCA", "2.00", LEGACY, False, "No dictionary material could be proven to be the 800 variant.", False),
    ("Infeeder CPL", "CPL", "1.50", LEGACY, False, "Legacy group CCA/CPL/CRL/ESA/FED = 1.5, split by dictionary type.", True),
    ("Infeeder CRL", "CRL", "1.50", LEGACY, False, "Legacy group CCA/CPL/CRL/ESA/FED = 1.5, split by dictionary type.", True),
    ("Infeeder ESA", "ESA", "1.50", LEGACY, False, "Legacy group CCA/CPL/CRL/ESA/FED = 1.5, split by dictionary type.", True),
    ("Infeeder FED", "FED", "1.50", LEGACY, False, "Legacy group CCA/CPL/CRL/ESA/FED = 1.5, split by dictionary type.", True),
    ("Interleaver CCI", "CCI", "1.50", LEGACY, False, None, True),
    ("Knife sharpener KSG", "KSG", "1.00", LEGACY, False, "Legacy group KSG/SSG = 1.", True),
    ("Knife sharpener SSG", "SSG", "1.00", LEGACY, False, "Legacy group KSG/SSG = 1.", True),
    ("Knife sharpener SSM", "SSM", "1.50", LEGACY, False, "Legacy group SSM/weSHARP = 1.5.", True),
    ("weSHARP sharpening centre", "SHA", "1.50", LEGACY, False, "Legacy group SSM/weSHARP = 1.5.", True),
    ("Lift-loading conveyor CHB", "CHB", "0.50", LEGACY, False, None, True),
    ("Loading magazine CBM", "CBM", "0.50", LEGACY, False, None, True),
    (
        "Marking conveyor CMB",
        "CMB",
        "1.50",
        LEGACY,
        True,
        "CONFLICT: legacy source says 0.50, database said 1.50. Value kept unchanged; confirm before using.",
        True,
    ),
    ("Multi-buffer CMP", "CMP", "4.00", LEGACY, False, None, True),
    ("Overlapper CCO 100/200/300", "CCO", "1.50", LEGACY, False, None, True),
    ("Textor overlapper TOX", "TOX", "1.50", LEGACY, False, None, True),
    ("Pick robot WPR 1", "WPR", "1.00", LEGACY, False, "Dictionary cannot tell the 1/2/4 robot variants apart (all 'wePICK'). Unlinked.", False),
    ("Pick robot WPR 2", "WPR", "2.00", LEGACY, False, "Dictionary cannot tell the 1/2/4 robot variants apart. Unlinked.", False),
    ("Pick robot WPR 4", "WPR", "4.00", LEGACY, False, "Dictionary cannot tell the 1/2/4 robot variants apart. Unlinked.", False),
    ("Rocker CCR", "CCR", "0.50", LEGACY, False, "Legacy group rocker CCR/CTR = 0.5, split by dictionary type.", True),
    ("Rocker CTR", "CTR", "0.50", LEGACY, False, "Legacy group rocker CCR/CTR = 0.5, split by dictionary type.", True),
    ("Scanner CPS", "CPS", "1.50", LEGACY, False, "Legacy group scanner CPS/CPSX = 1.5.", True),
    ("Shingle stack loader WCS", "WCS", "1.00", LEGACY, False, None, True),
    (
        "Shingle stacker TQB",
        "TQB",
        "1.00",
        LEGACY,
        False,
        "Legacy 'Shingle stacker' = 1 linked to TQB, the mapping the previous module table already used.",
        True,
    ),
    (
        "Shuttle loader WSL",
        "WSL",
        "0.50",
        LEGACY,
        False,
        "Legacy 'Shuttle Loader WSL(CSB+CGE)' = 0.5, priced per material as before.",
        True,
    ),
    (
        "Shuttle loader CGE",
        "CGE",
        "0.50",
        LEGACY,
        False,
        "Legacy 'Shuttle Loader WSL(CSB+CGE)' = 0.5, priced per material as before.",
        True,
    ),
    (
        "Shuttle loader CSB",
        "CSB",
        "0.50",
        LEGACY,
        True,
        "Grouped legacy rule WSL(CSB+CGE) = 0.5. Confirm whether CSB is priced per material.",
        True,
    ),
    ("Shuttle system WSS", "WSS", "2.00", LEGACY, False, None, True),
    ("Smart loader TL660", "TL6", "1.00", LEGACY, False, None, True),
    ("Sorting and erecting station CSA", "CSA", "1.00", LEGACY, False, None, True),
    ("Spurverteiler CTM", "CTM", "0.50", LEGACY, False, None, True),
    ("Turntable CCU", "CCU", "0.50", LEGACY, False, None, True),
    ("Underleaver CUL", "CUL", "2.00", LEGACY, False, "Legacy 'underleaver' = 2, split by dictionary type.", True),
    ("Underleaver UND", "UND", "2.00", LEGACY, False, "Legacy 'underleaver' = 2, split by dictionary type.", True),
    ("Underleaver PPI", "PPI", "2.00", LEGACY, False, "Legacy 'underleaver' = 2, split by dictionary type.", True),
    ("weDIVIDE DIV", "DIV", "3.00", LEGACY, False, None, True),
    ("Packaging machine wePACK", "PAC", "5.00", LEGACY, False, "Legacy 'Vmax/wePACK' = 5.", True),
    ("VMAX packing machine VPM", "VPM", "5.00", LEGACY, False, "Legacy 'Vmax/wePACK' = 5.", True),
    ("VMAX-5501 VMA", "VMA", "5.00", LEGACY, False, "Legacy 'Vmax/wePACK' = 5.", True),
    ("weSORT SOR", "SOR", "2.00", LEGACY, False, None, True),
    ("StreamLoader CSL", "CSL", "2.00", LEGACY, False, None, True),
    ("Tray denester DEN", "DEN", "1.00", LEGACY, False, "No dictionary material yet. Rule exists for future links.", True),
    ("Vario gripper GRB", "GRB", "3.00", LEGACY, False, "No dictionary material yet. Rule exists for future links.", True),
    ("Thera 450/500/650 TH1", "TH1", "5.00", LEGACY, False, "No dictionary material yet. Rule exists for future links.", True),
    ("Thera 100/250 TH2", "TH2", "3.00", LEGACY, False, "No dictionary material yet. Rule exists for future links.", True),
    (
        "lc-infeed conveyor CCL",
        "CCL",
        "5.00",
        CARRIED,
        False,
        "Value carried over from module_workloads. Not in the reconstructed legacy list: confirm.",
        True,
    ),
]

# Materials whose dictionary name names the rule explicitly. Each must exist in
# component_names, otherwise the INSERT ... SELECT links nothing.
EXPLICIT_LINKS = [
    ("Checkweigher 100", "CCW01001"),
]


def upgrade() -> None:
    op.create_table(
        "workload_rules",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("workload", sa.Numeric(10, 2), nullable=True),
        sa.Column("legacy_type_code", sa.String(length=16), nullable=True),
        sa.Column("category", sa.String(length=32), nullable=False, server_default="legacy"),
        sa.Column("needs_review", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("note", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_workload_rules_name"),
        sa.CheckConstraint("workload IS NULL OR workload >= 0", name="ck_workload_rules_workload_nonnegative"),
        sa.CheckConstraint(
            "category IN ('legacy', 'carried_over', 'manual')",
            name="ck_workload_rules_category",
        ),
    )
    op.create_index("ix_workload_rules_legacy_type_code", "workload_rules", ["legacy_type_code"])

    op.create_table(
        "workload_rule_materials",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "workload_rule_id",
            sa.Uuid(),
            sa.ForeignKey("workload_rules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("material_no", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("material_no", name="uq_workload_rule_materials_material_no"),
    )
    op.create_index("ix_workload_rule_materials_workload_rule_id", "workload_rule_materials", ["workload_rule_id"])

    rules_table = sa.table(
        "workload_rules",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("workload", sa.Numeric(10, 2)),
        sa.column("legacy_type_code", sa.String()),
        sa.column("category", sa.String()),
        sa.column("needs_review", sa.Boolean()),
        sa.column("note", sa.String()),
    )
    op.bulk_insert(
        rules_table,
        [
            {
                "id": uuid.uuid4(),
                "name": name,
                "workload": Decimal(workload),
                "legacy_type_code": code,
                "category": category,
                "needs_review": needs_review,
                "note": note,
            }
            for name, code, workload, category, needs_review, note, _link_type in RULES
        ],
    )

    # Type-level links. The rule name is unique, so each statement touches only
    # the dictionary rows of the one legacy code that rule owns.
    for name, code, _workload, _category, _review, _note, link_type in RULES:
        if not link_type:
            continue
        op.execute(
            sa.text(
                """
                INSERT INTO workload_rule_materials (id, workload_rule_id, material_no, created_at)
                SELECT gen_random_uuid(), r.id, cn.material_no, now()
                FROM component_names cn
                JOIN workload_rules r ON r.name = :rule_name
                WHERE cn.type_code = :code
                """
            ).bindparams(rule_name=name, code=code)
        )

    for rule_name, material_no in EXPLICIT_LINKS:
        op.execute(
            sa.text(
                """
                INSERT INTO workload_rule_materials (id, workload_rule_id, material_no, created_at)
                SELECT gen_random_uuid(), r.id, cn.material_no, now()
                FROM component_names cn
                JOIN workload_rules r ON r.name = :rule_name
                WHERE cn.material_no = :material_no
                """
            ).bindparams(rule_name=rule_name, material_no=material_no)
        )


def downgrade() -> None:
    op.drop_index("ix_workload_rule_materials_workload_rule_id", table_name="workload_rule_materials")
    op.drop_table("workload_rule_materials")
    op.drop_index("ix_workload_rules_legacy_type_code", table_name="workload_rules")
    op.drop_table("workload_rules")
