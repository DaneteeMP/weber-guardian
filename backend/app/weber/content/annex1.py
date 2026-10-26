"""Annex 1 - Equipment & Commercial Schedule (master pages 10-11).

Responsibility: always-included commercial annex. Equipment rows are built by
the renderer from the offer lines (equipment_table), not from numbered
{{Line_N}} tokens. The internal note "This Annex is always included in the
customer contract" is excluded from the customer copy.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex1.title", "text": "ANNEX 1 - EQUIPMENT & COMMERCIAL SCHEDULE"},

    # 1. Contract Information
    {"type": "h2", "id": "annex1.info.title", "text": "1. Contract Information"},
    {"type": "kv", "id": "annex1.info.customer", "label": "Customer", "token": "Customer_Legal_Name"},
    {"type": "kv", "id": "annex1.info.customer_no", "label": "Customer No.", "token": "Customer_Number"},
    {"type": "kv", "id": "annex1.info.site", "label": "Site", "token": "Customer_Site"},
    {"type": "kv", "id": "annex1.info.agreement_no", "label": "Agreement No.", "token": "Agreement_Number"},
    {"type": "kv", "id": "annex1.info.start_date", "label": "Contract Start Date", "token": "Contract_Start_Date"},
    {"type": "kv", "id": "annex1.info.term", "label": "Initial Term", "token": "Contract_Duration"},
    {"type": "kv", "id": "annex1.info.billing", "label": "Billing Frequency", "token": "Billing_Frequency"},
    {"type": "kv", "id": "annex1.info.currency", "label": "Currency", "token": "Currency"},

    # 2. Equipment Covered
    {"type": "h2", "id": "annex1.equipment.title", "text": "2. Equipment Covered"},
    {
        "type": "p",
        "id": "annex1.equipment.intro",
        "text": "Only the Equipment and machine modules listed below are covered by the Guardian Services.",
    },
    {
        "type": "equipment_table",
        "id": "annex1.equipment",
        "headers": [
            {"id": "annex1.equipment.h_line", "text": "Production Line"},
            {"id": "annex1.equipment.h_machine", "text": "Machine"},
            {"id": "annex1.equipment.h_serial", "text": "Serial No."},
            {"id": "annex1.equipment.h_type", "text": "Type"},
            {"id": "annex1.equipment.h_modules", "text": "Included Modules / Components"},
            {"id": "annex1.equipment.h_frequency", "text": "Service Frequency"},
        ],
    },

    # 3. Selected Guardian Modules
    {"type": "h2", "id": "annex1.modules.title", "text": "3. Selected Guardian Modules"},
    {"type": "p", "id": "annex1.modules.intro", "text": "The following Guardian modules form part of this Agreement:"},
    {"type": "module_checklist", "id": "annex1.modules"},
    {
        "type": "p",
        "id": "annex1.modules.outro",
        "text": (
            "Only the Annexes corresponding to the selected modules above are attached to and "
            "form part of the Agreement."
        ),
    },

    # 4. Commercial Summary
    {"type": "h2", "id": "annex1.summary.title", "text": "4. Commercial Summary"},
    {
        "type": "kv_table",
        "id": "annex1.summary",
        "headers": [
            {"id": "annex1.summary.h_item", "text": "Commercial Item"},
            {"id": "annex1.summary.h_amount", "text": "Amount"},
        ],
        "rows": [
            {"module": "maintenance_inspection", "token": "Inspection_Amount"},
            {"id": "annex1.summary.travel", "label": "Travel / Expenses", "token": "Travel_Amount"},
            {"id": "annex1.summary.kit", "label": "Spare Parts / Maintenance Kit", "token": "Parts_Kit_Amount"},
            {"module": "service_support", "token": "Service_Support_Amount"},
            {"module": "parts_availability", "token": "Parts_Module_Amount"},
            {"module": "blade_solutions", "token": "Blade_Module_Amount"},
            {"module": "training_optimization", "token": "Training_Module_Amount"},
            {"module": "digital_services", "token": "Digital_Module_Amount"},
            {"id": "annex1.summary.discount", "label": "Guardian Discount", "token": "Guardian_Discount"},
            {"id": "annex1.summary.total", "label": "TOTAL CONTRACT VALUE", "token": "Total_Contract_Value", "total": True},
        ],
    },
    {
        "type": "p",
        "id": "annex1.summary.vat_note",
        "text": "All amounts are exclusive of applicable VAT unless stated otherwise.",
    },

    # 5. Billing
    {"type": "h2", "id": "annex1.billing.title", "text": "5. Billing"},
    {"type": "kv", "id": "annex1.billing.frequency", "label": "Billing Frequency", "token": "Billing_Frequency"},
    {"type": "kv", "id": "annex1.billing.terms", "label": "Payment Terms", "token": "Payment_Terms"},
    {"type": "kv", "id": "annex1.billing.adjustment", "label": "Price Adjustment", "token": "Price_Adjustment_Rule"},
    {"type": "kv", "id": "annex1.billing.travel", "label": "Travel Conditions", "token": "Travel_Conditions"},
    {"type": "kv", "id": "annex1.billing.freight", "label": "Freight Conditions", "token": "Freight_Conditions"},

    # 6. Special Commercial Conditions
    {"type": "h2", "id": "annex1.special.title", "text": "6. Special Commercial Conditions"},
    {
        "type": "p",
        "id": "annex1.special.conditions",
        "text": "{{Special_Commercial_Conditions}}",
    },
]
