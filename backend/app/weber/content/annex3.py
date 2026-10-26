"""Annex 3 - Service Support (master pages 15-16).

Responsibility: English source of the service-support annex, gated by the
``service_support`` module in content.SECTIONS. Sections 1 is always included;
subsections are gated by their Guardian option.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "annex3.title", "text": "ANNEX 3 - SERVICE SUPPORT"},
    {
        "type": "p",
        "id": "annex3.tagline",
        "text": "Hotline, remote support and prioritized technical response.",
    },

    # 1. Purpose (always when the module is selected)
    {"type": "h2", "id": "annex3.purpose.title", "text": "1. Purpose"},
    {
        "type": "p",
        "id": "annex3.purpose.p1",
        "text": (
            "The Service Support module provides the Customer with access to Weber technical "
            "support for Equipment covered by this Agreement."
        ),
    },
    {"type": "p", "id": "annex3.purpose.p2", "text": "The exact service level depends on the options selected below."},

    {
        "type": "sub",
        "option": "standard_hotline",
        "blocks": [
            {"type": "h2", "id": "annex3.hotline.title", "text": "2. Standard Hotline"},
            {
                "type": "p",
                "id": "annex3.hotline.p1",
                "text": "The Customer shall have access to the Weber service hotline during the applicable support hours.",
            },
            {"type": "kv", "id": "annex3.hotline.hours", "label": "Support Hours", "token": "Hotline_Service_Hours"},
            {"type": "kv", "id": "annex3.hotline.phone", "label": "Telephone", "token": "Hotline_Number"},
            {"type": "kv", "id": "annex3.hotline.email", "label": "Email", "token": "Service_Email"},
            {"type": "p", "id": "annex3.hotline.p2", "text": "The hotline provides first-level technical support and coordination."},
            {
                "type": "p",
                "id": "annex3.hotline.p3",
                "text": (
                    "Where the issue cannot be resolved through the hotline, Weber may recommend "
                    "Remote Support, an on-site service visit, replacement parts or other technical action."
                ),
            },
            {
                "type": "p",
                "id": "annex3.hotline.p4",
                "text": (
                    "On-site service is not included merely by reason of having Standard Hotline "
                    "support unless expressly stated in Annex 1."
                ),
            },
        ],
    },

    {
        "type": "sub",
        "option": "remote_support",
        "blocks": [
            {"type": "h2", "id": "annex3.remote.title", "text": "3. Remote Support"},
            {
                "type": "p",
                "id": "annex3.remote.p1",
                "text": (
                    "Where technically available and authorized by the Customer, Weber may provide "
                    "remote diagnostic and technical support."
                ),
            },
            {
                "type": "p",
                "id": "annex3.remote.p2",
                "text": (
                    "The Customer shall provide the network connections, VPN access, user "
                    "authorization and other technical conditions reasonably necessary for remote access."
                ),
            },
            {"type": "p", "id": "annex3.remote.p3", "text": "Remote Support may include:"},
            {
                "type": "ul",
                "id": "annex3.remote.includes",
                "items": [
                    "remote fault analysis;",
                    "review of machine status or diagnostic information;",
                    "assistance with parameter or configuration checks;",
                    "support to Customer maintenance personnel; and",
                    "recommendations for further action.",
                ],
            },
            {
                "type": "p",
                "id": "annex3.remote.p4",
                "text": "Remote Support does not guarantee that a fault can be corrected without an on-site intervention.",
            },
        ],
    },

    {
        "type": "sub",
        "option": "priority_response",
        "blocks": [
            {"type": "h2", "id": "annex3.priority.title", "text": "4. Priority Response"},
            {
                "type": "p",
                "id": "annex3.priority.p1",
                "text": (
                    "Requests relating to Equipment covered by this Agreement shall receive "
                    "prioritized handling within Weber's service organization compared with standard "
                    "non-contract requests, subject to technician availability and the applicable "
                    "service level."
                ),
            },
            {
                "type": "kv",
                "id": "annex3.priority.target",
                "label": "Target First Response",
                "token": "Priority_Response_Target",
            },
            {
                "type": "p",
                "id": "annex3.priority.p2",
                "text": (
                    "Priority Response refers to prioritization of the support request. It does not "
                    "constitute a guaranteed repair time, guaranteed machine uptime or guaranteed "
                    "on-site arrival time unless expressly stated otherwise in Annex 1."
                ),
            },
        ],
    },
]
