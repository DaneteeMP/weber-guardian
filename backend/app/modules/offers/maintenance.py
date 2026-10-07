"""Maintenance draft: rows priced server-side as workload × branch tech rate.

A maintenance line has no price of its own. Its amount is the row's standard
hours (workload) times the technician hourly rate of the customer's subsidiary
(prices.tech_rate).

Each selected machine produces:

* one ``line`` row: the machine itself, priced by its family (the
  ``equipment_catalog`` line entry for its ``machine_type``, e.g. "40x");
* one ``module`` row per attached component, priced by its ``type_code``
  workload (``module_workloads``).

The slicer component of a machine IS the machine line, so it is never repeated
as a module: a compact "UB" slicer (no attachments) therefore yields its line
row alone. Unknown workloads are never invented: they produce
needs_review=True and amount=0.00 until an administrator configures them.
"""

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.customers.service import CustomerNotFound
from app.modules.component_names.models import ComponentName, ModuleWorkload
from app.modules.component_names.service import legacy_base_material_no, normalize_material_no
from app.modules.component_names.workloads import SLICER_TYPE_CODES
from app.modules.equipment.models import Equipment
from app.modules.equipment_catalog.service import resolve_line
from app.modules.offers.schemas import MaintenanceDraftOut, MaintenanceDraftRowOut
from app.modules.prices.models import PriceList


TWOPLACES = Decimal("0.01")

class RateNotConfigured(Exception):
    """The customer's subsidiary has no prices row."""

    def __init__(self, subsidiary_id: str | None):
        super().__init__(
            f"No tech rate configured for subsidiary: {subsidiary_id}"
        )
        self.subsidiary_id = subsidiary_id


def _money(value: Decimal) -> Decimal:
    """Same money convention as the pricing engine: 2 decimals, half up."""
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _machine_rows(rows: list[Equipment], name: str) -> list[Equipment]:
    return [row for row in rows if row.equipment_name == name]


def _machine_type_of(rows: list[Equipment]) -> str | None:
    """The machine's type: the first row that carries one."""
    for row in rows:
        if row.machine_type:
            return row.machine_type
    return None


def _line_row(
    machine: str,
    rows: list[Equipment],
    rate: Decimal,
    resolved,
) -> MaintenanceDraftRowOut:
    machine_type = _machine_type_of(rows)

    if machine_type is None:
        return MaintenanceDraftRowOut(
            machine=machine,
            kind="line",
            description=None,
            workload=None,
            amount=Decimal("0.00"),
            match_state="unknown",
            needs_review=True,
        )

    # The line is editable from the Offer badge: by machine_type (line_code),
    # through the equipment_catalog line entry when one exists.
    if resolved is None:
        return MaintenanceDraftRowOut(
            machine=machine,
            kind="line",
            description=machine_type,
            workload=None,
            amount=Decimal("0.00"),
            match_state="unknown",
            needs_review=True,
            workload_kind="line",
            line_code=machine_type,
        )

    entry, is_confirmed = resolved
    workload = entry.workload
    needs_review = not is_confirmed or workload is None

    amount = (
        _money(workload * rate)
        if workload is not None
        else Decimal("0.00")
    )

    return MaintenanceDraftRowOut(
        machine=machine,
        kind="line",
        description=entry.label,
        workload=workload,
        amount=amount,
        match_state="confirmed" if is_confirmed else "unconfirmed",
        needs_review=needs_review,
        workload_kind="line",
        workload_id=entry.id,
        line_code=machine_type,
    )


def _module_rows(
    machine: str,
    rows: list[Equipment],
    rate: Decimal,
    names_by_key: dict[str, ComponentName],
    legacy_by_code: dict[str, ModuleWorkload],
) -> list[MaintenanceDraftRowOut]:
    """Build one maintenance row per attached component of a machine.

    The same material can appear multiple times in the imported equipment
    data. It is therefore collapsed to one row so its workload is not counted
    repeatedly. The slicer component is skipped: it is the machine line, already
    priced by the line row, and repeating it would double the machine.
    """
    # One row per distinct catalogue material; keep the raw material so a
    # dictionary imported before the model-aware normalization still resolves.
    raw_by_key: dict[str, str] = {}
    for row in rows:
        if not row.material_no:
            continue
        raw_by_key.setdefault(normalize_material_no(row.material_no), row.material_no)

    output: list[MaintenanceDraftRowOut] = []

    for material_no in sorted(raw_by_key):
        raw_material = raw_by_key[material_no]
        name = names_by_key.get(material_no) or names_by_key.get(
            legacy_base_material_no(raw_material)
        )

        if name is None:
            output.append(
                MaintenanceDraftRowOut(
                    machine=machine,
                    kind="module",
                    description=None,
                    material_no=material_no,
                    type_code=None,
                    workload=None,
                    amount=Decimal("0.00"),
                    match_state="unknown",
                    needs_review=True,
                )
            )
            continue

        type_code = name.type_code

        # The slicer is the machine line itself (priced by family in the line
        # row). Never add it again as a module, and drop its variants such as
        # the "-Z" accessory rows.
        if (type_code or "").strip().upper() in SLICER_TYPE_CODES:
            continue

        legacy = legacy_by_code.get(type_code) if type_code else None
        workload = legacy.workload if legacy is not None else None
        if workload is None:
            needs_review = True
            match_state = "unknown"
        else:
            needs_review = legacy.needs_review
            match_state = "confirmed" if not needs_review else "unconfirmed"

        output.append(
            MaintenanceDraftRowOut(
                machine=machine,
                kind="module",
                description=name.name_en,
                material_no=material_no,
                type_code=type_code,
                workload_kind="module" if type_code else None,
                workload_id=None,
                component_type=name.component_type,
                workload=workload,
                amount=_money(workload * rate) if workload is not None else Decimal("0.00"),
                match_state=match_state,
                needs_review=needs_review,
            )
        )

    return output


def maintenance_draft(
    db: Session,
    customer_id: str,
    machine_names: list[str],
    scope_subsidiary_id: str | None = None,
) -> MaintenanceDraftOut:
    """Build the priced maintenance draft for selected customer machines.

    The technician rate always comes from the customer's subsidiary.

    Workloads are resolved from the global component workload master:
    normal component types use their component type, while model-based types
    such as Slicer use their canonical product/model.
    """
    customer = db.scalar(
        select(Customer).where(
            Customer.customer_id == customer_id
        )
    )

    if customer is None or (
        scope_subsidiary_id is not None
        and customer.subsidiary_id != scope_subsidiary_id
    ):
        raise CustomerNotFound(customer_id)

    rate_row = db.scalar(
        select(PriceList).where(
            PriceList.subsidiary_id == customer.subsidiary_id
        )
    )

    if rate_row is None:
        raise RateNotConfigured(customer.subsidiary_id)

    rate = rate_row.tech_rate

    rows = list(
        db.scalars(
            select(Equipment).where(
                Equipment.customer_id == customer_id,
                Equipment.equipment_name.in_(machine_names),
            )
        )
    )

    # ---------------------------------------------------------------
    # Machine lines
    # ---------------------------------------------------------------

    machine_types = {
        _machine_type_of(_machine_rows(rows, name))
        for name in machine_names
    }

    resolved_by_type: dict[str | None, object] = {}

    for machine_type in machine_types:
        if (
            machine_type is not None
            and machine_type not in resolved_by_type
        ):
            resolved_by_type[machine_type] = resolve_line(
                db,
                machine_type,
            )

    # ---------------------------------------------------------------
    # Component dictionary
    # ---------------------------------------------------------------

    all_rows = [
        _machine_rows(rows, name)
        for name in machine_names
    ]

    # Look up the dictionary by the model-aware key first, then by the legacy
    # collapse, so both dictionaries imported before and after the
    # normalize_material_no fix resolve.
    candidate_keys: set[str] = set()
    for group in all_rows:
        for row in group:
            if row.material_no:
                candidate_keys.add(normalize_material_no(row.material_no))
                candidate_keys.add(legacy_base_material_no(row.material_no))

    names_by_key: dict[str, ComponentName] = {}

    if candidate_keys:
        for name in db.scalars(
            select(ComponentName).where(
                ComponentName.material_no.in_(candidate_keys)
            )
        ):
            names_by_key[name.material_no] = name

    # ---------------------------------------------------------------
    # Global workload master
    #
    # Ordinary module hours come from the legacy type_code table
    # (module_workloads), loaded independently from the imported dictionary so
    # a dictionary re-import cannot overwrite manually configured workloads.
    # ---------------------------------------------------------------

    legacy_by_code = {
        row.type_code: row
        for row in db.scalars(select(ModuleWorkload))
    }

    # ---------------------------------------------------------------
    # Build draft
    # ---------------------------------------------------------------

    draft_rows: list[MaintenanceDraftRowOut] = []

    for machine, group in zip(machine_names, all_rows):
        machine_type = _machine_type_of(group)

        draft_rows.append(
            _line_row(
                machine,
                group,
                rate,
                resolved_by_type.get(machine_type),
            )
        )

        draft_rows.extend(
            _module_rows(
                machine,
                group,
                rate,
                names_by_key,
                legacy_by_code,
            )
        )

    total_workload = sum(
        (
            row.workload
            for row in draft_rows
            if row.workload is not None
        ),
        Decimal("0"),
    )

    total_amount = sum(
        (row.amount for row in draft_rows),
        Decimal("0"),
    )

    return MaintenanceDraftOut(
        customer_id=customer_id,
        subsidiary_id=customer.subsidiary_id,
        currency=rate_row.currency,
        tech_rate=rate,
        rows=draft_rows,
        total_workload=total_workload,
        total_amount=_money(total_amount),
    )
