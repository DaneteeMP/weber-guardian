"""Master Agreement section of the customer contract (master pages 3-9).

Responsibility: verbatim English source of the stable Master Agreement
(header, parties and clauses 1-19). Template chrome (page headers, footers)
and internal generation rules are excluded; {{Token}} placeholders are kept
verbatim and resolved by the renderer.
"""

from __future__ import annotations

BLOCKS = [
    {"type": "h1", "id": "master.title", "text": "WEBER GUARDIAN MASTER AGREEMENT"},
    {"type": "kv", "id": "master.kv.agreement_no", "label": "Agreement No.", "token": "Agreement_Number"},
    {"type": "kv", "id": "master.kv.offer_no", "label": "Offer No.", "token": "Offer_Number"},
    {"type": "kv", "id": "master.kv.offer_date", "label": "Offer Date", "token": "Offer_Date"},
    {"type": "kv", "id": "master.kv.start_date", "label": "Contract Start Date", "token": "Contract_Start_Date"},
    {"type": "kv", "id": "master.kv.term", "label": "Initial Contract Term", "token": "Contract_Duration"},
    {"type": "kv", "id": "master.kv.billing", "label": "Billing Frequency", "token": "Billing_Frequency"},
    {"type": "h2", "id": "master.between", "text": "BETWEEN"},
    {
        "type": "lines",
        "id": "master.weber_party",
        "items": [
            "{{Weber_Legal_Entity}}",
            "{{Weber_Address}}",
            "{{Weber_Postcode_City}}",
            "{{Weber_Country}}",
        ],
    },
    {"type": "p", "id": "master.weber_definition", "text": "hereinafter referred to as \"Weber\"."},
    {
        "type": "lines",
        "id": "master.customer_party",
        "items": [
            "{{Customer_Legal_Name}}",
            "{{Customer_Address}}",
            "{{Customer_Postcode_City}}",
            "{{Customer_Country}}",
        ],
    },
    {"type": "p", "id": "master.customer_definition", "text": "hereinafter referred to as the \"Customer\"."},
    {
        "type": "p",
        "id": "master.parties",
        "text": "Weber and the Customer are individually referred to as a \"Party\" and collectively as the \"Parties\".",
    },

    # 1. PURPOSE OF THE AGREEMENT
    {"type": "h2", "id": "master.clause1.title", "text": "1. PURPOSE OF THE AGREEMENT"},
    {
        "type": "p",
        "id": "master.clause1.p1",
        "text": (
            "The purpose of this Guardian Agreement is to support the reliable, efficient and "
            "economically sustainable operation of the Customer's Weber equipment throughout its lifecycle."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p2",
        "text": (
            "Guardian is a modular after-sales program. Depending on the modules selected by the "
            "Customer, the Agreement may include inspection and preventive maintenance services, "
            "technical support, spare-parts services, blade solutions, training and optimization "
            "services and digital services."
        ),
    },
    {
        "type": "p",
        "id": "master.clause1.p3",
        "text": "Only the services expressly identified in the applicable Annexes to this Agreement are included.",
    },
    {"type": "p", "id": "master.clause1.goals_intro", "text": "The objective of the Guardian program is to:"},
    {
        "type": "ul",
        "id": "master.clause1.goals",
        "items": [
            "improve equipment reliability and availability;",
            "support preventive maintenance and early identification of technical issues;",
            "reduce avoidable unplanned downtime;",
            "support predictable maintenance planning and expenditure;",
            "ensure access to Weber technical expertise;",
            "optimize spare-parts and blade management;",
            "improve operating and maintenance practices; and",
            "support the continuous optimization of the Customer's installed equipment.",
        ],
    },
    {
        "type": "p",
        "id": "master.clause1.exclusion",
        "text": (
            "No service, discount, response commitment or other benefit shall be deemed included "
            "unless it is expressly stated in this Agreement or in an Annex forming part of it."
        ),
    },

    # 2. CONTRACT DOCUMENTS AND MODULAR STRUCTURE
    {"type": "h2", "id": "master.clause2.title", "text": "2. CONTRACT DOCUMENTS AND MODULAR STRUCTURE"},
    {
        "type": "p",
        "id": "master.clause2.p1",
        "text": (
            "This Agreement consists of this Master Agreement and the Annexes listed below which "
            "have been selected for the Customer."
        ),
    },
    {
        "type": "ul",
        "id": "master.clause2.annexes",
        "items": [
            "Annex 1 - Equipment & Commercial Schedule: Always applicable.",
            "Annex 2 - Maintenance & Inspection: Applicable only when the Maintenance & Inspection module is selected.",
            "Annex 3 - Service Support: Applicable only when the Service Support module is selected.",
            "Annex 4 - Parts & Availability: Applicable only when the Parts & Availability module is selected.",
            "Annex 5 - Blade Solutions: Applicable only when the Blade Solutions module is selected.",
            "Annex 6 - Training & Optimization: Applicable only when the Training & Optimization module is selected.",
            "Annex 7 - Digital Services: Applicable only when the Digital Services module is selected.",
        ],
    },
    {"type": "p", "id": "master.clause2.p2", "text": "The applicable Annexes form an integral part of this Agreement."},
    {
        "type": "p",
        "id": "master.clause2.p3",
        "text": (
            "The services apply only to the machines, production lines, modules and locations "
            "identified in Annex 1 unless otherwise agreed in writing."
        ),
    },
    {
        "type": "p",
        "id": "master.clause2.p4",
        "text": (
            "If there is a conflict between the documents forming this Agreement, the following "
            "order of precedence shall apply:"
        ),
    },
    {
        "type": "ol",
        "id": "master.clause2.precedence",
        "items": [
            "Annex 1 - Equipment & Commercial Schedule;",
            "the applicable service-specific Annex;",
            "this Master Agreement; and",
            "Weber's applicable General Terms and Conditions.",
        ],
    },
    {
        "type": "p",
        "id": "master.clause2.p5",
        "text": (
            "Customer-specific deviations expressly stated in Annex 1 shall prevail over standard "
            "provisions relating to the same subject."
        ),
    },

    # 3. DEFINITIONS
    {"type": "h2", "id": "master.clause3.title", "text": "3. DEFINITIONS"},
    {
        "type": "dl",
        "id": "master.clause3.definitions",
        "items": [
            "Equipment: the machines, modules, systems or other equipment expressly listed in Annex 1.",
            "Inspection: the assessment of the actual condition of Equipment for the purpose of identifying wear, irregularities, required maintenance and potential actions necessary to support its future operation.",
            "Preventive Maintenance: scheduled measures intended to reduce deterioration and the risk of failure, including adjustment, lubrication, cleaning, replacement of defined wear parts and other activities expressly included in the applicable service scope.",
            "Corrective Maintenance / Repair: work intended to restore Equipment to the required operating condition following a fault, failure or identified defect.",
            "Wear Parts: components which, by their intended function and depending on operating conditions and usage, are expected to require periodic replacement.",
            "Spare Parts: replacement components supplied for the Equipment.",
            "Services: the Guardian services expressly selected and described in the applicable Annexes.",
            "Service Visit: an agreed physical visit by Weber personnel or an authorized Weber service partner to the Customer's site.",
            "Remote Support: technical assistance provided without a physical visit, including telephone, email, digital communication and, where available and authorized, remote connection to Equipment.",
            "Contract Year: each consecutive twelve-month period beginning on the Contract Start Date.",
        ],
    },

    # 4. EQUIPMENT COVERED
    {"type": "h2", "id": "master.clause4.title", "text": "4. EQUIPMENT COVERED"},
    {"type": "p", "id": "master.clause4.p1", "text": "The Guardian Agreement applies exclusively to the Equipment listed in Annex 1."},
    {"type": "p", "id": "master.clause4.p2", "text": "Annex 1 shall identify, as applicable:"},
    {
        "type": "ul",
        "id": "master.clause4.identify",
        "items": [
            "Customer production line;",
            "Weber machine reference;",
            "serial number;",
            "equipment type;",
            "modules included;",
            "service frequency;",
            "planned inspection or service time;",
            "selected Guardian modules;",
            "applicable service price; and",
            "any machine-specific commercial conditions.",
        ],
    },
    {
        "type": "p",
        "id": "master.clause4.p3",
        "text": (
            "The Customer shall notify Weber in writing of any relocation, material modification, "
            "disposal or sale of Equipment covered by this Agreement."
        ),
    },
    {
        "type": "p",
        "id": "master.clause4.p4",
        "text": (
            "Where Equipment is sold or permanently transferred to another legal entity or location, "
            "the continuation of the Guardian Agreement shall be subject to written confirmation by Weber."
        ),
    },
    {
        "type": "p",
        "id": "master.clause4.p5",
        "text": "The Parties may add or remove Equipment during the contract term by written amendment to Annex 1.",
    },

    # 5. GENERAL SERVICE PRINCIPLES
    {"type": "h2", "id": "master.clause5.title", "text": "5. GENERAL SERVICE PRINCIPLES"},
    {
        "type": "p",
        "id": "master.clause5.p1",
        "text": (
            "Weber shall perform the selected Services using appropriately qualified personnel and "
            "in accordance with generally accepted technical standards and Weber service procedures "
            "applicable to the relevant Equipment."
        ),
    },
    {
        "type": "p",
        "id": "master.clause5.p2",
        "text": "Weber may use qualified Weber affiliated companies or authorized Weber service partners for the performance of Services.",
    },
    {
        "type": "p",
        "id": "master.clause5.p3",
        "text": (
            "Weber shall determine the number and qualification of technicians reasonably necessary "
            "for the applicable service activity, taking into account the Equipment configuration "
            "and scope of work."
        ),
    },
    {
        "type": "p",
        "id": "master.clause5.p4",
        "text": "The Guardian Agreement does not constitute a guarantee that Equipment will operate without interruption or failure.",
    },
    {
        "type": "p",
        "id": "master.clause5.excluded_intro",
        "text": "Unless expressly included in an applicable Annex, the following are not included in the fixed Guardian fee:",
    },
    {
        "type": "ul",
        "id": "master.clause5.excluded",
        "items": [
            "corrective repairs;",
            "replacement parts;",
            "wear parts and consumables;",
            "upgrades or modifications;",
            "third-party equipment;",
            "work outside the agreed service hours;",
            "emergency interventions;",
            "additional travel;",
            "special access equipment;",
            "production materials;",
            "special tooling not normally required for the relevant Weber Equipment; and",
            "work resulting from misuse, damage, external causes or modifications not approved by Weber.",
        ],
    },
    {"type": "p", "id": "master.clause5.p5", "text": "Such services may be quoted and ordered separately."},

    # 6. CUSTOMER COOPERATION
    {"type": "h2", "id": "master.clause6.title", "text": "6. CUSTOMER COOPERATION"},
    {"type": "p", "id": "master.clause6.p1", "text": "The Customer shall provide the cooperation reasonably required for Weber to perform the Services."},
    {"type": "p", "id": "master.clause6.p2", "text": "In particular, the Customer shall ensure that:"},
    {
        "type": "ol",
        "id": "master.clause6.obligations",
        "items": [
            "Weber personnel have safe and timely access to the relevant Equipment;",
            "the Equipment is available at the agreed time;",
            "the Equipment is in a reasonably clean and accessible condition;",
            "production can be interrupted where required for the agreed work;",
            "utilities and technical connections required for the work, including electricity, compressed air, water, network access or VPN access where applicable, are available;",
            "suitable Customer personnel are available where assistance is required;",
            "sufficient original product is available where a production or functional test is required;",
            "Weber is informed in advance of known faults, unusual operating conditions or safety requirements;",
            "all site-specific health and safety requirements are communicated to Weber before work begins; and",
            "a Customer representative with sufficient authority is available to approve additional work or the replacement of components where necessary.",
        ],
    },
    {
        "type": "p",
        "id": "master.clause6.p3",
        "text": (
            "Any delay, waiting time or additional expense resulting from the Customer's failure to "
            "fulfil these obligations may be charged separately in accordance with the applicable "
            "Weber rates."
        ),
    },

    # 7. SCHEDULING
    {"type": "h2", "id": "master.clause7.title", "text": "7. SCHEDULING"},
    {
        "type": "p",
        "id": "master.clause7.p1",
        "text": (
            "Planned inspections, maintenance visits, training and other scheduled Services shall be "
            "coordinated between Weber and the Customer."
        ),
    },
    {"type": "p", "id": "master.clause7.p2", "text": "Weber shall use reasonable efforts to provide the Customer with advance notice of the planned date."},
    {
        "type": "p",
        "id": "master.clause7.p3",
        "text": "The applicable notice period, where specifically agreed, shall be stated in the relevant Annex or Annex 1.",
    },
    {
        "type": "p",
        "id": "master.clause7.p4",
        "text": "If either Party becomes unable to perform an agreed activity on the scheduled date, it shall inform the other Party as soon as reasonably possible.",
    },
    {
        "type": "p",
        "id": "master.clause7.p5",
        "text": (
            "Where a scheduled visit cannot be performed for reasons attributable to the Customer, "
            "Weber may charge any costs reasonably incurred, including travel, accommodation, "
            "waiting time and reserved personnel capacity."
        ),
    },

    # 8. ADDITIONAL WORK IDENTIFIED DURING A SERVICE ACTIVITY
    {"type": "h2", "id": "master.clause8.title", "text": "8. ADDITIONAL WORK IDENTIFIED DURING A SERVICE ACTIVITY"},
    {
        "type": "p",
        "id": "master.clause8.p1",
        "text": "Where an inspection, maintenance activity, audit or other Guardian service identifies additional work, Weber shall inform the Customer.",
    },
    {
        "type": "p",
        "id": "master.clause8.p2",
        "text": "Unless Annex 1 expressly provides otherwise, such additional work shall not automatically form part of the Guardian fixed fee.",
    },
    {
        "type": "p",
        "id": "master.clause8.p3",
        "text": (
            "Corrective maintenance, repairs, modifications, upgrades and the replacement of parts "
            "identified during an inspection shall require Customer authorization."
        ),
    },
    {
        "type": "p",
        "id": "master.clause8.p4",
        "text": "Where appropriate, Weber may issue a separate quotation or spare-parts recommendation following the service activity.",
    },
    {
        "type": "p",
        "id": "master.clause8.p5",
        "text": (
            "No additional chargeable work shall be intentionally performed without Customer "
            "authorization, except where immediate action is reasonably necessary to prevent an "
            "imminent safety risk and such action is permitted by applicable law and site rules."
        ),
    },

    # 9. PRICES AND PAYMENT
    {"type": "h2", "id": "master.clause9.title", "text": "9. PRICES AND PAYMENT"},
    {"type": "p", "id": "master.clause9.p1", "text": "The prices applicable to the Guardian Agreement are stated in Annex 1."},
    {"type": "p", "id": "master.clause9.p2", "text": "Unless expressly stated otherwise, all prices are exclusive of VAT and other applicable taxes."},
    {
        "type": "p",
        "id": "master.clause9.p3",
        "text": (
            "The applicable currency, billing frequency, payment terms, travel conditions, freight "
            "conditions, discounts and additional service rates shall be those specified in Annex 1 "
            "or the applicable service Annex."
        ),
    },
    {"type": "p", "id": "master.clause9.p4", "text": "Recurring Guardian fees shall be invoiced according to the billing frequency stated in Annex 1."},
    {
        "type": "p",
        "id": "master.clause9.p5",
        "text": (
            "Services, materials and expenses not included in the agreed Guardian fee shall be "
            "invoiced separately at the applicable agreed rates."
        ),
    },
    {
        "type": "p",
        "id": "master.clause9.p6",
        "text": "Weber may adjust recurring prices in accordance with the annual price adjustment mechanism stated in Annex 1.",
    },
    {
        "type": "p",
        "id": "master.clause9.p7",
        "text": (
            "Any agreed discount applies only to the categories expressly identified in the "
            "relevant Annex and shall not be combined with other discounts unless expressly agreed."
        ),
    },

    # 10. PARTS AND MATERIALS
    {"type": "h2", "id": "master.clause10.title", "text": "10. PARTS AND MATERIALS"},
    {
        "type": "p",
        "id": "master.clause10.p1",
        "text": (
            "Unless specifically included in Annex 1 or an applicable service Annex, spare parts, "
            "wear parts, blades, lubricants and other materials are not included in the Guardian "
            "service fee."
        ),
    },
    {
        "type": "p",
        "id": "master.clause10.p2",
        "text": (
            "Parts supplied by Weber shall be invoiced at the price applicable at the date of "
            "supply, less any Guardian discount expressly agreed under Annex 4 or Annex 5."
        ),
    },
    {
        "type": "p",
        "id": "master.clause10.p3",
        "text": (
            "Where replaced components are made available to the Customer for inspection, the "
            "Customer shall be responsible for their subsequent disposal unless otherwise agreed."
        ),
    },
    {
        "type": "p",
        "id": "master.clause10.p4",
        "text": (
            "Weber shall not be responsible for defects, damage, reduced performance or "
            "consequential effects caused by non-original components, unauthorized modifications "
            "or work performed by third parties, to the extent permitted by applicable law."
        ),
    },
    {
        "type": "p",
        "id": "master.clause10.p5",
        "text": (
            "Title to supplied goods shall remain with Weber until full payment has been received "
            "where permitted under the applicable local terms and law."
        ),
    },

    # 11. ACCEPTANCE AND SERVICE REPORTING
    {"type": "h2", "id": "master.clause11.title", "text": "11. ACCEPTANCE AND SERVICE REPORTING"},
    {
        "type": "p",
        "id": "master.clause11.p1",
        "text": (
            "Where the nature of a Service allows functional verification, the Customer shall "
            "provide Weber with a reasonable opportunity to test the Equipment following completion "
            "of the activity."
        ),
    },
    {
        "type": "p",
        "id": "master.clause11.p2",
        "text": (
            "Where the Customer identifies a material deficiency in the performance of a Service, it "
            "shall notify Weber without undue delay and provide sufficient information to allow "
            "Weber to assess the issue."
        ),
    },
    {
        "type": "p",
        "id": "master.clause11.p3",
        "text": (
            "If a Service has demonstrably not been performed in accordance with the agreed scope "
            "and Weber is responsible for the deficiency, Weber shall, as its primary remedy, "
            "re-perform or correct the affected Service within a reasonable period."
        ),
    },
    {
        "type": "p",
        "id": "master.clause11.p4",
        "text": (
            "Service reports, inspection reports, audit reports and recommendations document the "
            "condition observed at the time of the activity and do not constitute a guarantee of "
            "future machine performance."
        ),
    },

    # 12. WARRANTY AND LIABILITY
    {"type": "h2", "id": "master.clause12.title", "text": "12. WARRANTY AND LIABILITY"},
    {"type": "p", "id": "master.clause12.p1", "text": "Weber shall perform the Services with reasonable professional care and skill."},
    {
        "type": "p",
        "id": "master.clause12.p2",
        "text": (
            "Weber's liability shall be governed by the mandatory provisions of the applicable law "
            "and Weber's applicable General Terms and Conditions."
        ),
    },
    {
        "type": "p",
        "id": "master.clause12.p3",
        "text": (
            "To the maximum extent permitted by law, Weber shall not be liable for indirect or "
            "consequential losses, including loss of production, loss of profit, loss of business "
            "or other indirect commercial loss, except where such limitation is prohibited by "
            "applicable law."
        ),
    },
    {"type": "p", "id": "master.clause12.p4", "text": "Nothing in this Agreement shall exclude liability which cannot legally be excluded or limited."},
    {
        "type": "p",
        "id": "master.clause12.p5",
        "text": (
            "Where a failure or delay results from circumstances outside Weber's reasonable "
            "control, including failure or delay by suppliers, transportation disruption, "
            "industrial action, natural events, governmental measures, cyber incidents, epidemics "
            "or other events of force majeure, the affected performance period shall be extended "
            "as reasonably necessary."
        ),
    },

    # 13. CONTRACT TERM AND RENEWAL
    {"type": "h2", "id": "master.clause13.title", "text": "13. CONTRACT TERM AND RENEWAL"},
    {"type": "p", "id": "master.clause13.p1", "text": "This Agreement enters into force on the Contract Start Date stated in Annex 1."},
    {"type": "kv", "id": "master.clause13.term", "label": "Initial Term", "token": "Contract_Duration"},
    {"type": "kv", "id": "master.clause13.renewal", "label": "Renewal Term", "token": "Renewal_Term"},
    {"type": "kv", "id": "master.clause13.notice", "label": "Notice Period", "token": "Termination_Notice_Period"},
    {
        "type": "p",
        "id": "master.clause13.p2",
        "text": (
            "Unless otherwise stated in Annex 1, the Agreement shall automatically renew for "
            "successive renewal periods unless terminated in writing within the applicable notice period."
        ),
    },
    {
        "type": "p",
        "id": "master.clause13.p3",
        "text": (
            "The termination or expiry of the Master Agreement shall terminate all service Annexes "
            "unless otherwise expressly agreed."
        ),
    },
    {
        "type": "p",
        "id": "master.clause13.p4",
        "text": "Individual optional services may have different commencement or expiry dates where expressly stated in the relevant Annex.",
    },

    # 14. CHANGES TO THE AGREEMENT
    {"type": "h2", "id": "master.clause14.title", "text": "14. CHANGES TO THE AGREEMENT"},
    {
        "type": "p",
        "id": "master.clause14.p1",
        "text": (
            "Changes to Equipment covered, service frequency, Guardian modules, discounts, service "
            "levels, pricing or other material contractual conditions shall be documented in writing."
        ),
    },
    {"type": "p", "id": "master.clause14.p2", "text": "An updated Annex generated and accepted by both Parties may constitute such written amendment."},

    # 15. CONFIDENTIALITY
    {"type": "h2", "id": "master.clause15.title", "text": "15. CONFIDENTIALITY"},
    {
        "type": "p",
        "id": "master.clause15.p1",
        "text": (
            "Each Party shall keep confidential all non-public commercial, technical and operational "
            "information received from the other Party in connection with this Agreement."
        ),
    },
    {
        "type": "p",
        "id": "master.clause15.p2",
        "text": "Such information shall be used only for the performance and administration of the Guardian relationship.",
    },
    {"type": "p", "id": "master.clause15.p3", "text": "This obligation shall not apply to information which:"},
    {
        "type": "ul",
        "id": "master.clause15.exceptions",
        "items": [
            "is already lawfully in the public domain;",
            "was lawfully known to the receiving Party before disclosure;",
            "is received lawfully from a third party without confidentiality restrictions; or",
            "must be disclosed by law or competent authority.",
        ],
    },

    # 16. INTELLECTUAL PROPERTY
    {"type": "h2", "id": "master.clause16.title", "text": "16. INTELLECTUAL PROPERTY"},
    {
        "type": "p",
        "id": "master.clause16.p1",
        "text": (
            "All intellectual property rights in Weber documentation, service methods, checklists, "
            "software, technical information, training materials, analyses and other proprietary "
            "Weber content remain the property of Weber or the applicable rights holder."
        ),
    },
    {
        "type": "p",
        "id": "master.clause16.p2",
        "text": "The Customer may use documentation provided under this Agreement internally for the operation and maintenance of its Equipment.",
    },
    {"type": "p", "id": "master.clause16.p3", "text": "No intellectual property rights are transferred to the Customer unless expressly agreed in writing."},

    # 17. ASSIGNMENT AND SERVICE PARTNERS
    {"type": "h2", "id": "master.clause17.title", "text": "17. ASSIGNMENT AND SERVICE PARTNERS"},
    {
        "type": "p",
        "id": "master.clause17.p1",
        "text": "Weber may perform its obligations through Weber group companies or qualified and authorized Weber service partners.",
    },
    {
        "type": "p",
        "id": "master.clause17.p2",
        "text": "Weber may assign rights and obligations under this Agreement to another Weber group company subject to applicable law.",
    },
    {
        "type": "p",
        "id": "master.clause17.p3",
        "text": (
            "The Customer may not assign this Agreement to a third party without Weber's prior "
            "written consent, such consent not to be unreasonably withheld where continuation of "
            "the contractual relationship is commercially and technically feasible."
        ),
    },

    # 18. GOVERNING LAW AND JURISDICTION
    {"type": "h2", "id": "master.clause18.title", "text": "18. GOVERNING LAW AND JURISDICTION"},
    {"type": "kv", "id": "master.clause18.law", "label": "Governing Law", "token": "Governing_Law"},
    {"type": "kv", "id": "master.clause18.jurisdiction", "label": "Jurisdiction", "token": "Jurisdiction"},
    {"type": "p", "id": "master.clause18.p1", "text": "The above provisions are subject in each case to mandatory applicable law."},

    # 19. GENERAL PROVISIONS
    {"type": "h2", "id": "master.clause19.title", "text": "19. GENERAL PROVISIONS"},
    {
        "type": "p",
        "id": "master.clause19.p1",
        "text": (
            "If any provision of this Agreement is found to be invalid or unenforceable, the "
            "remaining provisions shall remain unaffected."
        ),
    },
    {"type": "p", "id": "master.clause19.p2", "text": "Failure by either Party to exercise a contractual right shall not constitute a waiver of that right."},
    {
        "type": "p",
        "id": "master.clause19.p3",
        "text": (
            "This Agreement and its applicable Annexes constitute the agreement between the Parties "
            "concerning the Guardian Services described herein and replace prior proposals or "
            "understandings relating specifically to the same service scope, unless expressly incorporated."
        ),
    },
    {"type": "p", "id": "master.clause19.p4", "text": "Amendments shall be made in writing."},
    {
        "type": "p",
        "id": "master.clause19.p5",
        "text": (
            "Electronic signatures may be used where legally permitted and shall have the same "
            "effect as handwritten signatures."
        ),
    },
]
