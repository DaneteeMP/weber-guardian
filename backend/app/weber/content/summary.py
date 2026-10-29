"""Configuration Summary (master pages 26-27).

Responsibility: the customer-facing overview of the purchased Guardian
configuration (customer, site, dates, equipment, value and the selected
scope). The signature page lives in content/signatures.py so the commercial
breakdown can print between the two.

Translation rules: a kv node with a literal ``value`` is translated as
``<id>`` (label) and ``<id>.value`` (value); column headings use their own
node ids.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "summary.title", "text": "GUARDIAN CONFIGURATION SUMMARY"},
    {
        "type": "p",
        "id": "summary.intro",
        "text": (
            "The following summary confirms the Guardian configuration purchased by the "
            "Customer under this Agreement."
        ),
    },
    {"type": "kv", "id": "summary.customer", "label": "Customer", "token": "Customer_Legal_Name"},
    {"type": "kv", "id": "summary.site", "label": "Site", "token": "Customer_Site"},
    {"type": "kv", "id": "summary.start", "label": "Contract Start", "token": "Contract_Start_Date"},
    {"type": "kv", "id": "summary.term", "label": "Contract Term", "token": "Contract_Duration"},
    {
        "type": "kv",
        "id": "summary.equipment",
        "label": "Equipment Covered",
        "value": "{{Number_Of_Machines}} machines / {{Number_Of_Lines}} production lines",
    },
    {"type": "kv", "id": "summary.value", "label": "Annual / Contract Value", "token": "Total_Contract_Value"},

    {"type": "h2", "id": "summary.scope.title", "text": "Your Guardian"},
    {
        "type": "kv_table",
        "id": "summary.scope",
        "headers": [
            {"id": "summary.scope.h_module", "text": "Guardian Module"},
            {"id": "summary.scope.h_scope", "text": "Selected Scope"},
        ],
        "rows": [
            {"id": "summary.scope.inspection", "label": "Inspection & Maintenance", "token": "Selected_Maintenance_Options"},
            {"module": "customer_service", "token": "Selected_Service_Support_Options"},
            {"module": "spare_parts", "token": "Selected_Parts_Options"},
            {"module": "blade_solutions", "token": "Selected_Blade_Options"},
            {"module": "academy", "token": "Selected_Training_Options"},
            {"module": "optimization", "token": "Selected_Optimization_Options"},
            {"module": "digital_services", "token": "Selected_Digital_Options"},
        ],
    },
]
