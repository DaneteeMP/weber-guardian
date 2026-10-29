"""Token values for the Guardian agreement templates.

Responsibility: build the ``{{Token}}`` dictionary the renderer resolves
into the customer contract, from an OfferDocument and the canonical locale.

Who uses it: app.weber.pdf.renderer; tests/test_renderer.py asserts the key
set covers every token referenced by app.weber.content.

Deliberate differences vs the legacy ``_token_values`` (raster engine):
- money and dates are formatted with app.weber.locales (Babel), so a Spanish
  contract shows "1.234,50 €" and "21 de septiembre de 2026" instead of the
  fixed English pattern;
- there are no {{Line_N}}/{{Serial_N}} machine tokens: equipment rows are
  built from ``doc.lines`` (machine_groups below), so every machine shows
  regardless of count, with no "See Annex 1 continuation" shortcut.

Data the system does not hold yet (agreement number, contract start date,
payment terms, service-level quantities, ...) is present with an empty value,
exactly like the legacy renderer: blank is the honest state, not a default.
The contract module fills those keys when the data lands. Every key always
exists so resolve_tokens never hides a typo.
"""
from __future__ import annotations

import re
from decimal import Decimal

from app.core.subsidiaries import EXECUTOR_CODES, normalize_subsidiary
from app.modules.offers.document import OfferDocument, OfferLine
from app.modules.offers.schemas import GUARDIAN_OPTIONS_BY_MODULE
from app.weber import contract_es
from app.weber.content import get_text, labels
from app.weber.locales import format_date, format_money, normalize_locale

DEFAULT_SUBSIDIARY = "ES"
_TOKEN_PATTERN = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")

# Tokens for the Selected_*_Options rows of Annex 1 and the summary.
_SCOPE_TOKENS = {
    "maintenance_inspection": "Selected_Maintenance_Options",
    "service_support": "Selected_Service_Support_Options",
    "parts_availability": "Selected_Parts_Options",
    "blade_solutions": "Selected_Blade_Options",
    "training_optimization": "Selected_Training_Options",
    "digital_services": "Selected_Digital_Options",
}


def document_locale(doc: OfferDocument) -> str:
    """Canonical contract locale (ValueError on garbage, "en" when blank)."""
    return normalize_locale(doc.language)


def guardian_type_label(locale: str, offer_type: str | None) -> str:
    """Customer-facing Guardian type label, translated per locale."""
    key = offer_type if offer_type in labels.GUARDIAN_TYPE_LABELS else "audit"
    return get_text(locale, f"guardian_type.{key}", labels.GUARDIAN_TYPE_LABELS[key])


def machine_groups(lines: tuple[OfferLine, ...]) -> list[tuple[str, list[OfferLine]]]:
    """Group offer lines by equipment name, preserving first-seen order."""
    groups: dict[str, list[OfferLine]] = {}
    for line in lines:
        if line.equipment:
            groups.setdefault(line.equipment, []).append(line)
    return list(groups.items())


def selected_scope_text(selections: set[str], module: str) -> str:
    """Comma-separated English labels of the options selected for a module."""
    return ", ".join(
        labels.OPTION_LABELS[option]
        for option in GUARDIAN_OPTIONS_BY_MODULE[module]
        if option in selections
    )


def _resolve_executor(doc: OfferDocument) -> tuple[dict[str, str], bool]:
    """Weber legal entity for the customer's owning subsidiary.

    Returns the block plus a provisional flag: True when the subsidiary has
    no executor data, in which case only the canonical name is filled (never
    another filial's address) - same rule as the legacy renderer and
    contract_es. The renderer turns the flag into the cover DRAFT banner.
    """
    canonical = normalize_subsidiary(doc.subsidiary_id) or DEFAULT_SUBSIDIARY
    code = EXECUTOR_CODES.get(canonical, canonical)
    block = contract_es.EXECUTORS.get(code)
    if block is None:
        return {"name": canonical, "street": "", "city": "", "country": "", "place_date": ""}, True
    return block, False


def executor_block(doc: OfferDocument) -> dict[str, str]:
    """Weber legal entity block (see _resolve_executor)."""
    return _resolve_executor(doc)[0]


def executor_is_provisional(doc: OfferDocument) -> bool:
    """True when the subsidiary has no real legal block yet (draft cover)."""
    return _resolve_executor(doc)[1]


def token_values(doc: OfferDocument, locale: str) -> dict[str, str]:
    """Return every {{Token}} value for this document in this locale."""
    selections = set(doc.guardian_selections)
    groups = machine_groups(doc.lines)
    machine_names = [name for name, _ in groups]
    executor = executor_block(doc)

    line_total = sum((line.import_amount for line in doc.lines), start=Decimal("0"))
    customer_city = " ".join(
        value for value in (doc.account_city, doc.account_province) if value
    )
    site = doc.customer_site or ", ".join(
        value
        for value in (doc.account_city, doc.account_province, doc.account_country)
        if value
    )

    def money(value: Decimal) -> str:
        return format_money(value, locale, doc.currency)

    bands = {rate.band: rate for rate in doc.band_rates}

    values = {
        "Agreement_Number": "",
        "Offer_Number": doc.number,
        "Offer_Date": format_date(doc.offer_date, locale),
        "Contract_Start_Date": "",
        "Contract_Duration": "",
        "Renewal_Term": "",
        "Termination_Notice_Period": "",
        "Billing_Frequency": "",
        "Weber_Legal_Entity": executor["name"],
        "Weber_Address": executor["street"],
        "Weber_Postcode_City": executor["city"],
        "Weber_Country": executor["country"],
        "Customer_Legal_Name": doc.account_name,
        "Customer_Number": doc.customer_number or "",
        "Customer_Site": site,
        "Customer_Address": "",
        "Customer_Postcode_City": customer_city,
        "Customer_Country": doc.account_country or "",
        "Currency": doc.currency,
        # Contract time-band rates (with / without maintenance contract). Empty
        # when the subsidiary has not configured them.
        "Band1_Rate_Without": money(bands[1].rate_without_contract) if 1 in bands else "",
        "Band1_Rate_With": money(bands[1].rate_with_contract) if 1 in bands else "",
        "Band2_Rate_Without": money(bands[2].rate_without_contract) if 2 in bands else "",
        "Band2_Rate_With": money(bands[2].rate_with_contract) if 2 in bands else "",
        "Band3_Rate_Without": money(bands[3].rate_without_contract) if 3 in bands else "",
        "Band3_Rate_With": money(bands[3].rate_with_contract) if 3 in bands else "",
        "Number_Of_Machines": str(len(machine_names)),
        "Number_Of_Lines": str(len(machine_names)),
        "Inspection_Amount": money(line_total),
        # Legacy "RepartirCostes": travel, diets and hotel are already spread
        # over the module prices, so the travel line of the commercial summary
        # is zero and inspection + kit - discount = total contract value.
        "Travel_Amount": money(Decimal("0")),
        "Parts_Kit_Amount": money(doc.bk_price),
        "Service_Support_Amount": "",
        "Parts_Module_Amount": "",
        "Blade_Module_Amount": "",
        "Training_Module_Amount": "",
        "Digital_Module_Amount": "",
        "Guardian_Discount": money(doc.discount),
        "Total_Contract_Value": money(doc.total_end),
        "Payment_Terms": "",
        "Price_Adjustment_Rule": "",
        "Travel_Conditions": "",
        "Freight_Conditions": "",
        "Governing_Law": "",
        "Jurisdiction": "",
        "Special_Commercial_Conditions": doc.general_comments or "",
        "Inspection_Frequency": doc.inspection_frequency or "",
        "Guardian_Type": guardian_type_label(locale, doc.offer_type),
        "Number_Of_Inspections": "",
        "Standard_Service_Hours": "",
        "Hotline_Service_Hours": "",
        "Hotline_Number": "",
        "Service_Email": "",
        "Priority_Response_Target": "",
        "Parts_Discount": "",
        "Parts_Delivery_Condition": "",
        "Freight_Free_Threshold": "",
        "Blade_Discount": "",
        "Operator_Training_Quantity": "",
        "Maintenance_Training_Quantity": "",
        "Line_Optimization_Quantity": "",
        "EPIP_Audit_Quantity": "",
        "EPIP_Lines": "",
        "Factory_Cockpit_Lines": ", ".join(machine_names),
        "Performance_Review_Frequency": "",
        "MRO_Review_Frequency": "",
        "MRO_Target": "",
        "Account_Review_Frequency": "",
    }
    for module, token in _SCOPE_TOKENS.items():
        values[token] = selected_scope_text(selections, module)
    return values


def resolve_tokens(text: str, values: dict[str, str]) -> str:
    """Replace {{Token}} placeholders with their values.

    Raises ValueError for a token the value map does not know: a typo in the
    content must fail the build, never render an empty field silently.
    """
    missing = set(_TOKEN_PATTERN.findall(text)) - set(values)
    if missing:
        raise ValueError(f"unknown tokens: {sorted(missing)}")
    return _TOKEN_PATTERN.sub(lambda match: values[match.group(1)], text)
