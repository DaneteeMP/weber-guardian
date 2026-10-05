"""Create the global module workload table and seed the legacy values.

Revision ID: 0018
Revises: 0017

A maintenance line is priced as workload times the branch technician rate, and
machines have no price of their own. Lines keep their workload in
equipment_catalog; this table holds the module workloads, keyed by the
component_names.type_code that the dictionary cleaned out of names_dictionary.csv.

The business supplied 63 legacy workloads: 17 for lines and 46 for modules.
Every module value below was matched to a type_code against the cleaned
dictionary rather than by guessing from the label, and the match is written in
the comment next to it.

Three groups are deliberately left unresolved:

* Conflicting values for one code. CCW is 1.5 for mono-track and 2 for
  multi-track; CCA is 1.5 for the standard infeeder and 2 for the 600/800.
  One number cannot be both, so workload stays NULL and needs_review is set.
* Codes the legacy list names but the dictionary does not contain (tray
  denester, vario gripper, both Thera variants). They exist as rows with a
  NULL workload so the grid shows what is still missing.
* Codes whose dictionary name contradicts the legacy label: CTE is a
  "BG synchroniser" in the dictionary but the legacy calls it "infeed cycle",
  and CCU is a "portioning unit" while the legacy calls it "turntable". Also
  left NULL rather than matched on a hunch.

Workloads are global: they describe the work a component needs, not the branch
that performs it. The branch rate lives in prices.tech_rate.

needs_review means "a human must decide", so the UI can filter on it. It is
cleared by saving a workload, never silently by this migration.
"""
from alembic import op
import sqlalchemy as sa


revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


# (type_code, business label, workload or None, match evidence)
SEED = [
    # Bandsystem [CBS01001] in the dictionary.
    ("CBS", "Bandsystem CBS", "0.5", "Bandsystem [CBS01001]"),
    # CCW is the checkweigher family, but four different legacy values.
    ("CCW", "checkweigher CCW 200 mono / 200 multi-track / 500 multi-track / LC-WEB99", None,
     "checkweigher [CCW05001]; values 1.5, 2, 2, 1 disagree"),
    # CompactBuffer [CPB01001].
    ("CPB", "Compactbuffer CPB", "1.5", "CompactBuffer [CPB01001]"),
    # "infeed conveyor" is the CCE family; MOV is "Transport conveyor Move-it".
    ("CCE", "infeed conveyor CCE", "1.5", "infeed conveyor [CCE-2050]"),
    ("MOV", "infeed conveyor MOV", "1.5", "Transport conveyor Move-it [MOV]"),
    ("CTE", "infeed cycle CTE", None,
     "dictionary calls CTE a BG synchroniser, not an infeed cycle"),
    # "autom. infeeder" covers CCA, CRL, ESA and FED; CPL is the Compact Loader
    # named by the same legacy line. CSM is a shaved-meat infeeder, excluded.
    ("CCA", "infeeder CCA / CPL / CRL / ESA / FED, and CCA 600/800", None,
     "autom. infeeder [CCA-1287]; values 1.5 and 2 disagree"),
    ("CPL", "infeeder CPL", "1.5", "Compact Loader [CPL01001]"),
    ("CRL", "infeeder CRL", "1.5", "autom. infeeder (Typ-I-C) [CRL-7047]"),
    ("ESA", "infeeder ESA", "1.5", "autom. infeeder [ESA-I-5013]"),
    ("FED", "infeeder FED", "1.5", "weFEED [FED]"),
    # Interleaver [CCI06001]; TIX is "Interleaver TI", a different product.
    ("CCI", "interleaver CCI", "1.5", "Interleaver [CCI06001]"),
    # The three sharpeners are blade sharpeners in the dictionary; SHA is
    # "sharpening centre weSHARP 7000", the weSHARP half of the legacy line.
    ("KSG", "knife sharpener KSG", "1.0", "circular blade sharpener [KSG]"),
    ("SSG", "knife sharpener SSG", "1.0", "blade sharpener for IB [SSG]"),
    ("SSM", "knife sharpener SSM", "1.5", "blade sharpener [SSM]"),
    ("SHA", "sharpening centre weSHARP", "1.5", "sharpening centre weSHARP 7000 [SHA7000]"),
    # "lift-loading conveyor" names CHB directly.
    ("CHB", "lift-loading conveyor CHB", "0.5", "lift-loading conveyor [CHB 904-7428]"),
    # CBM is "Belademagazin", which is the German for loading magazine.
    ("CBM", "loading magazine CBM", "0.5", "Belademagazin [CBM01001]"),
    # Marking Conveyor [CMB01001].
    ("CMB", "marking conveyor CMB", "1.5", "Marking Conveyor [CMB01001]"),
    # CMP is "Mehrlagenpuffer", the multi-layer buffer conveyor.
    ("CMP", "multi-buffer", "4.0", "multi-layered buffer. conveyor [CMP01001-109]"),
    # Both overlapper lines carry 1.5, so CCO and TOX share it.
    ("CCO", "overlapper CCO 100/200/300", "1.5", "portion overlapper [CCO03001]"),
    ("TOX", "overlapper / Textor overlapper", "1.5", "Textor Overlapper [TOX01001]"),
    # WPR is the pick robot, but three different legacy values.
    ("WPR", "pick robot WPR (1 / 2 / 4)", None,
     "pick robot [WPR03001]; values 1, 2 and 4 disagree"),
    # CCR is the rocker; CTR is named by the same legacy line.
    ("CCR", "rocker CCR", "0.5", "Rocker [CCR01001]"),
    ("CTR", "rocker CTR", "0.5", "rocker CTR [CTR]"),
    # The dictionary calls CCU a portioning unit, not a turntable, and the
    # turning station is CCD, so this one is left to a human.
    ("CCU", "turntable CCU", None, "dictionary: portioning unit [CCU06001], not a turntable"),
    # Product Scanner X-Ray [CPS04001]; CPSX does not exist in the dictionary.
    ("CPS", "scanner CPS", "1.5", "Product Scanner X-Ray [CPS04001]"),
    # WCS is "shingle/stack loader", TQB "transfer unit cross shingle"; both
    # legacy lines carry 1.
    ("WCS", "shingle stack loader WCS", "1.0", "shingle/stack loader WCS [WCS-7139]"),
    ("TQB", "shingle stacker", "1.0", "transfer unit cross shingle [TQB06001]"),
    # Weber Shuttle Loader [WSL01001]; CGE groups and infeeds into it.
    ("WSL", "shuttle loader WSL", "0.5", "Weber Shuttle Loader [WSL01001]"),
    ("CGE", "shuttle loader CGE", "0.5", "grouping and infeed conveyor [CGE01001]"),
    # Weber Shuttle System [WSS01002].
    ("WSS", "shuttle system WSS", "2.0", "Weber Shuttle System [WSS01002]"),
    # SmartLoader [TL660-20001] matches the legacy "smart loader TL660".
    ("TL6", "smart loader TL660", "1.0", "SmartLoader [TL660-20001]"),
    # CSA is "Sortier- und Aufrichtstation": sorting and erecting station.
    ("CSA", "sorting and erecting station CSA", "1.0", "Sortier- und Aufrichtstation [CSA 905-8038]"),
    # Spurverteiler [CTM01001].
    ("CTM", "spurverteiler CTM", "0.5", "Spurverteiler [CTM01001]"),
    # TSX carries the Textor slicer 500/600/700 family.
    ("TSX", "Textor TS500/700", "4.0", "Textor TS700 Slicer [TSX06001]"),
    # Every underleaver shares 2, so all three codes take it.
    ("UND", "underleaver", "2.0", "underleaver [UND50001-10000]"),
    ("CUL", "underleaver CUL", "2.0", "underleaver [CUL01001]"),
    ("PPI", "underleaver PPI", "2.0", "Underleaver from Pacproinc [PPI01001]"),
    # The packaging machines all take 5, so no risk in seeding all of them.
    ("VPM", "VMAX packing machine", "5.0", "VMAX packing machine [VPM10001]"),
    ("PAC", "packaging machine wePACK", "5.0", "packaging machine wePACK [PAC10001]"),
    ("VMA", "VMAX-5501", "5.0", "Verpackungsmaschine VMAX-5501 [VMAX-5501]"),
    # Cheese block divider weDIVIDE 7000 [DIV70001].
    ("DIV", "weDIVIDE", "3.0", "Cheese block divider weDIVIDE 7000 [DIV70001]"),
    # Converger weSORT [SOR10001].
    ("SOR", "weSORT", "2.0", "Converger weSORT [SOR10001]"),
    # StreamLoader [CSL01001].
    ("CSL", "StreamLoader", "2.0", "StreamLoader [CSL01001]"),
    # SLI is the slicer family, shared by S6 and both weSLICE lines, and the
    # legacy values (5, 4, 5) do not agree on one number.
    ("SLI", "Slicer S6 / weSLICE 4000 / weSLICE 9500", None,
     "Slicer S6 [SLI06001] and weSLICE 4000 [SLI40001] share the code; values 5, 4 and 5 disagree"),
    # The four below exist in the legacy list but nowhere in the dictionary, so
    # there is no material number to attach them to.
    ("DEN", "tray denester", None, "no material number for tray denester in the dictionary"),
    ("GRB", "vario gripper", None, "no material number for vario gripper in the dictionary"),
    ("TH1", "Thera 450/500/650", None, "no material number for Thera in the dictionary"),
    ("TH2", "Thera 100/250", None, "no material number for Thera in the dictionary"),
]


def upgrade() -> None:
    op.create_table(
        "component_workloads",
        sa.Column("type_code", sa.String(16), primary_key=True),
        # The business wording, so the grid shows what a code means without a
        # second lookup. Kept from the legacy list, not invented.
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
        "component_workloads",
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
            for type_code, label, workload, _evidence in SEED
        ],
    )


def downgrade() -> None:
    op.drop_table("component_workloads")
