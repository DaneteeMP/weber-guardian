"""Annex 5 - Blade Solutions (master pages 19-21).

Responsibility: English source of the blade annex, gated by the
``blade_solutions`` module in content.SECTIONS. Every numbered subsection is
gated by its Guardian option; the module introduction is always included.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex5.title", "text": "ANNEX 5 - BLADE SOLUTIONS"},
    {
        "type": "p",
        "id": "annex5.tagline",
        "text": "Commercial, availability and technical support for Weber blade programs.",
    },
    {
        "type": "p",
        "id": "annex5.intro",
        "text": (
            "The Blade Solutions module is intended to support the correct selection, "
            "availability, use and management of Weber blades, including the principle "
            "\"Right Blade, Right Application\"."
        ),
    },

    {
        "type": "sub",
        "option": "blade_discount",
        "blocks": [
            {"type": "h2", "id": "annex5.discount.title", "text": "1. Blade Discount"},
            {
                "type": "p",
                "id": "annex5.discount.p1",
                "text": "The Customer shall receive the following Guardian discount on eligible Weber blades:",
            },
            {"type": "p", "id": "annex5.discount.amount", "text": "Blade Discount {{Blade_Discount}} %"},
            {
                "type": "p",
                "id": "annex5.discount.p2",
                "text": (
                    "The applicable blades, Customer locations, machines, committed quantities "
                    "and any special pricing shall be listed in the commercial schedule where required."
                ),
            },
            {
                "type": "p",
                "id": "annex5.discount.p3",
                "text": (
                    "Blade discounts are not cumulative with other blade promotions or special "
                    "prices unless expressly agreed."
                ),
            },
            {
                "type": "p",
                "id": "annex5.discount.p4",
                "text": (
                    "Where fixed-term blade pricing is agreed, the applicable term and pricing "
                    "conditions shall be stated in Annex 1."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "stock_agreement",
        "blocks": [
            {"type": "h2", "id": "annex5.stock.title", "text": "2. Stock Agreement"},
            {
                "type": "p",
                "id": "annex5.stock.p1",
                "text": "Weber and the Customer may establish an agreed blade stock concept based on expected consumption.",
            },
            {"type": "p", "id": "annex5.stock.p2", "text": "The stock agreement shall define, where applicable:"},
            {
                "type": "ul",
                "id": "annex5.stock.defines",
                "items": [
                    "blade references;",
                    "agreed stock quantity;",
                    "minimum stock;",
                    "maximum stock;",
                    "expected annual consumption;",
                    "replenishment method;",
                    "stock location;",
                    "ownership of stock;",
                    "delivery conditions; and",
                    "treatment of obsolete or unused stock.",
                ],
            },
            {
                "type": "p",
                "id": "annex5.stock.p3",
                "text": (
                    "The Customer shall provide reasonably accurate consumption information and "
                    "notify Weber of material changes in production or blade demand."
                ),
            },
            {
                "type": "p",
                "id": "annex5.stock.p4",
                "text": (
                    "The stock arrangement is intended to improve availability but does not "
                    "constitute an unconditional guarantee of uninterrupted supply in "
                    "circumstances outside Weber's reasonable control."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "sharpening_assessment",
        "blocks": [
            {"type": "h2", "id": "annex5.sharpening.title", "text": "3. Sharpening Assessment"},
            {
                "type": "p",
                "id": "annex5.sharpening.p1",
                "text": "Weber shall assess the Customer's blade sharpening process and capability as agreed.",
            },
            {"type": "p", "id": "annex5.sharpening.p2", "text": "The assessment may include:"},
            {
                "type": "ul",
                "id": "annex5.sharpening.includes",
                "items": [
                    "sharpening equipment;",
                    "sharpening process;",
                    "blade handling;",
                    "blade condition;",
                    "grinding parameters;",
                    "maintenance practices;",
                    "blade storage;",
                    "process consistency; and",
                    "opportunities for improvement.",
                ],
            },
            {"type": "p", "id": "annex5.sharpening.p3", "text": "Weber may issue recommendations following the assessment."},
            {
                "type": "p",
                "id": "annex5.sharpening.p4",
                "text": (
                    "Unless specifically included, implementation of those recommendations, "
                    "repairs or modifications to sharpening equipment and additional training "
                    "are not included."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "blade_application_review",
        "blocks": [
            {"type": "h2", "id": "annex5.application.title", "text": "4. Blade Application Review"},
            {
                "type": "p",
                "id": "annex5.application.p1",
                "text": (
                    "Where included in the selected Blade Program, Weber may review the "
                    "blade-to-product combination with the objective of supporting the principle "
                    "\"Right Blade, Right Application\"."
                ),
            },
            {
                "type": "p",
                "id": "annex5.application.p2",
                "text": (
                    "Recommendations may consider product type, slicing conditions, machine "
                    "configuration, blade geometry and operational requirements."
                ),
            },
        ],
    },
]
