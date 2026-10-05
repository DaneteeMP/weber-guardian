"""Confirm the equipment catalog line matches inserted by migration 0013.

Revision ID: 0015
Revises: 0014

Migration 0013 stored the numeric review of the imported machine_type codes as
unconfirmed candidates, so the resolver returned nothing for a catalog line and
no offer could ever be priced from the line catalog. The business confirmed
that each of these codes does identify its catalog family, so they become
confirmed.

Only the exact values listed here are touched. Matches an administrator adds
later are left alone, and module matches stay unconfirmed until a real
material_no to module mapping is loaded.
"""
from alembic import op
import sqlalchemy as sa


revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


# Same codes, grouped by catalog label exactly as in migration 0013, so the two
# files can be compared entry by entry.
CONFIRMED_CODES = {
    "1000": ("WLN10001", "WLN10002", "WLN01001"),
    "30x": ("CCS302", "CCS304", "CCS305", "WLN03041", "WLN03051"),
    "40x": ("CCS401", "CCS402", "CCS404", "CCS405", "WLN04021", "WLN04041", "WLN04051", "WLN04052"),
    "40x+": ("WLN40001",),
    "4500": ("WLN45001",),
    "504/505": ("CCS504", "CCS505", "TLN05001", "WLN05041", "WLN05051"),
    "602": ("CCS602", "WLN06021"),
    "604": ("CCS604", "WLN06041", "WLN06042"),
    "7000": ("CCS7000", "TLN07001", "WLN70001"),
    "702": ("CCS702", "WLN07021"),
    "802": ("CCS802",),
    "804": ("CCS804", "WLN08041"),
    "9000": ("CCS9000",),
    "901": ("CCS901",),
    "902": ("CCS902",),
    "903": ("CCS903",),
    "90x": ("CCS904", "CCS905", "CCS906", "WLN09021", "WLN09031", "WLN09041", "WLN09042",
            "WLN09051", "WLN09061"),
}

CONFIRMED_MACHINE_TYPES = tuple(
    code for codes in CONFIRMED_CODES.values() for code in codes
)


def _matching_rows() -> int:
    table = sa.table(
        "equipment_catalog_matches",
        sa.column("match_field", sa.String(16)),
        sa.column("match_value", sa.String(64)),
    )
    statement = sa.select(sa.func.count()).where(
        table.c.match_field == "machine_type",
        table.c.match_value.in_(CONFIRMED_MACHINE_TYPES),
    )
    return op.get_bind().execute(statement).scalar_one()


def _set_confirmed(value: bool) -> None:
    table = sa.table(
        "equipment_catalog_matches",
        sa.column("match_field", sa.String(16)),
        sa.column("match_value", sa.String(64)),
        sa.column("is_confirmed", sa.Boolean()),
    )
    op.get_bind().execute(
        table.update()
        .where(
            table.c.match_field == "machine_type",
            table.c.match_value.in_(CONFIRMED_MACHINE_TYPES),
        )
        .values(is_confirmed=value)
    )


def upgrade() -> None:
    # An UPDATE that matches fewer rows than intended still reports success, so
    # a mistyped code here would quietly confirm part of the catalog and leave
    # the rest unresolvable. Compare against the list first and fail loudly.
    found = _matching_rows()
    if found != len(CONFIRMED_MACHINE_TYPES):
        raise RuntimeError(
            f"expected {len(CONFIRMED_MACHINE_TYPES)} catalog line matches to confirm, "
            f"found {found}: this list and the catalog disagree"
        )
    _set_confirmed(True)


def downgrade() -> None:
    # Deliberately unguarded: reverting a revision must always be possible, so
    # it cannot refuse to run. The cost is that it clears only the codes listed
    # above, so editing that list between upgrade and downgrade leaves the
    # removed codes confirmed. In a real deployment 0015 runs once.
    _set_confirmed(False)