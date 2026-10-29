"""Annex 7 - Digital Services (Global Appendix 8, gated by options).

Responsibility: English source of the digital-services annex. The module is
gated by ``digital_services``; each clause is gated by its Guardian option.
Only data the system currently holds is printed.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex7.title", "text": "ANNEX 7 - DIGITAL SERVICES"},
    {
        "type": "p",
        "id": "annex7.tagline",
        "text": "Factory Cockpit, performance reviews, MRO reviews and dedicated account management.",
    },
    {
        "type": "p",
        "id": "annex7.intro",
        "text": (
            "The Digital Services module offers selected digital monitoring, performance review "
            "and account management services."
        ),
    },

    {
        "type": "sub",
        # Monitoring is delivered through the same cockpit connection.
        "options": ("factory_cockpit", "monitoring"),
        "blocks": [
            {"type": "h2", "id": "annex7.cockpit.title", "text": "S801 Factory Cockpit / Monitoring"},
            {
                "type": "p",
                "id": "annex7.cockpit.p1",
                "text": (
                    "Where available and selected, Weber provides the agreed connection or access "
                    "to designated Factory Cockpit or supported digital monitoring functionality "
                    "for eligible equipment."
                ),
            },
            {
                "type": "p",
                "id": "annex7.cockpit.p2",
                "text": (
                    "Connection architecture, service availability, retention, access rights and "
                    "cybersecurity responsibilities shall be defined in the digital service terms."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "performance_mro_review",
        "blocks": [
            {"type": "h2", "id": "annex7.performance.title", "text": "S802 Performance Review & Trend Reporting"},
            {
                "type": "p",
                "id": "annex7.performance.p1",
                "text": (
                    "Weber may prepare or review agreed equipment performance information, "
                    "operating trends and identified areas for follow-up based on the data made "
                    "available."
                ),
            },
            {
                "type": "p",
                "id": "annex7.performance.p2",
                "text": (
                    "Values may be affected by data quality, operating practices, product mix and "
                    "third-party systems. Reports are analytical, not production performance "
                    "guarantees."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "performance_mro_review",
        "blocks": [
            {"type": "h2", "id": "annex7.mro.title", "text": "S803 Service / Parts MRO Review"},
            {
                "type": "p",
                "id": "annex7.mro.p1",
                "text": (
                    "Weber may review the agreed service expenditure and spare parts usage against "
                    "a defined MRO reference or agreed planning target."
                ),
            },
            {
                "type": "p",
                "id": "annex7.mro.p2",
                "text": (
                    "Guardian fixed fees, actual maintenance interventions and consumed spare "
                    "parts shall remain separate data elements; no duplicate costs and no "
                    "inference of breakdowns from invoice totals."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "performance_mro_review",
        "blocks": [
            {"type": "h2", "id": "annex7.account.title", "text": "S105 Dedicated Account Service Reviews"},
            {
                "type": "p",
                "id": "annex7.account.p1",
                "text": (
                    "Where selected, an assigned account or After-Sales contact will coordinate "
                    "periodic reviews of agreed service delivery, completed activities, open action "
                    "items and upcoming requirements."
                ),
            },
        ],
    },
]
