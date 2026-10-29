"""Annex 2 - Maintenance & Inspection (Global Appendix 3 content, gated by options).

Responsibility: English source of the maintenance annex. The module is gated by
``maintenance_inspection`` in content.SECTIONS; each service clause is gated by
its Guardian option. Only data that the system currently holds is printed;
paragraphs that would need missing values are not written here.
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
            "The Maintenance & Inspection module is intended to assess and maintain the "
            "condition of the Equipment identified in Annex 1, identify the required "
            "technical actions and support reliable operation and maintenance planning."
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
            {"type": "h2", "id": "annex2.inspection.title", "text": "S301 Scheduled Technical Inspection"},
            {
                "type": "p",
                "id": "annex2.inspection.p1",
                "text": (
                    "An inspection evaluates the condition of the selected equipment at the "
                    "agreed interval using the applicable line/module-based checklist. The "
                    "technical scope shall be adapted to equipment type and configuration."
                ),
            },
            {
                "type": "p",
                "id": "annex2.inspection.p2",
                "text": (
                    "Before the inspection, Weber and the Customer will review known operating "
                    "issues, equipment history and planned production availability. After the "
                    "inspection, findings are discussed with the designated Customer "
                    "representative and recorded in an inspection report."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "machine_checklist",
        "blocks": [
            {"type": "h2", "id": "annex2.checklist.title", "text": "Machine Checklist"},
            {
                "type": "p",
                "id": "annex2.checklist.p1",
                "text": (
                    "For slicer lines, the standard checklist may include the following, where "
                    "technically applicable and safely accessible:"
                ),
            },
            {
                "type": "ul",
                "id": "annex2.checklist.items",
                "items": [
                    "function test with original product where available; equipment condition "
                    "and safety-related observations;",
                    "sensors, electronics, machine settings, electrical and pneumatic functions; "
                    "drives, timing belts and selected drive trains;",
                    "mechanical adjustments, housings and seals, conveyors and moving elements; "
                    "line modules and ancillary Weber components;",
                    "identification of wear, pending repairs, machine anomalies and "
                    "recommendations for further actions;",
                    "access to scale or cutter head housings only as expressly agreed and safely "
                    "authorised;",
                    "preparation of a module-based inspection checklist, report and optional "
                    "follow-up parts quotation.",
                ],
            },
            {
                "type": "p",
                "id": "annex2.checklist.p2",
                "text": (
                    "For Weber packaging machines, the inspection checklist can also include "
                    "defined packaging-specific condition checks. Third-party labellers, pumps "
                    "and end-of-line devices are excluded unless expressly listed."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "inspection_report",
        "blocks": [
            {"type": "h2", "id": "annex2.report.title", "text": "S305 Follow-up Visit & Reporting"},
            {
                "type": "p",
                "id": "annex2.report.p1",
                "text": (
                    "Where agreed, Weber will perform a defined follow-up after an inspection "
                    "or maintenance event, which may be onsite or remote depending on the agreed "
                    "service."
                ),
            },
            {
                "type": "p",
                "id": "annex2.report.p2",
                "text": (
                    "A follow-up visit is not automatically included with an inspection and may "
                    "be conditional on Weber performing specified maintenance work, as stated in "
                    "the Customer schedule."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "preventive_maintenance",
        "blocks": [
            {"type": "h2", "id": "annex2.preventive.title", "text": "S303 Preventive Maintenance"},
            {
                "type": "p",
                "id": "annex2.preventive.p1",
                "text": (
                    "Preventive maintenance consists of planned adjustments, lubrication, "
                    "cleaning of defined technical components and replacement of specified wear "
                    "parts according to the agreed activity list and equipment constraints."
                ),
            },
            {
                "type": "p",
                "id": "annex2.preventive.p2",
                "text": (
                    "The scope of parts supplied, parts installed, labour allowance, frequency "
                    "and required downtime shall be specified per machine in Annex 1."
                ),
            },
            {
                "type": "p",
                "id": "annex2.preventive.p3",
                "text": (
                    "Preventive maintenance is distinct from a corrective repair; services "
                    "outside the planned task list are separately authorised and invoiced unless "
                    "expressly included."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "maintenance_kit",
        "blocks": [
            {"type": "h2", "id": "annex2.kit.title", "text": "S402 Basic Spare Parts Kit - Supply Only"},
            {
                "type": "p",
                "id": "annex2.kit.p1",
                "text": (
                    "The Basic Spare Parts Kit consists of the exact articles and quantities "
                    "listed in the signed Kit Schedule. It supports planned replacement or "
                    "Customer-held stock, but is not an unlimited consumables entitlement."
                ),
            },
            {
                "type": "p",
                "id": "annex2.kit.p2",
                "text": (
                    "Weber supplies the listed items under the specified ordering, delivery and "
                    "price conditions. Installation is not included in a supply-only kit."
                ),
            },
        ],
    },

    # Module-level: corrective work (always when the module is selected)
    {"type": "h2", "id": "annex2.repairs.title", "text": "S304 Corrective Maintenance / Repair"},
    {
        "type": "p",
        "id": "annex2.repairs.p1",
        "text": (
            "Repair work follows an identified failure, fault or defect and seeks to restore an "
            "agreed condition, subject to access, technical feasibility and parts availability."
        ),
    },
    {
        "type": "p",
        "id": "annex2.repairs.p2",
        "text": (
            "Unless a repair allocation is expressly priced and selected, corrective labour, "
            "replacement parts, travel and other costs are quoted or charged according to the "
            "selected service rates and Customer authorisation."
        ),
    },
    {
        "type": "p",
        "id": "annex2.repairs.p3",
        "text": (
            "An attendance, fault diagnosis or repair task shall not be represented as a "
            "guaranteed restoration of production within a particular period unless expressly "
            "agreed in writing."
        ),
    },

    # Inspection frequency (subsidiary/offer data)
    {"type": "h2", "id": "annex2.frequency.title", "text": "Inspection Frequency"},
    {"type": "kv", "id": "annex2.frequency.value", "label": "Frequency", "token": "Inspection_Frequency"},
    {
        "type": "p",
        "id": "annex2.frequency.p1",
        "text": "The actual schedule shall be coordinated between Weber and the Customer.",
    },
]
