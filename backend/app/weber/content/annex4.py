"""Annex 4 - Parts & Availability (Global Appendices 2 and 4, gated by options).

Responsibility: English source of the parts annex. The module is gated by
``parts_availability`` in content.SECTIONS; each service clause is gated by
its Guardian option. Only data the system currently holds is printed.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex4.title", "text": "ANNEX 4 - PARTS & AVAILABILITY"},
    {
        "type": "p",
        "id": "annex4.tagline",
        "text": "Spare-parts commercial conditions, priority handling and recommended stock.",
    },

    # 1. Purpose (always when the module is selected)
    {"type": "h2", "id": "annex4.purpose.title", "text": "1. Purpose"},
    {
        "type": "p",
        "id": "annex4.purpose.p1",
        "text": (
            "The Parts & Availability module supports structured spare-parts planning and "
            "access to original Weber spare parts for the Equipment covered by this Agreement."
        ),
    },

    {
        "type": "sub",
        "option": "parts_discount",
        "blocks": [
            {"type": "h2", "id": "annex4.discount.title", "text": "S201 Spare Parts Commercial Conditions"},
            {
                "type": "p",
                "id": "annex4.discount.p1",
                "text": (
                    "Selected spare parts categories are supplied at the agreed prices and "
                    "discounts, with exclusions and treatment of exchange parts, blades, special "
                    "orders and upgraded equipment expressly stated."
                ),
            },
            {
                "type": "p",
                "id": "annex4.discount.p2",
                "text": "Discounts are not cumulative unless expressly agreed.",
            },
        ],
    },

    {
        "type": "sub",
        "option": "priority_handling",
        "blocks": [
            {"type": "h2", "id": "annex4.handling.title", "text": "S203 Priority Parts Handling"},
            {
                "type": "p",
                "id": "annex4.handling.p1",
                "text": (
                    "Subject to availability and agreed order placement, eligible orders may "
                    "receive priority processing or dispatch according to the local arrangement."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "recommended_parts_list",
        "blocks": [
            {"type": "h2", "id": "annex4.parts_list.title", "text": "S202 Recommended Spare Parts List"},
            {
                "type": "p",
                "id": "annex4.parts_list.p1",
                "text": (
                    "Weber may prepare a machine-specific recommended spare parts list, "
                    "distinguishing planned wear items from high-risk spare parts recommended for "
                    "Customer stock. Lists shall be reviewed according to equipment age, "
                    "specification and supportability."
                ),
            },
            {
                "type": "p",
                "id": "annex4.parts_list.p2",
                "text": (
                    "Where the local subsidiary applies the Benelux-style classification, A/B "
                    "denote recommended wear/critical parts and C/D/E may identify local stock, "
                    "other Weber stock or manufacture-on-order; a given part can carry both a "
                    "recommendation and an availability status."
                ),
            },
            {
                "type": "ul",
                "id": "annex4.parts_list.categories",
                "items": [
                    "A - Recommended wear parts.",
                    "B - Critical / higher-failure-risk spare parts proposed for onsite stock.",
                    "C - Available from local Weber stock (subject to confirmation).",
                    "D - Available from another Weber location (subject to confirmation).",
                    "E - Made to order / no current stock.",
                ],
            },
            {
                "type": "p",
                "id": "annex4.parts_list.p3",
                "text": (
                    "The list is advisory, not a warranty of stock availability, suitability for "
                    "all configurations or a commitment to automatically supply the recommended "
                    "quantities."
                ),
            },
            {
                "type": "p",
                "id": "annex4.parts_list.p4",
                "text": (
                    "Weber supplies an advisory machine-specific parts list, without material "
                    "supply or installation unless separately ordered."
                ),
            },
        ],
    },
]
