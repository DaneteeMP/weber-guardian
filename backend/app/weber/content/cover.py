"""Cover section of the customer contract.

Responsibility: the customer-facing cover. The Guardian wordmark is rendered
by the template (page running element); these blocks add the contract title,
the two party blocks (Weber as Executor and the customer as Client) with their
legal addresses, and the closing preamble.

The legacy cover wording ("Between the company:", "(hereinafter, the
Executor)", ...) is translated per locale through the node ids
``cover.executor.label`` / ``cover.executor.alias`` / ``cover.customer.label``
/ ``cover.customer.alias`` and ``cover.preamble``. Party names and addresses
are resolved from the offer tokens (Weber_Legal_Entity, Customer_Legal_Name,
...); empty address lines are dropped by the renderer.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "cover.title", "text": "MAINTENANCE CONTRACT"},
    {
        "type": "party",
        "id": "cover.executor",
        "label": "Between the company:",
        "name_token": "Weber_Legal_Entity",
        "address_tokens": ["Weber_Address", "Weber_Postcode_City", "Weber_Country"],
        "alias": "(hereinafter, the Executor)",
    },
    {
        "type": "party",
        "id": "cover.customer",
        "label": "And the company:",
        "name_token": "Customer_Legal_Name",
        "address_tokens": ["Customer_Address", "Customer_Postcode_City", "Customer_Country"],
        "alias": "(hereinafter, the Client)",
    },
    {
        "type": "p",
        "id": "cover.preamble",
        "text": (
            'the following inspection and maintenance contract is concluded '
            '(hereinafter, the "Contract"):'
        ),
    },
]
