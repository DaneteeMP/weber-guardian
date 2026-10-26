"""Signature page of the customer contract (last section).

Responsibility: the closing signature block. It is always printed last so the
customer signs after every annex and the commercial breakdown. The node ids
keep the ``summary.signatures.*`` prefix they have always had.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "summary.signatures.title", "text": "SIGNATURES"},
    {
        "type": "p",
        "id": "summary.signatures.intro",
        "text": (
            "By signing this Agreement, the Parties confirm their acceptance of the Master "
            "Agreement and all Annexes identified in Annex 1 as applicable."
        ),
    },
    {
        "type": "signatures",
        "id": "summary.signatures",
        "company_label": {"id": "summary.signatures.company", "label": "Company"},
        "columns": [
            {
                "id": "summary.signatures.customer",
                "heading": "For the Customer",
                "company_token": "Customer_Legal_Name",
            },
            {
                "id": "summary.signatures.weber",
                "heading": "For Weber",
                "company_token": "Weber_Legal_Entity",
            },
        ],
        "fields": [
            {"id": "summary.signatures.name", "label": "Name"},
            {"id": "summary.signatures.position", "label": "Position"},
            {"id": "summary.signatures.place", "label": "Place"},
            {"id": "summary.signatures.date", "label": "Date"},
            {"id": "summary.signatures.signature", "label": "Signature"},
        ],
    },
]
