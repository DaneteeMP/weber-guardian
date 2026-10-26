"""Annex 7 - Digital Services (master pages 24-25).

Responsibility: English source of the digital-services annex, gated by the
``digital_services`` module in content.SECTIONS. The module introduction has
no numbered heading in the master template; every numbered subsection is
gated by its Guardian option.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex7.title", "text": "ANNEX 7 - DIGITAL SERVICES"},
    {
        "type": "p",
        "id": "annex7.tagline",
        "text": "Factory Cockpit, performance review, MRO review and dedicated account ownership.",
    },
    {
        "type": "p",
        "id": "annex7.intro",
        "text": (
            "The Digital Services module provides selected digital monitoring, performance-review "
            "and account-management services."
        ),
    },

    {
        "type": "sub",
        "option": "factory_cockpit",
        "blocks": [
            {"type": "h2", "id": "annex7.cockpit.title", "text": "1. Factory Cockpit"},
            {
                "type": "p",
                "id": "annex7.cockpit.p1",
                "text": (
                    "Where the selected Equipment is technically compatible, Weber shall support "
                    "connection of the agreed Equipment to Factory Cockpit in accordance with the "
                    "applicable digital service conditions."
                ),
            },
            {
                "type": "kv",
                "id": "annex7.cockpit.lines",
                "label": "Connected Line(s)",
                "token": "Factory_Cockpit_Lines",
            },
            {
                "type": "p",
                "id": "annex7.cockpit.p2",
                "text": (
                    "Factory Cockpit may be used to collect and visualize available machine "
                    "performance data for the purpose of performance review and optimization."
                ),
            },
            {
                "type": "p",
                "id": "annex7.cockpit.p3",
                "text": (
                    "The Customer shall provide the network infrastructure, permissions and "
                    "technical access reasonably required for the connection."
                ),
            },
            {
                "type": "p",
                "id": "annex7.cockpit.p4",
                "text": (
                    "Availability of specific data depends on the machine generation, installed "
                    "software and connectivity of the relevant Equipment."
                ),
            },
            {
                "type": "p",
                "id": "annex7.cockpit.p5",
                "text": (
                    "Any separate software licence or digital-service terms applicable to Factory "
                    "Cockpit shall remain applicable."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "performance_review",
        "blocks": [
            {"type": "h2", "id": "annex7.performance.title", "text": "2. Performance Review"},
            {
                "type": "p",
                "id": "annex7.performance.p1",
                "text": "Weber and the Customer shall conduct periodic reviews of available Equipment performance data.",
            },
            {
                "type": "kv",
                "id": "annex7.performance.frequency",
                "label": "Review Frequency",
                "token": "Performance_Review_Frequency",
            },
            {"type": "p", "id": "annex7.performance.p2", "text": "The review may include:"},
            {
                "type": "ul",
                "id": "annex7.performance.includes",
                "items": [
                    "selected machine KPIs;",
                    "performance trends;",
                    "recurring technical observations;",
                    "identified improvement opportunities;",
                    "completed activities;",
                    "pending actions; and",
                    "priorities for the next review period.",
                ],
            },
            {
                "type": "p",
                "id": "annex7.performance.p3",
                "text": "The Parties may agree specific Customer KPIs and target values.",
            },
            {
                "type": "p",
                "id": "annex7.performance.p4",
                "text": (
                    "Unless expressly agreed otherwise, such target values are management "
                    "objectives and not contractual performance guarantees."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "mro_review",
        "blocks": [
            {"type": "h2", "id": "annex7.mro.title", "text": "3. MRO Review"},
            {
                "type": "p",
                "id": "annex7.mro.p1",
                "text": (
                    "Weber shall periodically review relevant Maintenance, Repair and Operations "
                    "expenditure information available for the covered Equipment."
                ),
            },
            {"type": "p", "id": "annex7.mro.p2", "text": "The review may include:"},
            {
                "type": "ul",
                "id": "annex7.mro.includes",
                "items": [
                    "spare-parts expenditure;",
                    "service expenditure;",
                    "blade expenditure where relevant;",
                    "historical maintenance activity;",
                    "installed-base information;",
                    "maintenance trends;",
                    "identified cost drivers; and",
                    "comparison against an agreed MRO planning target.",
                ],
            },
            {
                "type": "kv",
                "id": "annex7.mro.frequency",
                "label": "MRO Review Frequency",
                "token": "MRO_Review_Frequency",
            },
            {
                "type": "kv",
                "id": "annex7.mro.target",
                "label": "Agreed MRO Target, if applicable",
                "token": "MRO_Target",
            },
            {
                "type": "p",
                "id": "annex7.mro.p3",
                "text": (
                    "The purpose of the review is to support maintenance planning and identify "
                    "improvement opportunities. It does not constitute a guarantee that a "
                    "particular MRO expenditure level will be achieved."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "dedicated_account_team",
        "blocks": [
            {"type": "h2", "id": "annex7.account.title", "text": "4. Dedicated Account Team"},
            {
                "type": "p",
                "id": "annex7.account.p1",
                "text": "Weber shall assign a Guardian account ownership structure for the Customer.",
            },
            {
                "type": "p",
                "id": "annex7.account.p2",
                "text": (
                    "The team shall coordinate selected Guardian activities and act as a central "
                    "point for periodic program review."
                ),
            },
            {"type": "p", "id": "annex7.account.p3", "text": "The account-management process may include:"},
            {
                "type": "ul",
                "id": "annex7.account.includes",
                "items": [
                    "scheduled Customer reviews;",
                    "coordination between relevant Weber functions;",
                    "review of open actions;",
                    "review of upcoming service activities;",
                    "review of parts and blade requirements;",
                    "performance discussions;",
                    "optimization opportunities; and",
                    "follow-up of agreed actions.",
                ],
            },
            {"type": "kv", "id": "annex7.account.cadence", "label": "Review Cadence", "token": "Account_Review_Frequency"},
            {
                "type": "p",
                "id": "annex7.account.p4",
                "text": (
                    "The dedicated account team supplements, but does not replace, the normal "
                    "Weber operational channels for urgent service requests, spare-parts orders "
                    "or emergency support."
                ),
            },
        ],
    },
]
