"""Annex 3 - Service Support (Global Appendix 1 content, gated by options).

Responsibility: English source of the service-support annex. The module is
gated by ``service_support`` in content.SECTIONS; each service clause is gated
by its Guardian option. Paragraphs that depend on data the system does not
hold yet are not written here: the renderer also drops any paragraph whose
{{Token}} has no value.

The service-rate tables (time bands + with/without contract) print only when
the subsidiary has configured its band rates.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex3.title", "text": "ANNEX 3 - SERVICE SUPPORT"},
    {
        "type": "p",
        "id": "annex3.tagline",
        "text": "Customer service and technical support.",
    },

    # 1. Purpose (always when the module is selected)
    {"type": "h2", "id": "annex3.purpose.title", "text": "1. Purpose"},
    {
        "type": "p",
        "id": "annex3.purpose.p1",
        "text": (
            "The Service Support module provides the Customer with access to Weber "
            "technical support for Equipment covered by this Agreement."
        ),
    },
    {
        "type": "p",
        "id": "annex3.purpose.p2",
        "text": "The exact service level depends on the options selected below.",
    },

    # Service rates (subsidiary configuration; omitted when not configured)
    {"type": "h2", "id": "annex3.rates.title", "text": "2. Service Rates", "requires_band_rates": True},
    {
        "type": "band_rates",
        "id": "annex3.rates",
        "matrix_headers": [
            {"id": "annex3.rates.hours", "text": "Hours"},
            {"id": "annex3.rates.weekdays", "text": "Monday - Friday"},
            {"id": "annex3.rates.saturday", "text": "Saturday"},
            {"id": "annex3.rates.sunday", "text": "Sunday / holiday"},
        ],
        "matrix_rows": [
            ["06:00 - 18:00", "I", "II", "III"],
            ["18:00 - 06:00", "II", "III", "III"],
        ],
        "rate_headers": [
            {"id": "annex3.rates.band", "text": "Band"},
            {"id": "annex3.rates.without", "text": "Without contract"},
            {"id": "annex3.rates.with", "text": "With contract"},
        ],
    },

    {
        "type": "sub",
        "option": "standard_hotline",
        "blocks": [
            {"type": "h2", "id": "annex3.hotline.title", "text": "S101 Standard Hotline"},
            {
                "type": "p",
                "id": "annex3.hotline.p1",
                "text": (
                    "Weber shall provide access to the selected standard technical service "
                    "contact channel during the agreed availability window. This is a "
                    "communication service; no onsite response time is implied."
                ),
            },
            {"type": "kv", "id": "annex3.hotline.phone", "label": "Contact point", "token": "Hotline_Number"},
            {"type": "kv", "id": "annex3.hotline.email", "label": "Email", "token": "Service_Email"},
            {"type": "kv", "id": "annex3.hotline.hours", "label": "Monday - Friday", "token": "Hotline_Service_Hours"},
            {
                "type": "p",
                "id": "annex3.hotline.p2",
                "text": (
                    "Availability for call acceptance is not, by itself, a guaranteed "
                    "diagnostic resolution, onsite attendance or spare-part dispatch."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "remote_support",
        "blocks": [
            {"type": "h2", "id": "annex3.remote.title", "text": "S103 Remote Technical Support"},
            {
                "type": "p",
                "id": "annex3.remote.p1",
                "text": (
                    "Weber may provide initial fault analysis by telephone, email, supported "
                    "remote connection or video communication, subject to agreement on secure "
                    "access and customer assistance."
                ),
            },
            {
                "type": "p",
                "id": "annex3.remote.p2",
                "text": (
                    "Connection, network and cybersecurity arrangements must be agreed before "
                    "activation. Remote support does not replace a required onsite service."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "priority_response",
        "blocks": [
            {"type": "h2", "id": "annex3.priority.title", "text": "S104 On-site Service & Priority Response"},
            {
                "type": "p",
                "id": "annex3.priority.p1",
                "text": (
                    "Onsite technical assistance is available in the agreed territory subject "
                    "to technician availability and applicable dispatch and booking conditions. "
                    "Any priority ranking must be expressly agreed."
                ),
            },
            {
                "type": "p",
                "id": "annex3.priority.p2",
                "text": (
                    "Service callout charges, labour, travel, waiting time, overtime, "
                    "accommodation and materials are calculated under the approved rate schedule."
                ),
            },
        ],
    },
]
