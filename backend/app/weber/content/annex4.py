"""Annex 4 - Parts & Availability (master pages 17-18).

Responsibility: English source of the parts annex, gated by the
``parts_availability`` module in content.SECTIONS. Section 5 (Delivery
Conditions) is always included when the module is selected.

Translation rule: a kv node with a literal ``value`` (not a token) is
translated as ``<id>`` for the label and ``<id>.value`` for the value.
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
            "The Parts & Availability module supports structured spare-parts planning and access "
            "to Weber original spare parts for the Equipment covered by this Agreement."
        ),
    },

    {
        "type": "sub",
        "option": "parts_discount",
        "blocks": [
            {"type": "h2", "id": "annex4.discount.title", "text": "2. Parts Discount"},
            {
                "type": "p",
                "id": "annex4.discount.p1",
                "text": (
                    "The Customer shall receive the following discount on eligible Weber spare "
                    "parts for Equipment covered by the Guardian Agreement:"
                ),
            },
            {
                "type": "p",
                "id": "annex4.discount.amount",
                "text": "Guardian Parts Discount {{Parts_Discount}} %",
            },
            {
                "type": "p",
                "id": "annex4.discount.p2",
                "text": "The discount applies to Weber original spare parts unless otherwise stated.",
            },
            {"type": "p", "id": "annex4.discount.p3", "text": "The following may be excluded:"},
            {
                "type": "ul",
                "id": "annex4.discount.excluded",
                "items": [
                    "exchange parts;",
                    "blades;",
                    "special-price items;",
                    "third-party products;",
                    "freight and express charges;",
                    "services and labor; and",
                    "items already subject to another special price or discount.",
                ],
            },
            {"type": "p", "id": "annex4.discount.p4", "text": "Discounts are not cumulative unless expressly agreed."},
        ],
    },

    {
        "type": "sub",
        "option": "priority_handling",
        "blocks": [
            {"type": "h2", "id": "annex4.handling.title", "text": "3. Priority Handling"},
            {
                "type": "p",
                "id": "annex4.handling.p1",
                "text": (
                    "Parts inquiries and orders relating to Equipment covered by this Agreement "
                    "shall receive priority handling within the applicable Weber parts organization."
                ),
            },
            {"type": "p", "id": "annex4.handling.p2", "text": "Priority handling includes accelerated internal processing where reasonably possible."},
            {
                "type": "p",
                "id": "annex4.handling.p3",
                "text": (
                    "It does not constitute a guaranteed delivery time where the requested part is "
                    "not available from stock or where delivery depends on external suppliers, "
                    "production or transportation."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "recommended_parts_list",
        "blocks": [
            {"type": "h2", "id": "annex4.parts_list.title", "text": "4. Recommended Parts List"},
            {
                "type": "p",
                "id": "annex4.parts_list.p1",
                "text": (
                    "Weber shall provide, where technically and commercially available, a "
                    "recommended spare-parts list for the selected Equipment."
                ),
            },
            {
                "type": "lines",
                "id": "annex4.parts_list.categories",
                "items": [
                    "A - Local / immediately available items: Parts normally available from the responsible Weber organization.",
                    "B - Central stock items: Parts normally available from Weber central stock.",
                    "C - Recommended customer-stock items: Critical or higher-risk spare parts which Weber recommends the Customer hold locally.",
                    "D - Wear parts: Parts expected to require replacement depending on usage.",
                    "E - Make-to-order / long-lead-time parts: Parts which are not normally stocked and may require manufacturing or extended procurement lead time.",
                ],
            },
            {
                "type": "p",
                "id": "annex4.parts_list.p2",
                "text": (
                    "The recommended parts list constitutes a recommendation based on the available "
                    "machine configuration and service information. It is not a guarantee that every "
                    "possible failure scenario is covered."
                ),
            },
        ],
    },

    # 5. Delivery Conditions (always when the module is selected)
    {"type": "h2", "id": "annex4.delivery.title", "text": "5. Delivery Conditions"},
    {"type": "p", "id": "annex4.delivery.p1", "text": "Stock availability and delivery conditions shall be subject to Annex 1."},
    {
        "type": "kv",
        "id": "annex4.delivery.condition",
        "label": "Standard Delivery Condition",
        "token": "Parts_Delivery_Condition",
    },
    {
        "type": "kv",
        "id": "annex4.delivery.threshold",
        "label": "Freight-Free Threshold",
        "token": "Freight_Free_Threshold",
    },
    {
        "type": "kv",
        "id": "annex4.delivery.courier",
        "label": "Express / Courier Costs",
        "value": "Charged separately unless otherwise agreed.",
    },
]
