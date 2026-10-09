"""Offer HTTP contracts (Pydantic). Backend owns all prices.

Clients never send totals: CalculateOut/OfferOut carry them, Create
schemas do not. All money is Decimal (EUR explicit).
"""
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Money = Decimal
MAX12 = 9999999999.99

GUARDIAN_OPTIONS_BY_MODULE = {
    "maintenance_inspection": (
        "inspection",
        "machine_checklist",
        "inspection_report",
        "preventive_maintenance",
        "maintenance_kit",
    ),
    "service_support": ("standard_hotline", "remote_support", "priority_response"),
    "parts_availability": ("parts_discount", "priority_handling", "recommended_parts_list"),
    "blade_solutions": (
        "blade_discount",
        "stock_agreement",
        "sharpening_assessment",
        "blade_application_review",
    ),
    "training_optimization": (
        "operator_training",
        "maintenance_training",
        "line_optimization",
        "epip_audit",
    ),
    "digital_services": (
        "factory_cockpit",
        "performance_review",
        "mro_review",
        "dedicated_account_team",
    ),
}
GUARDIAN_SELECTION_KEYS = frozenset(
    key
    for module, options in GUARDIAN_OPTIONS_BY_MODULE.items()
    for key in (module, *options)
)


def _validate_guardian_selections(value: list[str]) -> list[str]:
    """Validate selected module/option keys and require parents for options."""
    if len(value) != len(set(value)):
        raise ValueError("guardian selections must not contain duplicates")
    unknown = set(value) - GUARDIAN_SELECTION_KEYS
    if unknown:
        raise ValueError(f"unknown Guardian selections: {', '.join(sorted(unknown))}")
    selected = set(value)
    for module, options in GUARDIAN_OPTIONS_BY_MODULE.items():
        if any(option in selected for option in options) and module not in selected:
            raise ValueError(f"Guardian options require module selection: {module}")
    return value


class OfferItemCreate(BaseModel):
    equipment: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None, max_length=500)
    import_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal(str(MAX12)))
    workload: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))


class OfferItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    row_no: int
    equipment: str | None
    description: str | None
    import_amount: Decimal
    workload: Decimal


class OfferCalculateIn(BaseModel):
    """Dry-run input: aggregated hours + rates. No persistence."""

    work_hours: Decimal = Field(ge=Decimal("0"))
    bk_hours: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    report_hours: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    trip_hours_base: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    km: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    km_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    tech_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    diet_full_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    diet_half_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    hotel_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    discount_rate: Decimal = Field(default=Decimal("0.15"), ge=Decimal("0"), le=Decimal("1"))
    bk_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    currency: str = Field(default="EUR", min_length=1, max_length=8)


class OfferCalculateOut(BaseModel):
    """Engine breakdown. total = gross, total_end = net."""

    work_hours: Decimal
    bk_hours: Decimal
    report_hours: Decimal
    total_hours: Decimal
    num_days: int
    trip_cost: Decimal
    trip_hours: Decimal
    diets: Decimal
    hotel_nights_cost: Decimal
    expenses: Decimal
    hours_import: Decimal
    discount: Decimal
    bk_price: Decimal
    total: Decimal
    total_end: Decimal
    currency: str


class MaintenanceDraftIn(BaseModel):
    """Input of the maintenance draft: the customer and the selected machines."""

    model_config = ConfigDict(str_strip_whitespace=True)

    customer_id: str = Field(min_length=1, max_length=64)
    machine_names: list[str] = Field(min_length=1, max_length=200)


class MaintenanceDraftRowOut(BaseModel):
    """One draft row, priced server-side as workload × branch tech rate.

    workload is None when nobody has set hours yet: the amount stays 0.00
    and the row is flagged for review until an editor fixes the data in the
    Workload Catalog. offers never edit workloads or prices themselves.
    needs_review is also True when the hours exist but are unverified (the
    linked workload carries needs_review).
    """

    machine: str
    kind: Literal["line", "module"]
    description: str | None
    material_no: str | None = None
    type_code: str | None = None
    # Which catalog row priced this line: the machine line (equipment_catalog,
    # keyed by machine_type) or the global workload (workload_rules, by id).
    # Traceability only; hours are edited in the Workload Catalog.
    # workload_id is None for a module whose material has no workload yet.
    workload_kind: Literal["line", "module"] | None = None
    workload_id: uuid.UUID | None = None
    line_code: str | None = None
    component_type: str | None = None
    workload: Decimal | None
    amount: Decimal
    match_state: Literal["confirmed", "unconfirmed", "unknown"]
    needs_review: bool


class MaintenanceDraftOut(BaseModel):
    """Draft rows for the selected machines of one customer.

    The rate and currency come from the customer's subsidiary price row, so
    every country prices its own hours. Rows arrive in machine order with the
    line row first and its modules after it.
    """

    customer_id: str
    subsidiary_id: str | None
    currency: str
    tech_rate: Decimal
    rows: list[MaintenanceDraftRowOut]
    total_workload: Decimal
    total_amount: Decimal


class OfferStatusUpdate(BaseModel):
    """Status change (e.g. CLOSE OFFER). Values validated against the domain list."""

    status: str = Field(min_length=1, max_length=32)


class StatusCount(BaseModel):
    status: str
    count: int


class MonthCount(BaseModel):
    month: str
    count: int


class RankingRow(BaseModel):
    customer_id: str
    count: int
    total_end: Decimal


class OffersSummaryOut(BaseModel):
    total: int
    by_status: list[StatusCount]
    monthly: list[MonthCount]
    ranking: list[RankingRow]


class OfferCreate(BaseModel):
    """Create input. Totals are computed server-side, never accepted."""

    customer_id: str = Field(min_length=1, max_length=64)
    id_guardian_offer: str | None = Field(default=None, min_length=1, max_length=64)
    status: str = Field(default="Draft", min_length=1, max_length=32)
    responsible_person: str | None = Field(default=None, max_length=128)
    language: str | None = Field(default=None, max_length=32)
    inspection_frequency: str | None = Field(default=None, max_length=32)
    general_comments: str | None = Field(default=None, max_length=2000)
    offer_date: date | None = None
    guardian_selections: list[str] = Field(default_factory=list, max_length=40)
    pricing: OfferCalculateIn
    items: list[OfferItemCreate] = Field(default_factory=list)

    @field_validator("guardian_selections")
    @classmethod
    def guardian_selections_are_valid(cls, value: list[str]) -> list[str]:
        return _validate_guardian_selections(value)


class OfferUpdate(BaseModel):
    """Full edit input. The guardian number never changes through edits."""

    status: str = Field(min_length=1, max_length=32)
    responsible_person: str | None = Field(default=None, max_length=128)
    language: str | None = Field(default=None, max_length=32)
    inspection_frequency: str | None = Field(default=None, max_length=32)
    general_comments: str | None = Field(default=None, max_length=2000)
    offer_date: date | None = None
    guardian_selections: list[str] = Field(default_factory=list, max_length=40)
    pricing: OfferCalculateIn
    items: list[OfferItemCreate] = Field(default_factory=list)

    @field_validator("guardian_selections")
    @classmethod
    def guardian_selections_are_valid(cls, value: list[str]) -> list[str]:
        return _validate_guardian_selections(value)


class OfferOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    id_guardian_offer: str
    customer_id: str
    status: str
    responsible_person: str | None
    language: str | None
    inspection_frequency: str | None
    currency: str
    work_hours: Decimal
    bk_hours: Decimal
    report_hours: Decimal
    total_hours: Decimal
    trip_hours: Decimal
    trip_cost: Decimal
    diets: Decimal
    hotel_cost: Decimal
    expenses: Decimal
    hours_import: Decimal
    discount: Decimal
    bk_price: Decimal
    total: Decimal
    total_end: Decimal
    general_comments: str | None
    created_by: uuid.UUID | None
    created_at: datetime
    offer_date: date | None
    guardian_selections: list[str]
    items: list[OfferItemOut] = Field(default_factory=list)
