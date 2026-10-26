"""Annex 2 - Maintenance & Inspection (master pages 12-15).

Responsibility: English source of the maintenance annex. The annex itself is
gated by the ``maintenance_inspection`` module (see content.SECTIONS); each
``sub`` wrapper is gated by its Guardian option. Sections 1, 7, 8 and 9 are
always included when the module is selected. Internal generation rules are
excluded.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex2.title", "text": "ANNEX 2 - MAINTENANCE & INSPECTION"},
    {
        "type": "p",
        "id": "annex2.tagline",
        "text": "Inspection, preventive maintenance and machine-condition services.",
    },

    # 1. Purpose (always when the module is selected)
    {"type": "h2", "id": "annex2.purpose.title", "text": "1. Purpose"},
    {
        "type": "p",
        "id": "annex2.purpose.p1",
        "text": (
            "The Maintenance & Inspection module is intended to assess and maintain the condition "
            "of the Equipment identified in Annex 1, identify required technical actions and "
            "support reliable operation and maintenance planning."
        ),
    },
    {
        "type": "p",
        "id": "annex2.purpose.p2",
        "text": "The exact activities included depend on the options selected in the Guardian configuration.",
    },

    {
        "type": "sub",
        "option": "inspection",
        "blocks": [
            {"type": "h2", "id": "annex2.inspection.title", "text": "2. Inspection"},
            {
                "type": "p",
                "id": "annex2.inspection.p1",
                "text": "Weber shall perform inspections of the selected Equipment at the frequency stated in Annex 1.",
            },
            {
                "type": "p",
                "id": "annex2.inspection.p2",
                "text": "An inspection may include, where applicable to the selected Equipment:",
            },
            {
                "type": "ul",
                "id": "annex2.inspection.includes",
                "items": [
                    "review of the general machine condition;",
                    "inspection based on Weber's machine- or module-specific checklist;",
                    "review of relevant sensors and electrical components;",
                    "inspection of drives, belts and mechanical components;",
                    "inspection of pneumatic components;",
                    "inspection of seals and machine housings;",
                    "verification and adjustment of mechanically movable components where reasonably required;",
                    "review of relevant machine settings;",
                    "identification of visible wear or abnormalities;",
                    "identification of outstanding repair or maintenance requirements;",
                    "discussion of known issues with the Customer's responsible personnel; and",
                    "functional verification following the inspection where appropriate.",
                ],
            },
            {
                "type": "p",
                "id": "annex2.inspection.p3",
                "text": (
                    "Where useful and operationally possible, Weber may review the production "
                    "process using the Customer's original product."
                ),
            },
            {
                "type": "p",
                "id": "annex2.inspection.p4",
                "text": (
                    "Opening of specific protected machine areas, such as weighing or cutting-head "
                    "housings, shall be carried out where technically appropriate and agreed."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "machine_checklist",
        "blocks": [
            {"type": "h2", "id": "annex2.checklist.title", "text": "3. Machine Checklist"},
            {
                "type": "p",
                "id": "annex2.checklist.p1",
                "text": "Weber shall document the inspection using the applicable Weber inspection checklist.",
            },
            {
                "type": "p",
                "id": "annex2.checklist.p2",
                "text": "The checklist records the inspected elements and their observed condition at the time of the inspection.",
            },
            {
                "type": "p",
                "id": "annex2.checklist.p3",
                "text": (
                    "The checklist is intended as a technical service record and does not "
                    "constitute certification that the Equipment is free from defects or that no "
                    "future failure may occur."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "inspection_report",
        "blocks": [
            {"type": "h2", "id": "annex2.report.title", "text": "4. Inspection Report"},
            {
                "type": "p",
                "id": "annex2.report.p1",
                "text": "Following the inspection, Weber shall provide an inspection report summarizing the principal findings.",
            },
            {"type": "p", "id": "annex2.report.p2", "text": "The report may include:"},
            {
                "type": "ul",
                "id": "annex2.report.includes",
                "items": [
                    "condition findings;",
                    "identified wear;",
                    "recommended maintenance or repairs;",
                    "recommended spare parts;",
                    "technical observations;",
                    "identified risks requiring further attention; and",
                    "recommended priorities or next actions.",
                ],
            },
            {
                "type": "p",
                "id": "annex2.report.p3",
                "text": (
                    "Where appropriate, Weber may prepare a separate quotation for recommended "
                    "parts, repairs, upgrades or other activities arising from the inspection."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "preventive_maintenance",
        "blocks": [
            {"type": "h2", "id": "annex2.preventive.title", "text": "5. Preventive Maintenance"},
            {
                "type": "p",
                "id": "annex2.preventive.p1",
                "text": "Weber shall perform the preventive maintenance activities expressly defined for the Equipment in Annex 1.",
            },
            {"type": "p", "id": "annex2.preventive.p2", "text": "Preventive maintenance may include:"},
            {
                "type": "ul",
                "id": "annex2.preventive.includes",
                "items": [
                    "mechanical adjustment;",
                    "lubrication;",
                    "cleaning of technically relevant components;",
                    "replacement of defined filters, seals or wear components;",
                    "checking and adjustment of drives and belts;",
                    "checking of pneumatic elements;",
                    "checking of electrical and sensor components; and",
                    "other machine-specific preventive maintenance tasks identified in the applicable Weber maintenance plan.",
                ],
            },
            {
                "type": "p",
                "id": "annex2.preventive.p3",
                "text": (
                    "Replacement parts, wear parts and consumables are not included unless "
                    "expressly stated in Annex 1 or in an agreed maintenance kit."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "maintenance_kit",
        "blocks": [
            {"type": "h2", "id": "annex2.kit.title", "text": "6. Spare Parts / Maintenance Kit"},
            {
                "type": "p",
                "id": "annex2.kit.p1",
                "text": (
                    "The maintenance kit shall contain only the parts expressly identified in the "
                    "applicable quotation or equipment schedule."
                ),
            },
            {"type": "p", "id": "annex2.kit.p2", "text": "The price of the kit shall be shown separately in Annex 1."},
            {
                "type": "p",
                "id": "annex2.kit.p3",
                "text": "Unused parts remain subject to the commercial conditions stated in Annex 1.",
            },
        ],
    },

    # 7-9 always when the module is selected
    {"type": "h2", "id": "annex2.repairs.title", "text": "7. Additional Maintenance and Repairs"},
    {
        "type": "p",
        "id": "annex2.repairs.p1",
        "text": (
            "Repairs and corrective maintenance identified during an inspection are not included "
            "in the standard inspection price unless specifically stated otherwise."
        ),
    },
    {
        "type": "p",
        "id": "annex2.repairs.p2",
        "text": "Where additional work is recommended, Weber shall obtain Customer approval or issue a separate quotation.",
    },

    {"type": "h2", "id": "annex2.frequency.title", "text": "8. Inspection Frequency"},
    {"type": "kv", "id": "annex2.frequency.value", "label": "Frequency", "token": "Inspection_Frequency"},
    {
        "type": "kv",
        "id": "annex2.frequency.planned",
        "label": "Planned Inspections per Contract Year",
        "token": "Number_Of_Inspections",
    },
    {"type": "p", "id": "annex2.frequency.p1", "text": "The actual schedule shall be coordinated between Weber and the Customer."},

    {"type": "h2", "id": "annex2.hours.title", "text": "9. Service Hours"},
    {
        "type": "p",
        "id": "annex2.hours.p1",
        "text": "Services shall normally be performed during: {{Standard_Service_Hours}}",
    },
    {"type": "p", "id": "annex2.hours.p2", "text": "Work requested outside these hours may be subject to additional charges."},
]
