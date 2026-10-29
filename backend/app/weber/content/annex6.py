"""Annex 6 - Training & Optimization (Global Appendices 5 and 7, gated by options).

Responsibility: English source of the training/optimization annex. The module
is gated by ``training_optimization``; each clause is gated by its Guardian
option. Only data the system currently holds is printed.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex6.title", "text": "ANNEX 6 - TRAINING & OPTIMIZATION"},
    {
        "type": "p",
        "id": "annex6.tagline",
        "text": "Operator and maintenance training, line optimization and EPIP audits.",
    },
    {
        "type": "p",
        "id": "annex6.intro",
        "text": (
            "The Training & Optimization module offers selected activities intended to improve "
            "machine operation, maintenance capability and production performance."
        ),
    },

    {
        "type": "sub",
        "option": "operator_training",
        "blocks": [
            {"type": "h2", "id": "annex6.operator.title", "text": "S501 Operator Training"},
            {
                "type": "p",
                "id": "annex6.operator.p1",
                "text": (
                    "Training for operators on safe and efficient use of defined equipment, "
                    "including selected operating procedures, adjustments, cleaning practice and "
                    "basic operating checks to the extent appropriate."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "maintenance_training",
        "blocks": [
            {"type": "h2", "id": "annex6.maintenance.title", "text": "S502 Maintenance Technician Training"},
            {
                "type": "p",
                "id": "annex6.maintenance.p1",
                "text": (
                    "Training for the Customer maintenance team on machine architecture, "
                    "preventive checks, fault recognition, safe troubleshooting and maintenance "
                    "procedures, within the agreed access permissions."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "line_optimization",
        "blocks": [
            {"type": "h2", "id": "annex6.optimization.title", "text": "S702 Line Optimization"},
            {
                "type": "p",
                "id": "annex6.optimization.p1",
                "text": (
                    "Weber reviews identified technical and production constraints and may "
                    "recommend or perform agreed machine-setting or process improvements within "
                    "the accepted scope."
                ),
            },
            {
                "type": "p",
                "id": "annex6.optimization.p2",
                "text": "Any capital upgrades or repair items remain separate.",
            },
        ],
    },

    {
        "type": "sub",
        "option": "epip_audit",
        "blocks": [
            {"type": "h2", "id": "annex6.epip.title", "text": "S701 EPIP / Equipment Audit"},
            {
                "type": "p",
                "id": "annex6.epip.p1",
                "text": (
                    "Weber performs the selected in-depth equipment assessment / EPIP-style audit "
                    "on specified production lines and provides an assessment report."
                ),
            },
            {
                "type": "p",
                "id": "annex6.epip.p2",
                "text": (
                    "The report shall distinguish observed condition, priority actions, "
                    "recommended repairs and improvement opportunities."
                ),
            },
        ],
    },
]
