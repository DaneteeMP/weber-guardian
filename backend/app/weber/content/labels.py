"""English module labels and document order for the Guardian agreement.

Responsibility: single English source for the six Guardian module names, used
by the Annex 1 checklist, the Configuration Summary table and the renderer.
Translations override them via the ``module.<key>`` message id (see es.py).
"""

from __future__ import annotations

MODULE_LABELS: dict[str, str] = {
    "maintenance_inspection": "Maintenance & Inspection",
    "service_support": "Service Support",
    "parts_availability": "Parts & Availability",
    "blade_solutions": "Blade Solutions",
    "training_optimization": "Training & Optimization",
    "digital_services": "Digital Services",
}

# Fixed document order for checklists and summary rows.
MODULES: tuple[str, ...] = tuple(MODULE_LABELS)

# Guardian contract types, keyed by the API ``offer_type`` value. "audit" is
# the internal value of the customer-facing "Inspection" type; "guardian" is
# the Basic Kit. Translations override them via ``guardian_type.<key>``.
GUARDIAN_TYPE_LABELS: dict[str, str] = {
    "audit": "Inspection",
    "off_guardian": "Off-Guardian",
    "guardian": "Basic Kit",
}

# English option labels, keyed by Guardian option. Used by the token values
# of the Selected_*_Options scope tokens (see app.weber.pdf.values).
OPTION_LABELS: dict[str, str] = {
    "inspection": "Inspection / Annual Inspection",
    "machine_checklist": "Machine Checklist",
    "inspection_report": "Inspection Report",
    "preventive_maintenance": "Preventive Maintenance",
    "maintenance_kit": "Spare Parts / Maintenance Kit",
    "standard_hotline": "Standard Hotline",
    "remote_support": "Remote Support",
    "priority_response": "Priority Response",
    "parts_discount": "Parts Discount",
    "priority_handling": "Priority Handling",
    "recommended_parts_list": "Recommended Parts List",
    "blade_discount": "Blade Discount",
    "stock_agreement": "Stock Agreement",
    "sharpening_assessment": "Sharpening Assessment",
    "blade_application_review": "Blade Application Review",
    "operator_training": "Operator Training",
    "maintenance_training": "Maintenance Training",
    "line_optimization": "Line Optimization",
    "epip_audit": "EPIP Audit",
    "factory_cockpit": "Factory Cockpit",
    "performance_review": "Performance Review",
    "mro_review": "MRO Review",
    "dedicated_account_team": "Dedicated Account Team",
}
