"""Annex 6 - Training & Optimization (master pages 21-23).

Responsibility: English source of the training annex, gated by the
``training_optimization`` module in content.SECTIONS. Sections 5 (Follow-Up)
is always included when the module is selected; subsections are gated by
their Guardian option.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex6.title", "text": "ANNEX 6 - TRAINING & OPTIMIZATION"},
    {
        "type": "p",
        "id": "annex6.tagline",
        "text": "Operator training, maintenance training, line optimization and EPIP audits.",
    },
    {
        "type": "p",
        "id": "annex6.intro",
        "text": (
            "The Training & Optimization module provides selected activities intended to improve "
            "machine operation, maintenance capability and production performance."
        ),
    },

    {
        "type": "sub",
        "option": "operator_training",
        "blocks": [
            {"type": "h2", "id": "annex6.operator.title", "text": "1. Operator Training"},
            {
                "type": "p",
                "id": "annex6.operator.p1",
                "text": "Weber shall provide operator-focused training for the selected Equipment.",
            },
            {
                "type": "p",
                "id": "annex6.operator.p2",
                "text": "The training content may include, depending on the machine and agreed objectives:",
            },
            {
                "type": "ul",
                "id": "annex6.operator.includes",
                "items": [
                    "correct machine operation;",
                    "basic machine settings;",
                    "operating routines;",
                    "product changeover;",
                    "operator-level checks;",
                    "cleaning and inspection considerations;",
                    "identification of abnormal machine behavior; and",
                    "good operating practices.",
                ],
            },
            {
                "type": "kv",
                "id": "annex6.operator.quantity",
                "label": "Number of Sessions / Days",
                "token": "Operator_Training_Quantity",
            },
            {
                "type": "p",
                "id": "annex6.operator.p3",
                "text": "Training shall be conducted for the Customer's nominated personnel.",
            },
            {
                "type": "p",
                "id": "annex6.operator.p4",
                "text": (
                    "Unless expressly stated otherwise, training does not constitute formal "
                    "certification of Customer personnel."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "maintenance_training",
        "blocks": [
            {"type": "h2", "id": "annex6.maintenance.title", "text": "2. Maintenance Training"},
            {
                "type": "p",
                "id": "annex6.maintenance.p1",
                "text": "Weber shall provide technical training for the Customer's maintenance personnel.",
            },
            {"type": "p", "id": "annex6.maintenance.p2", "text": "Training may include:"},
            {
                "type": "ul",
                "id": "annex6.maintenance.includes",
                "items": [
                    "machine construction and functional principles;",
                    "preventive maintenance;",
                    "inspection points;",
                    "wear-part identification;",
                    "troubleshooting methodology;",
                    "mechanical adjustment;",
                    "relevant electrical or pneumatic components;",
                    "maintenance documentation; and",
                    "recommended maintenance practices.",
                ],
            },
            {
                "type": "kv",
                "id": "annex6.maintenance.quantity",
                "label": "Number of Sessions / Days",
                "token": "Maintenance_Training_Quantity",
            },
        ],
    },

    {
        "type": "sub",
        "option": "line_optimization",
        "blocks": [
            {"type": "h2", "id": "annex6.optimization.title", "text": "3. Line Optimization"},
            {
                "type": "p",
                "id": "annex6.optimization.p1",
                "text": (
                    "Weber shall perform an agreed review of the selected production line with the "
                    "objective of identifying opportunities to improve performance."
                ),
            },
            {"type": "p", "id": "annex6.optimization.p2", "text": "The activity may include:"},
            {
                "type": "ul",
                "id": "annex6.optimization.includes",
                "items": [
                    "review of machine parameters;",
                    "observation of production;",
                    "analysis of operating conditions;",
                    "review of line interaction;",
                    "identification of performance restrictions;",
                    "adjustment of selected parameters where appropriate; and",
                    "recommendations for further improvement.",
                ],
            },
            {
                "type": "kv",
                "id": "annex6.optimization.quantity",
                "label": "Number of Optimization Activities",
                "token": "Line_Optimization_Quantity",
            },
            {
                "type": "p",
                "id": "annex6.optimization.p3",
                "text": (
                    "Line Optimization does not constitute a guarantee of a specific output, yield, "
                    "OEE, giveaway reduction or other performance improvement unless a specific "
                    "performance commitment is expressly agreed in writing."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "epip_audit",
        "blocks": [
            {"type": "h2", "id": "annex6.epip.title", "text": "4. EPIP Audit"},
            {
                "type": "p",
                "id": "annex6.epip.p1",
                "text": "Weber shall perform an EPIP audit on the Equipment or lines specified in Annex 1.",
            },
            {
                "type": "p",
                "id": "annex6.epip.p2",
                "text": (
                    "The audit shall include an assessment of the selected line and a report "
                    "identifying relevant findings, opportunities and priority actions."
                ),
            },
            {
                "type": "p",
                "id": "annex6.epip.p3",
                "text": (
                    "Where applicable, the results shall be reviewed with the Customer and "
                    "incorporated into the ongoing Guardian action plan."
                ),
            },
            {"type": "kv", "id": "annex6.epip.quantity", "label": "Number of EPIP Audits", "token": "EPIP_Audit_Quantity"},
            {"type": "kv", "id": "annex6.epip.lines", "label": "Lines Covered", "token": "EPIP_Lines"},
            {
                "type": "p",
                "id": "annex6.epip.p4",
                "text": (
                    "Corrective actions, repairs, upgrades or parts resulting from the audit are "
                    "not included unless expressly stated."
                ),
            },
        ],
    },

    # 5. Follow-Up (always when the module is selected)
    {"type": "h2", "id": "annex6.followup.title", "text": "5. Follow-Up"},
    {
        "type": "p",
        "id": "annex6.followup.p1",
        "text": (
            "Where included in the selected package, Weber may conduct follow-up meetings or "
            "calls before and after selected activities to review:"
        ),
    },
    {
        "type": "ul",
        "id": "annex6.followup.items",
        "items": [
            "agreed objectives;",
            "completed activities;",
            "observed impact;",
            "outstanding action items;",
            "technical priorities; and",
            "next actions.",
        ],
    },
]
