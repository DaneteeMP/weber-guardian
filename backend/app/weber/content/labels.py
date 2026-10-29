"""English module labels and document order for the Guardian agreement.

Responsibility: single English source for the Guardian module names, used by
the Annex 1 checklist, the Configuration Summary table and the renderer.
Translations override them via the ``module.<key>`` message id (see es.py).
"""

from __future__ import annotations

MODULE_LABELS: dict[str, str] = {
    "customer_service": "Customer Service",
    "spare_parts": "Spare Parts & Availability",
    "academy": "Academy",
    "blade_solutions": "Knife & Blade Solutions",
    "optimization": "Optimization & Performance",
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

# English service labels, keyed by Guardian service. Used by the token values
# of the Selected_*_Options scope tokens (see app.weber.pdf.values).
OPTION_LABELS: dict[str, str] = {
    # Automatic content and Basic Kit: never selectable, but printed.
    "inspection": "Inspection",
    "machine_checklist": "Machine Checklist",
    "inspection_report": "Inspection Report",
    "preventive_maintenance": "Preventive Maintenance",
    "maintenance_kit": "Spare Parts / Maintenance Kit",
    "hotline": "Hotline",
    "remote_support": "Remote Support",
    "on_site_assistance": "On-site Assistance",
    "supply_conditions": "Supply Conditions",
    "priority_logistics": "Priority Logistics",
    "parts_recommendations": "Parts Recommendations",
    "operator_training": "Operator Training",
    "maintenance_training": "Maintenance Training",
    "knife_consulting": "Knife Consulting",
    "sharpening": "Sharpening",
    "blade_supply_program": "Blade Supply Programme",
    "epip_audit": "EPIP Audit",
    "line_optimization": "Line Optimization",
    "improvement_plan": "Improvement Plan",
    "performance_mro_review": "Performance & MRO Review",
    "factory_cockpit": "Factory Cockpit",
    "monitoring": "Monitoring",
}
