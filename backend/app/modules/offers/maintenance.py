"""Maintenance draft: rows priced server-side as workload × branch tech rate.

A maintenance line has no price of its own. Its amount is the row's standard
hours (workload) times the technician hourly rate of the customer's subsidiary
(prices.tech_rate).

Workloads are global master data:

* Normal component types use one workload per component type.
* Special model-based component types (currently Slicer) use one workload
  per pure product/model, ignoring variants such as "-Basic", "-Extended",
  "-1" and "-2".

Unknown workloads are never invented. They produce needs_review=True and
amount=0.00 until an administrator configures them.
"""

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.customers.service import CustomerNotFound
from app.modules.component_names.models import ComponentName, ComponentWorkload
from app.modules.component_names.service import normalize_material_no
from app.modules.component_names.workloads import workload_identity
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


def _clean_text(value: str | None) -> str:
    """Normalize whitespace without changing the actual wording."""
    if not value:
        return ""
    return " ".join(value.split()).strip()


def _machine_rows(rows: list[Equipment], name: str) -> list[Equipment]:
    return [row for row in rows if row.equipment_name == name]


def _machine_type_of(rows: list[Equipment]) -> str | None:
    """The machine's type: the first row that carries one."""
    for row in rows:
        if row.machine_type:
            return row.machine_type
    return None


def _workload_key(name: ComponentName) -> str | None:
    """Resolve a dictionary row to its stable workload source key."""
    component_type = _clean_text(name.component_type)
    if not component_type:
        return None
    return workload_identity(
        component_type,
        name.name_en,
        name.description,
    )[0]


def _workload_index(
    workloads: list[ComponentWorkload],
) -> dict[str, ComponentWorkload]:
    """Index workload master by stable identity, never by its editable name."""
    result: dict[str, ComponentWorkload] = {}

    for workload in workloads:
        result[workload.source_key] = workload

    return result


def _line_row(
    machine: str,
    rows: list[Equipment],
    rate: Decimal,
    resolved,
) -> MaintenanceDraftRowOut:
    machine_type = _machine_type_of(rows)

    if machine_type is None or resolved is None:
        return MaintenanceDraftRowOut(
            machine=machine,
            kind="line",
            description=machine_type,
            workload=None,
            amount=Decimal("0.00"),
            match_state="unknown",
            needs_review=True,
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
    )


def _module_rows(
    machine: str,
    rows: list[Equipment],
    rate: Decimal,
    names_by_material: dict[str, ComponentName],
    workloads_by_key: dict[tuple[str, str], ComponentWorkload],
) -> list[MaintenanceDraftRowOut]:
    """Build one maintenance row per distinct material number.

    The same material can appear multiple times in the imported equipment
    data. It is therefore collapsed to one row so its workload is not counted
    repeatedly.
    """
    materials = sorted(
        {
            normalize_material_no(row.material_no)
            for row in rows
            if row.material_no
        }
    )

    output: list[MaintenanceDraftRowOut] = []

    for material_no in materials:
        name = names_by_material.get(material_no)

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

        workload_key = _workload_key(name)
        workload_row = (
            workloads_by_key.get(workload_key)
            if workload_key is not None
            else None
        )

        workload = (
            workload_row.workload
            if workload_row is not None
            else None
        )

        description = (
            workload_row.name
            if workload_row is not None
            else name.name_en
        )

        known = workload is not None
        needs_review = not known or (workload_row is not None and workload_row.needs_review)
        match_state = (
            "unknown"
            if not known
            else "unconfirmed"
            if needs_review
            else "confirmed"
        )

        output.append(
            MaintenanceDraftRowOut(
                machine=machine,
                kind="module",
                description=description,
                material_no=material_no,
                type_code=name.type_code,
                workload=workload,
                amount=(
                    _money(workload * rate)
                    if known
                    else Decimal("0.00")
                ),
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

    materials = {
        normalize_material_no(row.material_no)
        for group in all_rows
        for row in group
        if row.material_no
    }

    names_by_material: dict[str, ComponentName] = {}

    if materials:
        for name in db.scalars(
            select(ComponentName).where(
                ComponentName.material_no.in_(materials)
            )
        ):
            names_by_material[name.material_no] = name

    # ---------------------------------------------------------------
    # Global workload master
    #
    # We deliberately load the workload catalog independently from the
    # imported dictionary. This means a dictionary re-import cannot
    # overwrite manually configured workloads.
    # ---------------------------------------------------------------

    workloads = list(
        db.scalars(
            select(ComponentWorkload)
        )
    )

    workloads_by_key = _workload_index(workloads)

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
                names_by_material,
                workloads_by_key,
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
