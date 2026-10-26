"""Commercial breakdown page (legacy Annex 1: machines, modules, amounts).

Responsibility: the last customer-facing page before the signatures. It shows
the customer box, the offer meta (date, offer number, inspection frequency and
Guardian type), the per-line table (line, module, amount) with its totals, and
the scope/discount notes.

The table is dynamic: one row per offer line. The meta labels, column headings,
totals labels and notes are translated per locale (see content/<locale>.py).
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "breakdown.title", "text": "ANNEX 1, List of machines and modules"},
    {
        "type": "commercial_breakdown",
        "id": "breakdown",
        "customer": [
            "{{Customer_Legal_Name}}",
            "{{Customer_Address}}",
            "{{Customer_Postcode_City}}",
            "{{Customer_Country}}",
        ],
        "meta_right": [
            {"id": "breakdown.date", "label": "Date", "token": "Offer_Date"},
            {"id": "breakdown.offer_no", "label": "Offer No.", "token": "Offer_Number"},
        ],
        "meta_left": [
            {"id": "breakdown.frequency", "label": "Inspection Frequency", "token": "Inspection_Frequency"},
            {"id": "breakdown.type", "label": "Type", "token": "Guardian_Type"},
        ],
        "columns": [
            {"id": "breakdown.col.line", "text": "Line No."},
            {"id": "breakdown.col.module", "text": "Module"},
            {"id": "breakdown.col.amount", "text": "Amount"},
        ],
        "totals": [
            {"id": "breakdown.total", "label": "Total", "token": "Inspection_Amount"},
            {"id": "breakdown.kit", "label": "Basic spare parts kit", "token": "Parts_Kit_Amount"},
            {"id": "breakdown.discount", "label": "Maintenance contract discount", "token": "Guardian_Discount"},
            {"id": "breakdown.grand_total", "label": "Total amount (excl. VAT)", "token": "Total_Contract_Value", "total": True},
        ],
    },
    {
        "type": "p",
        "id": "breakdown.intro",
        "text": (
            "Both parties agree to the following Weber inspection quotation under the "
            "conditions set out below:"
        ),
    },
    {
        "type": "ul",
        "id": "breakdown.notes",
        "items": [
            "includes travel, labour and documentation.",
            "checking of sensors, electrical components, transmissions, toothed belts and "
            "blades (the basic kit includes replacement of the main belts of the head, "
            "spindle and auxiliary modules).",
            "adjustment of the mechanical parts of the different modules.",
            "review and optimisation of programmes.",
            "recording of all scheduled repairs.",
        ],
    },
    {"type": "p", "id": "breakdown.notes_title", "class": "notes-title", "text": "NOTES:"},
    {
        "type": "ul",
        "id": "breakdown.discount_notes",
        "items": [
            "15% discount on technical assistance for the contracted lines.",
            "5% discount on spare parts for the contracted lines (not applicable to "
            "existing discounts).",
            "5% discount on blades for complete boxes of 3 blades (not applicable to "
            "existing discounts).",
            "includes one free follow-up visit after 6 months.",
            "all parts, consumables and spare parts outside the quotation, as well as hours "
            "outside normal working hours, waiting time and repairs outside the quotation, "
            "are invoiced separately.",
        ],
    },
]
