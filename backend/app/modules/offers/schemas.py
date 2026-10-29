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

# Guardian service catalog: the real services a salesperson can put in an
# offer. Commercial conditions (response times, discounts, account team),
# the content the software already knows (inspection, equipment, prices) and
# activities owned by another service are NOT selectable and never appear
# here: they are derived from the offer fields.
GUARDIAN_SERVICES = {
    "customer_service": (
        "hotline",
        "remote_support",
        "on_site_assistance",
    ),
    "spare_parts": (
        "supply_conditions",
        "priority_logistics",
        "parts_recommendations",
    ),
    "academy": (
        "operator_training",
        "maintenance_training",
    ),
    "blade_solutions": (
        "knife_consulting",
        "sharpening",
        "blade_supply_program",
    ),
    "optimization": (
        "epip_audit",
        "line_optimization",
        "improvement_plan",
        "performance_mro_review",
    ),
    "digital_services": (
        "factory_cockpit",
        "monitoring",
    ),
}

# Always part of the agreement: the contract states them, nobody ticks them.
GUARDIAN_AUTO_SERVICES = (
    "inspection",
    "machine_checklist",
    "inspection_report",
)

# Basic Kit adds these to Annex 2 without asking: they are what the kit is.
GUARDIAN_BASIC_KIT_SERVICES = ("preventive_maintenance", "maintenance_kit")

# Selections saved before the service catalog was redesigned. They are read,
# mapped to the current keys and rewritten on the next save, so old offers
# keep their contract text instead of silently losing services.
GUARDIAN_LEGACY_MODULES = {
    "maintenance_inspection": None,  # inspection is automatic now
    "service_support": "customer_service",
    "parts_availability": "spare_parts",
    "training_optimization": "academy",
    "blade_solutions": "blade_solutions",
    "digital_services": "digital_services",
}
GUARDIAN_LEGACY_OPTIONS = {
    "standard_hotline": "hotline",
    "priority_response": "on_site_assistance",
    "parts_discount": "supply_conditions",
    "priority_handling": "priority_logistics",
    "recommended_parts_list": "parts_recommendations",
    "blade_discount": "blade_supply_program",
    "stock_agreement": "blade_supply_program",
    "sharpening_assessment": "sharpening",
    "blade_application_review": "knife_consulting",
    "performance_review": "performance_mro_review",
    "mro_review": "performance_mro_review",
    "dedicated_account_team": "performance_mro_review",
    # Options that became automatic or moved to a commercial condition.
    "inspection": None,
    "machine_checklist": None,
    "inspection_report": None,
    "preventive_maintenance": None,
    "maintenance_kit": None,
}

GUARDIAN_MODULE_KEYS = frozenset(GUARDIAN_SERVICES)
GUARDIAN_SERVICE_KEYS = frozenset(
    service for services in GUARDIAN_SERVICES.values() for service in services
)
GUARDIAN_SELECTION_KEYS = frozenset(
    GUARDIAN_MODULE_KEYS
    | GUARDIAN_SERVICE_KEYS
    | frozenset(GUARDIAN_LEGACY_MODULES)
    | frozenset(GUARDIAN_LEGACY_OPTIONS)
)


def normalize_guardian_selections(value: list[str] | tuple[str, ...]) -> list[str]:
    """Current module/service keys for any selection ever stored.

    Legacy keys are translated key by key, duplicates collapse and options
    carry their parent module so the stored shape stays consistent. Unknown
    keys are dropped: they belong to a retired catalog and would only make
    the offer render empty sections.
    """
    mapped: list[str] = []
    for key in value:
        if key in GUARDIAN_MODULE_KEYS or key in GUARDIAN_SERVICE_KEYS:
            mapped.append(key)
        elif key in GUARDIAN_LEGACY_MODULES:
            mapped.append(GUARDIAN_LEGACY_MODULES[key])
        elif key in GUARDIAN_LEGACY_OPTIONS:
            mapped.append(GUARDIAN_LEGACY_OPTIONS[key])
    current: list[str] = []
    for key in mapped:
        if key is not None and key not in current:
            current.append(key)
    for module, services in GUARDIAN_SERVICES.items():
        if any(service in current for service in services) and module not in current:
            current.append(module)
    return current


def document_guardian_selections(
    value: list[str] | tuple[str, ...], offer_type: str | None
) -> list[str]:
    """Selections the contract needs: current keys plus the derived services.

    Inspection is always part of the agreement and Basic Kit always brings
    preventive maintenance and the maintenance kit. Neither is stored on the
    offer (nobody ticked them), but the PDF has to state them.
    """
    selections = normalize_guardian_selections(value)
    derived = list(GUARDIAN_AUTO_SERVICES)
    if offer_type == "guardian":
        derived.extend(GUARDIAN_BASIC_KIT_SERVICES)
    for key in derived:
        if key not in selections:
            selections.append(key)
    return selections


def _validate_guardian_selections(value: list[str]) -> list[str]:
    """Accept current or legacy keys and return the canonical stored list."""
    if len(value) != len(set(value)):
        raise ValueError("guardian selections must not contain duplicates")
    unknown = set(value) - GUARDIAN_SELECTION_KEYS
    if unknown:
        raise ValueError(f"unknown Guardian selections: {', '.join(sorted(unknown))}")
    return normalize_guardian_selections(value)


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
    # Guardian contract discriminator. Campaign does not exist: removed.
    # audit uses no basic kit but keeps the branch discount; off_guardian
    # drops the branch discount; the "Basic Kit" guardian type sends
    # offer_type guardian with basic_kit True.
    offer_type: Literal["guardian", "audit", "off_guardian"] = "audit"
    basic_kit: bool = False
    # Inspected machines count. Report hours are never client data: the
    # service derives them as equipment_count x 2 (legacy Actualizar-
    # ListadoMaquinas). Persistence recomputes the count from the stored
    # items, so this field is only the dry-run preview number.
    equipment_count: int = Field(ge=0)
    # Module lines, so the preview can show the amounts the gross is spread
    # over (legacy "RepartirCostes") exactly as the saved offer will.
    items: list[OfferItemCreate] = Field(default_factory=list)


class OfferCalculateOut(BaseModel):
    """Engine breakdown. total = gross, total_end = net."""

    work_hours: Decimal
    bk_hours: Decimal
    report_hours: Decimal
    total_hours: Decimal
    num_days: int
    # Amount of each module line once the gross is spread over them (legacy
    # "RepartirCostes"), in the order of the items that were sent.
    line_amounts: list[Decimal]
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
    line row first and its modules after it. basic_kit_hours and
    basic_kit_price are the sums from the basic_kit catalog for the selected
    machines (zero when no machine has a kit): the offer turns them into the
    bk_hours/bk_price pricing inputs when its Guardian Type is Basic Kit.
    """

    customer_id: str
    subsidiary_id: str | None
    currency: str
    tech_rate: Decimal
    rows: list[MaintenanceDraftRowOut]
    total_workload: Decimal
    total_amount: Decimal
    basic_kit_hours: Decimal = Decimal("0")
    basic_kit_price: Decimal = Decimal("0")


class OfferStatusUpdate(BaseModel):
    """Status change (e.g. CLOSE OFFER). Values validated against the domain list."""

    status: str = Field(min_length=1, max_length=32)


class CustomAnnex(BaseModel):
    """One customer-authored annex appended to the printed contract.

    Validation is deliberately strict on the title (a headingless annex page
    would be a silent defect) and permissive on the body: the print modal
    auto-saves while the user types, so an empty body is a valid transient
    state. Unknown {{Tokens}} in the body are never resolved: user text
    reaches the PDF verbatim.

    body_html holds the sanitized HTML extracted from an uploaded .docx
    (offers.docx_annex); when present it replaces the plain-text body at
    render time. Both travel in the same JSON entry so the annex list keeps
    one shape whether it was typed or uploaded.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    body: str = Field(default="", max_length=20000)
    body_html: str | None = Field(default=None, max_length=500_000)


class OfferDocumentSettingsIn(BaseModel):
    """Partial update of the print settings (Print PDF modal auto-save).

    Every field is optional: omitted or null keeps the stored value. Scope
    validation matches OfferCreate/Update so the modal cannot persist a
    selection the full-edit form would reject. language is only length-checked
    here (same rule as OfferCreate): app.weber.locales is the single authority
    on supported contract languages and reports garbage as 422 when the PDF
    is generated, keeping the core module free of weber imports.
    """

    guardian_selections: list[str] | None = Field(default=None, max_length=40)
    language: str | None = Field(default=None, max_length=32)
    custom_annexes: list[CustomAnnex] | None = Field(default=None, max_length=10)

    @field_validator("guardian_selections")
    @classmethod
    def guardian_selections_are_valid(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _validate_guardian_selections(value)


class StatusCount(BaseModel):
    status: str
    count: int


class MonthCount(BaseModel):
    month: str
    count: int


class CustomerOfferRow(BaseModel):
    """One customer rollup, shared by the dashboard lists and the ranking."""

    customer_id: str
    account_name: str
    count: int
    total_end: Decimal
    last_offer_id: str | None = None
    last_offer_date: date | None = None
    last_status: str | None = None


class StatusDetailRow(BaseModel):
    status: str
    count: int
    total_end: Decimal
    customers: list[CustomerOfferRow]


class AreaRow(BaseModel):
    area: str
    count: int
    total_end: Decimal


class RankingRow(BaseModel):
    customer_id: str
    account_name: str | None = None
    count: int
    total_end: Decimal
    last_offer_id: str | None = None
    last_status: str | None = None
    last_offer_date: date | None = None


class OffersSummaryOut(BaseModel):
    total: int
    by_status: list[StatusCount]
    status_details: list[StatusDetailRow]
    monthly: list[MonthCount]
    ranking: list[RankingRow]
    customers_total: int
    customers: list[CustomerOfferRow]
    customers_with_offers_total: int
    customers_without_offers_total: int
    customers_without_offers: list[CustomerOfferRow]
    pending_total: int
    pending_customers: list[CustomerOfferRow]
    realized_total: int
    realized_customers: list[CustomerOfferRow]
    by_area: list[AreaRow]


class OfferCreate(BaseModel):
    """Create input. Totals are computed server-side, never accepted."""

    customer_id: str = Field(min_length=1, max_length=64)
    id_guardian_offer: str | None = Field(default=None, min_length=1, max_length=64)
    status: str = Field(default="Pending response", min_length=1, max_length=32)
    responsible_person: str | None = Field(default=None, max_length=128)
    language: str | None = Field(default=None, max_length=32)
    inspection_frequency: str | None = Field(default=None, max_length=32)
    general_comments: str | None = Field(default=None, max_length=2000)
    offer_date: date | None = None
    guardian_selections: list[str] = Field(default_factory=list, max_length=40)
    custom_annexes: list[CustomAnnex] = Field(default_factory=list, max_length=10)
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
    # None = keep the stored annexes: the full-edit PUT is sent by forms that
    # do not know about them (and must not wipe what the print modal saved).
    custom_annexes: list[CustomAnnex] | None = Field(default=None, max_length=10)
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
    offer_type: str
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
    custom_annexes: list[CustomAnnex]
    items: list[OfferItemOut] = Field(default_factory=list)

    @field_validator("guardian_selections")
    @classmethod
    def _current_guardian_selections(cls, value: list[str]) -> list[str]:
        """Old offers are shown with the current service keys."""
        return normalize_guardian_selections(value)
