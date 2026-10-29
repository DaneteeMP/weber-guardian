"""Master Agreement (legacy maintenance contract: 0 + I-IX).

Replaces the previous 19-clause Guardian master with the legacy Weber
maintenance contract text (the one rendered in the Spanish offer). The English
text below is the source; content/<locale>.py overrides it.

The legacy numbers (phone, service hours, 12-month term, 15%/5% discounts and
the Spanish governing law) are kept verbatim for now; they will be tokenized
when the contract-data entry lands.
"""

from __future__ import annotations

BLOCKS = [
    # 0. Definitions
    {"type": "h2", "id": "master.clause0.title", "text": "0. DEFINITIONS", "page_break": True},
    {
        "type": "p",
        "id": "master.clause0.intro",
        "text": "The terms used in this agreement have the following meanings:",
    },
    {"type": "p", "id": "master.clause0.machine.term", "class": "clause-subheading", "text": "Machine / Modules"},
    {
        "type": "p",
        "id": "master.clause0.machine.definition",
        "text": (
            "A functional unit, item of equipment or system to which the services "
            "provided under this contract relate."
        ),
    },
    {"type": "p", "id": "master.clause0.inspection.term", "class": "clause-subheading", "text": "Inspection"},
    {
        "type": "p",
        "id": "master.clause0.inspection.definition",
        "text": (
            "The determination and assessment of the actual condition of a machine / "
            "module, including the determination of the causes of wear and the resulting "
            "consequences for future use."
        ),
    },
    {"type": "p", "id": "master.clause0.maintenance.term", "class": "clause-subheading", "text": "Maintenance"},
    {
        "type": "p",
        "id": "master.clause0.maintenance.definition",
        "text": (
            'Measures intended to delay the deterioration of existing wear items '
            '("preventive maintenance"), in particular by adjustments or by replacing '
            "filters, seals and lubricants, technical cleaning, etc."
        ),
    },
    {"type": "p", "id": "master.clause0.replacement.term", "class": "clause-subheading", "text": "Replacement"},
    {
        "type": "p",
        "id": "master.clause0.replacement.definition",
        "text": (
            "Any measure to return a machine / module to the agreed condition, in "
            "particular by replacing parts, including wear parts. Measures to maintain "
            "the agreed condition outside the maintenance services are also part of the "
            "repair."
        ),
    },

    # I. Purpose of the contract
    {"type": "h2", "id": "master.clause1.title", "text": "I. PURPOSE OF THE CONTRACT"},
    {
        "type": "p",
        "id": "master.clause1.p1",
        "text": (
            "(0) The purpose of the inspection contract is the inspection of the machines "
            "and modules listed in Annex 1, with these services invoiced on the basis of a "
            "fixed fee (Annex 1). Maintenance of the machines and components shall be "
            "charged as incurred and according to the rates in force."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p2",
        "text": (
            "The purpose of the Contract is to extend the useful life of the machines and "
            "modules, reduce downtime and keep maintenance costs under control through "
            "adequate inspection and maintenance."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p3",
        "text": (
            "(1) Under this Contract, the Executor assumes the following services for the "
            "machines and modules listed:"
        ),
    },
    {
        "type": "ul",
        "id": "master.clause1.services",
        "items": [
            "Hotline service",
            "Supply of spare parts",
            "Maintenance",
            "Courtesy visit after maintenance",
            "Blade Programme (stock holding)",
        ],
    },
    {
        "type": "p",
        "id": "master.clause1.p4",
        "text": "(2) The Executor's service comprises, in the following cases:",
    },
    {
        "type": "p",
        "id": "master.clause1.p5",
        "text": "(2.1) Where the hotline or telephone service centre is contacted:",
    },
    {
        "type": "ul",
        "id": "master.clause1.hotline",
        "items": [
            "Hotline service from Monday to Friday, 07:30 to 17:30.",
            "Telephone: 938 23 32 33",
        ],
    },
    {
        "type": "p",
        "id": "master.clause1.p6",
        "text": (
            "(2.2) Distribution of spare parts: supply of spare parts available in stock "
            "(in the Iberian Peninsula and Germany) within 24-48 hours. If the requested "
            "spare part is not in stock, it will be ordered and delivered as soon as "
            "possible."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p7",
        "text": "(2.3) Inspection: inspection of the machines in accordance with Annex 1.",
    },
    {
        "type": "p",
        "id": "master.clause1.p8",
        "text": "(2.4) Maintenance: performance of repairs in accordance with point I.3 of the Contract.",
    },
    {
        "type": "p",
        "id": "master.clause1.p9",
        "text": (
            "(2.5) Blade stock-holding programme: 5% discount from the first box of 3 "
            "units, in accordance with Annex 2."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p10",
        "text": (
            "(3) Any maintenance work or other services (for example, changes to machines "
            "and systems) resulting from the inspection shall require a separate purchase "
            "order and will be invoiced against an additional quotation."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p11",
        "text": (
            "(4) The number of machines included in Annex 1, as well as the scope of the "
            "services arising from this Contract, shall be verified by the contracting "
            "parties in the last quarter of the Contract."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p12",
        "text": (
            "(5) Changes to the number of machines included in the agreement and changes "
            "to the scope of the service by the Client shall be recorded in writing, "
            "amending Annex 1. This service agreement is valid for the 12 months of the "
            "Contract's term or until the Contract ends."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p13",
        "text": (
            "(6) Courtesy visit to be carried out if the subsequent maintenance is "
            "performed by the Executor."
        ),
    },

    # II. Price and payment
    {"type": "h2", "id": "master.clause2.title", "text": "II. PRICE AND PAYMENT"},
    {
        "type": "p",
        "id": "master.clause2.p1",
        "text": (
            "(1) The price of the inspection work is calculated in accordance with Annex 1. "
            "The relationship is derived from the machine model and the modules selected "
            "under point I of the Contract."
        ),
    },
    {
        "type": "p",
        "id": "master.clause2.p2",
        "text": (
            '(2) The price for the "Inspection" and "Maintenance" modules includes travel, '
            "transport, accommodation and subsistence expenses. Except for exceptions "
            "agreed with the Client."
        ),
    },
    {
        "type": "p",
        "id": "master.clause2.p3",
        "text": "(3) Replaced parts shall be presented to the Client for their control.",
    },
    {
        "type": "p",
        "id": "master.clause2.p4",
        "text": (
            "(4) The price of the inspection personnel's work shall be paid within 30 days "
            "of the invoice being issued. Invoicing takes place after the inspection has "
            "been performed."
        ),
    },
    {
        "type": "p",
        "id": "master.clause2.p5",
        "text": (
            "(5) The Executor is entitled to review the price of the work in accordance "
            "with Annex 1 annually. It shall notify the Client of such review at least 3 "
            "months before it takes effect. The price change shall apply in the following "
            "payment period."
        ),
    },
    {
        "type": "p",
        "id": "master.clause2.p6",
        "text": (
            "(6) Retention of payments or set-off for any alleged counterclaims by the "
            "Client is not accepted."
        ),
    },
    {
        "type": "p",
        "id": "master.clause2.p7",
        "text": (
            "(7) The Executor offers a 15% discount for machine assistance services and a "
            "maximum 5% discount on spare parts, non-cumulative, as indicated in Annex 1."
        ),
    },

    # III. Client participation and technical contribution
    {"type": "h2", "id": "master.clause3.title", "text": "III. CLIENT PARTICIPATION AND TECHNICAL CONTRIBUTION"},
    {"type": "p", "id": "master.clause3.p1", "text": "(1) The Client shall ensure that:"},
    {
        "type": "ul",
        "id": "master.clause3.obligations",
        "items": [
            "The work can be carried out punctually at the agreed times and on the agreed "
            "machines, and shall guarantee free access to the machines and modules.",
            "The machine is in operating condition, available and clean (without product "
            "residue).",
            "Once the work is completed, a functional check can be carried out with the "
            "customer's original products in sufficient quantity.",
            "Faults in progress are recorded on the machine drawings.",
            "Production is organised so that it can be stopped during the inspection.",
        ],
    },
    {
        "type": "p",
        "id": "master.clause3.p2",
        "text": (
            "(2.a) The Client shall bear the costs incurred by the inspection personnel "
            "during the inspection and maintenance."
        ),
    },
    {
        "type": "p",
        "id": "master.clause3.p3",
        "text": (
            "The Client shall take the special measures necessary for personal and material "
            "protection at the inspection/maintenance site. It shall also inform the "
            "executing company's personnel of the special safety measures, insofar as these "
            "are relevant to the inspection and maintenance personnel. The Client shall "
            "notify the executor of any breaches committed by personnel that violate these "
            "safety regulations."
        ),
    },
    {
        "type": "p",
        "id": "master.clause3.p4",
        "text": (
            "(b) The Client undertakes to bear the costs of the technical contribution, in "
            "particular to provide assistance, workshop, auxiliary means such as water and "
            "electricity free of charge, including the necessary connections."
        ),
    },
    {
        "type": "p",
        "id": "master.clause3.p5",
        "text": (
            "(c) In order to decide whether the work can be carried out and/or the parts "
            "indicated in point I.3 can be replaced during the inspection interval, the "
            "Client shall designate a person with decision-making authority."
        ),
    },

    # IV. Compliance with contract deadlines
    {"type": "h2", "id": "master.clause4.title", "text": "IV. COMPLIANCE WITH CONTRACT DEADLINES"},
    {
        "type": "p",
        "id": "master.clause4.p1",
        "text": (
            "(1) The Executor undertakes to carry out an inspection within the time "
            "interval agreed in Annex 1."
        ),
    },
    {
        "type": "p",
        "id": "master.clause4.p2",
        "text": (
            "(2) The Executor shall notify the Client of the exact inspection date at least "
            "6 weeks in advance, unless a specific date has been agreed between the "
            "contracting parties."
        ),
    },
    {
        "type": "p",
        "id": "master.clause4.p3",
        "text": "(3) The Executor shall provide the services during the following periods:",
    },
    {
        "type": "ul",
        "id": "master.clause4.service_periods",
        "items": [
            "Inspection and maintenance from Monday to Friday, 08:00 to 18:00.",
            "Except by mutual agreement.",
        ],
    },
    {
        "type": "p",
        "id": "master.clause4.p4",
        "text": (
            "(4) If the Client or the Executor is unable to carry out the work on the "
            "scheduled date, both parties shall notify each other at least 2 working days in "
            "advance. If the Executor does not attend on the agreed date, the Executor shall "
            "not invoice the travel costs for the next date; if the line is not available on "
            "the date agreed by the Client, the Client shall pay the Executor the travel "
            "costs incurred."
        ),
    },
    {
        "type": "p",
        "id": "master.clause4.p5",
        "text": (
            "(5) If the inspection/maintenance is delayed due to circumstances arising from "
            "labour disputes, in particular strikes and stoppages, or events not "
            "attributable to the Executor, the inspection/maintenance shall be appropriately "
            "extended, provided it can be proven that such impediments have a significant "
            "impact on completing the inspection/maintenance. This shall also apply where "
            "such circumstances occur after the Executor has failed to meet the notice "
            "period set out in the previous paragraph."
        ),
    },

    # V. Commencement and term
    {"type": "h2", "id": "master.clause5.title", "text": "V. COMMENCEMENT AND TERM OF THE CONTRACT"},
    {
        "type": "p",
        "id": "master.clause5.p1",
        "text": (
            "(1) The Contract is valid from the signature of both parties. The term of the "
            "Contract is 12 months and it may be terminated by either party."
        ),
    },
    {
        "type": "p",
        "id": "master.clause5.p2",
        "text": (
            "(2) The Contract shall be automatically renewed for a further 12 months unless "
            "terminated in writing 3 months before its end."
        ),
    },

    # VI. Warranty and liability
    {"type": "h2", "id": "master.clause6.title", "text": "VI. WARRANTY AND LIABILITY"},
    {
        "type": "p",
        "id": "master.clause6.p1",
        "text": (
            "(1) If the inspection/maintenance has not been fully completed, the Executor "
            "shall review or rectify it at no cost."
        ),
    },
    {
        "type": "p",
        "id": "master.clause6.p2",
        "text": (
            "(2) The Executor shall remedy free of charge all damage caused by itself or its "
            "agents to the machines and installations that were to be maintained. The amount "
            "of the repair obligation is limited to the annual fee stipulated in the "
            "contract."
        ),
    },
    {
        "type": "p",
        "id": "master.clause6.p3",
        "text": (
            "(3) If the Executor fails to comply with its duty of repair, remedy or damage "
            "repair, the Client may set an appropriate extension. If, through the Executor's "
            "fault, this period elapses without result, the Client may, at its choice, demand "
            "a reduction in the maintenance and inspection fees or terminate the Contract "
            "immediately. Both the Executor and the Client expressly agree that the Executor "
            "shall be liable for damages only where intent or gross negligence on its part "
            "or on the part of its agents can be proven. In particular, the parties expressly "
            "exclude liability for indirect damages or losses."
        ),
    },
    {
        "type": "p",
        "id": "master.clause6.p4",
        "text": (
            "(4) Any other right of claim by the Client shall apply only in the case of "
            "intent or gross negligence. In addition, the Client may not assert any other "
            "right of set-off against the Executor, in particular no right to compensation "
            "for damages or other rights for any inconvenience related to the inspection "
            "Contract, regardless of the reasons."
        ),
    },
    {
        "type": "p",
        "id": "master.clause6.p5",
        "text": "(5) The Executor shall not be liable for any damage or defect caused by non-original parts.",
    },

    # VII. Limitation period
    {"type": "h2", "id": "master.clause7.title", "text": "VII. LIMITATION PERIOD"},
    {
        "type": "p",
        "id": "master.clause7.p1",
        "text": (
            "The Client's warranty rights shall expire twelve months after acceptance of the "
            "corresponding inspection/maintenance service. The warranty period shall be "
            "extended for the duration of the remedial work."
        ),
    },

    # VIII. Other provisions
    {"type": "h2", "id": "master.clause8.title", "text": "VIII. OTHER PROVISIONS"},
    {
        "type": "p",
        "id": "master.clause8.p1",
        "text": (
            "(1) Inspection/maintenance personnel shall be granted access to the machines and "
            "installations during normal working hours/service time so that they may carry "
            "out the announced inspection and maintenance work. The Client shall provide all "
            "necessary information about the machines and modules indicated in Annex 1 and "
            "provide the corresponding documentation."
        ),
    },
    {
        "type": "p",
        "id": "master.clause8.p2",
        "text": (
            "(2) If the Client transfers machines and installations to third parties, it "
            "shall remain liable for payment of the fees unless the third party accedes to "
            "the contract with the Executor's prior authorisation. The Executor may only "
            "refuse consent for justified reasons."
        ),
    },
    {
        "type": "p",
        "id": "master.clause8.p3",
        "text": "(3) The Executor is entitled to transfer to third parties the rights and duties assumed under this contract.",
    },
    {
        "type": "p",
        "id": "master.clause8.p4",
        "text": "(4) Additional agreements and amendments to the contract must be made in writing.",
    },
    {
        "type": "p",
        "id": "master.clause8.p5",
        "text": (
            "(5) If any provision of this contract becomes invalid, all other provisions or "
            "agreements shall remain valid."
        ),
    },

    # IX. Place of jurisdiction
    {"type": "h2", "id": "master.clause9.title", "text": "IX. PLACE OF JURISDICTION"},
    {
        "type": "p",
        "id": "master.clause9.p1",
        "text": (
            "To the extent permitted by law, the place of performance and jurisdiction shall "
            "be the Executor's registered office. The law of Spain shall apply exclusively."
        ),
    },
]
