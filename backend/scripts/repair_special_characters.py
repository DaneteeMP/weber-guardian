"""Restore the characters the SAP export dropped as "?".

The export is ISO-8859-1: it cannot write the local letters (sh, z with
caron, c with acute, l with stroke...) nor the typographic apostrophe and
dashes, so it wrote "?" and the import stored that verbatim. The characters
are gone from the source file, so they are restored from the reviewed
mapping in data/special_character_fixes.json.

    python scripts/repair_special_characters.py            # dry run
    python scripts/repair_special_characters.py --apply    # write

The dry run is the default on purpose: the mapping is data, and a wrong
character would be as bad as the "?" it replaces. Every row is checked
against the value the database holds right now, so a database that changed
since the mapping was written stops the run instead of overwriting it.
"""
import json
import sys
from pathlib import Path

from sqlalchemy import select, update

from app.core.db import SessionLocal
from app.modules.customers.models import Customer
from app.modules.equipment.models import CustomerSite

MAPPING = Path(__file__).resolve().parent.parent / "data" / "special_character_fixes.json"


def load_mapping() -> dict:
    with MAPPING.open(encoding="utf-8") as handle:
        return json.load(handle)


def check_customer(db, entry: dict) -> str | None:
    """Return the current name, or None when it does not match the mapping."""
    customer = db.scalar(
        select(Customer).where(Customer.customer_id == entry["customer_id"])
    )
    if customer is None:
        return None
    return customer.account_name


def check_site(db, entry: dict) -> str | None:
    site = db.scalar(select(CustomerSite).where(CustomerSite.customer_id == entry["customer_id"]))
    if site is None:
        return None
    return getattr(site, entry["field"]) or ""


def main() -> int:
    apply = "--apply" in sys.argv
    mapping = load_mapping()
    problems: list[str] = []
    changes: list[tuple[str, str, str]] = []

    with SessionLocal() as db:
        for entry in mapping["customers"]:
            current = check_customer(db, entry)
            if current is None:
                problems.append(f"customer {entry['customer_id']} not found")
                continue
            if current == entry["corrected"]:
                # Already repaired: the script can run again without changes.
                continue
            if current != entry["current"]:
                problems.append(
                    f"customer {entry['customer_id']}: database holds {current!r}, "
                    f"mapping expects {entry['current']!r}"
                )
                continue
            changes.append((f"customer {entry['customer_id']}", current, entry["corrected"]))

        for entry in mapping["sites"]:
            current = check_site(db, entry)
            if current is None:
                problems.append(f"site {entry['customer_id']} not found")
                continue
            if current == entry["corrected"]:
                # Already repaired: the script can run again without changes.
                continue
            if current != entry["current"]:
                problems.append(
                    f"site {entry['customer_id']}.{entry['field']}: database holds {current!r}, "
                    f"mapping expects {entry['current']!r}"
                )
                continue
            changes.append((f"site {entry['customer_id']}.{entry['field']}", current, entry["corrected"]))

        if problems:
            print("STOP: the database does not match the mapping, nothing was written.")
            for problem in problems:
                print(f"  - {problem}")
            return 1

        print(f"{len(changes)} values to restore\n")
        for label, current, corrected in changes:
            print(f"  {label}")
            print(f"      {current}")
            print(f"   -> {corrected}")

        if not apply:
            print("\nDry run. Run again with --apply to write.")
            return 0

        for entry in mapping["customers"]:
            db.execute(
                update(Customer)
                .where(Customer.customer_id == entry["customer_id"])
                .values(account_name=entry["corrected"])
            )
        for entry in mapping["sites"]:
            db.execute(
                update(CustomerSite)
                .where(CustomerSite.customer_id == entry["customer_id"])
                .values(**{entry["field"]: entry["corrected"]})
            )
        db.commit()

        # The repair is only complete when no "?" is left in the fields it
        # touches. A leftover means a row the mapping does not cover.
        left = db.scalar(
            select(Customer).where(Customer.account_name.like("%?%")).limit(1)
        )
        sites_left = db.scalar(
            select(CustomerSite)
            .where(
                (CustomerSite.physical_street.like("%?%"))
                | (CustomerSite.physical_city.like("%?%"))
            )
            .limit(1)
        )
        print(f"\napplied {len(changes)} corrections")
        if left is not None:
            print(f"  WARNING: customer {left.customer_id} still holds a '?'")
        if sites_left is not None:
            print(f"  WARNING: site of customer {sites_left.customer_id} still holds a '?'")
        if left is None and sites_left is None:
            print("  no '?' left in customer names or site addresses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
