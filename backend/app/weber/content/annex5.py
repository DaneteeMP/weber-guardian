"""Annex 5 - Blade Solutions (Global Appendix 6 content, gated by options).

Responsibility: English source of the blade annex. The module is gated by
``blade_solutions`` in content.SECTIONS; each clause is gated by its Guardian
option. Only data the system currently holds is printed.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex5.title", "text": "ANNEX 5 - BLADE SOLUTIONS"},
    {
        "type": "p",
        "id": "annex5.tagline",
        "text": "Blade application consulting, sharpening and the blade programme.",
    },
    {
        "type": "p",
        "id": "annex5.intro",
        "text": (
            "The Blade Solutions module supports the correct selection, availability, use and "
            "management of Weber blades, including the \u201cright blade, right application\u201d "
            "principle."
        ),
    },

    {
        "type": "sub",
        "option": "blade_discount",
        "blocks": [
            {"type": "h2", "id": "annex5.discount.title", "text": "S603 Blade Supply Partnership"},
            {
                "type": "p",
                "id": "annex5.discount.p1",
                "text": (
                    "If the Customer selects the Blade Partnership option, the parties agree a "
                    "defined catalogue of blade references, quantities, prices, order schedule and "
                    "commercial term in the Blade Programme Schedule."
                ),
            },
            {
                "type": "p",
                "id": "annex5.discount.p2",
                "text": (
                    "Any fixed monthly budget or instalment plan, consumption forecast, minimum "
                    "commitment, price-lock term, rebate, release order, return programme or "
                    "special delivery arrangement applies only if specified in that schedule."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "stock_agreement",
        "blocks": [
            {"type": "h2", "id": "annex5.stock.title", "text": "Blade Stock Agreement"},
            {
                "type": "p",
                "id": "annex5.stock.p1",
                "text": (
                    "Where a blade stock agreement is selected, the parties define the references, "
                    "quantities, replenishment method, stock location and ownership in the signed "
                    "schedule."
                ),
            },
            {
                "type": "p",
                "id": "annex5.stock.p2",
                "text": (
                    "Purchased or delivered quantities must be accounted for distinctly from "
                    "estimated usage or internal blade stock."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "sharpening_assessment",
        "blocks": [
            {"type": "h2", "id": "annex5.sharpening.title", "text": "S602 Sharpening Assessment"},
            {
                "type": "p",
                "id": "annex5.sharpening.p1",
                "text": (
                    "Weber evaluates the Customer's current sharpening approach, processes, "
                    "machine parameters and potential quality-control or handling improvements "
                    "within the agreed scope."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "blade_application_review",
        "blocks": [
            {"type": "h2", "id": "annex5.application.title", "text": "S601 Knife Application Consulting"},
            {
                "type": "p",
                "id": "annex5.application.p1",
                "text": (
                    "Weber reviews the selected slicing application, product characteristics, "
                    "cutting configuration and relevant knife geometry or specification with the "
                    "Customer."
                ),
            },
            {
                "type": "p",
                "id": "annex5.application.p2",
                "text": (
                    "Deliverable: a documented set of technical recommendations for a suitable "
                    "knife/application combination, subject to verification in the real "
                    "application."
                ),
            },
        ],
    },
]
