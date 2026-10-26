"""German overrides for the Guardian agreement content (full catalog).

Responsibility: translate every translatable node id to German. Any node id
missing here falls back to the English source text, so a parity test
(test_content.py) requires this catalog to cover all translatable ids.
Overrides are strings for text nodes and lists of strings for list nodes
(ul, ol, dl, lines), mirroring the English source shape. Pure-token nodes
(address lines, special-conditions slot) are intentionally not translated:
{{Token}} placeholders must survive verbatim. Ids must exist in the English
section modules; the test suite rejects unknown ids and wrong override shapes.
"""

from __future__ import annotations

MESSAGES: dict[str, str | list[str]] = {
    # Module labels (labels.MODULE_LABELS)
    "module.maintenance_inspection": "Wartung und Inspektion",
    "module.service_support": "Service-Support",
    "module.parts_availability": "Ersatzteile und Verfügbarkeit",
    "module.blade_solutions": "Klingenlösungen",
    "module.training_optimization": "Schulung und Optimierung",
    "module.digital_services": "Digitale Dienstleistungen",

    # Guardian contract types (labels.GUARDIAN_TYPE_LABELS)
    "guardian_type.audit": "Inspektion",
    "guardian_type.off_guardian": "Off-Guardian",
    "guardian_type.guardian": "Basic Kit",

    # Cover
    "cover.title": "WARTUNGSVERTRAG",
    "cover.executor.label": "Zwischen dem Unternehmen:",
    "cover.executor.alias": "(nachfolgend der Auftragnehmer)",
    "cover.customer.label": "Und dem Unternehmen:",
    "cover.customer.alias": "(nachfolgend der Auftraggeber)",
    "cover.preamble": (
        "wird der folgende Inspektions- und Wartungsvertrag geschlossen "
        '(nachfolgend der "Vertrag"):'
    ),

    # Commercial breakdown (legacy Annex 1)
    "breakdown.title": "ANHANG 1, Liste der Maschinen und Module",
    "breakdown.date": "Datum",
    "breakdown.offer_no": "Angebots-Nr.",
    "breakdown.frequency": "Inspektionsfrequenz",
    "breakdown.type": "Typ",
    "breakdown.col.line": "Linie",
    "breakdown.col.module": "Modul",
    "breakdown.col.amount": "Betrag",
    "breakdown.total": "Gesamt",
    "breakdown.kit": "Basis-Ersatzteil-Kit",
    "breakdown.discount": "Rabatt bei Wartungsvertrag",
    "breakdown.grand_total": "Gesamtbetrag (exkl. MwSt.)",
    "breakdown.intro": (
        "Beide Parteien vereinbaren das folgende Inspektionsangebot von Weber zu den "
        "nachstehend aufgeführten Bedingungen:"
    ),
    "breakdown.notes": [
        "einschließlich Anreise, Arbeitsleistung und Dokumentation.",
        "Überprüfung von Sensoren, elektrischen Bauteilen, Antrieben, Zahnriemen und "
        "Klingen (das Basis-Kit umfasst den Austausch der Hauptriemen von Kopf, Spindel "
        "und Zusatzmodulen).",
        "Einstellung der mechanischen Teile der verschiedenen Module.",
        "Überprüfung und Optimierung der Programme.",
        "Erfassung aller geplanten Reparaturen.",
    ],
    "breakdown.notes_title": "HINWEISE:",
    "breakdown.discount_notes": [
        "15 % Rabatt auf die technische Unterstützung für die vertraglich gebundenen Linien.",
        "5 % Rabatt auf Ersatzteile für die vertraglich gebundenen Linien (nicht "
        "anwendbar auf bestehende Rabatte).",
        "5 % Rabatt auf Klingen bei kompletten Schachteln mit 3 Klingen (nicht "
        "anwendbar auf bestehende Rabatte).",
        "einschließlich eines kostenlosen Nachfolgebesuchs nach 6 Monaten.",
        "Alle Teile, Verbrauchsmaterialien und Ersatzteile außerhalb des Angebots "
        "sowie Stunden außerhalb der normalen Arbeitszeiten, Wartezeiten und "
        "Reparaturen außerhalb des Angebots werden separat in Rechnung gestellt.",
    ],

    # Master Agreement
    "master.title": "WEBER GUARDIAN RAHMENVEREINBARUNG",
    "master.kv.agreement_no": "Vereinbarungs-Nr.",
    "master.kv.offer_no": "Angebots-Nr.",
    "master.kv.offer_date": "Angebotsdatum",
    "master.kv.start_date": "Vertragsbeginn",
    "master.kv.term": "Anfängliche Vertragslaufzeit",
    "master.kv.billing": "Abrechnungshäufigkeit",
    "master.between": "ZWISCHEN",
    "master.weber_definition": "nachfolgend „Weber“ genannt.",
    "master.customer_definition": "nachfolgend „Kunde“ genannt.",
    "master.parties": (
        "Weber und der Kunde werden jeweils einzeln als „Partei“ und gemeinsam als "
        "„die Parteien“ bezeichnet."
    ),

    # 1. PURPOSE OF THE AGREEMENT
    "master.clause1.title": "1. ZWECK DER VEREINBARUNG",
    "master.clause1.p1": (
        "Zweck dieser Guardian-Vereinbarung ist es, den zuverlässigen, effizienten und "
        "wirtschaftlich nachhaltigen Betrieb der Weber-Ausrüstung des Kunden über deren "
        "gesamte Lebensdauer zu unterstützen."
    ),
    "master.clause1.p2": (
        "Guardian ist ein modulares After-Sales-Programm. Je nach den vom Kunden "
        "ausgewählten Modulen kann die Vereinbarung Inspektions- und vorbeugende "
        "Wartungsleistungen, technischen Support, Ersatzteil-Dienstleistungen, "
        "Klingenlösungen, Schulungs- und Optimierungsleistungen sowie digitale "
        "Dienstleistungen umfassen."
    ),
    "master.clause1.p3": (
        "Eingeschlossen sind ausschließlich die in den zutreffenden Anhängen dieser "
        "Vereinbarung ausdrücklich bezeichneten Leistungen."
    ),
    "master.clause1.goals_intro": "Das Ziel des Guardian-Programms ist:",
    "master.clause1.goals": [
        "die Zuverlässigkeit und Verfügbarkeit der Ausrüstung zu verbessern;",
        "die vorbeugende Wartung und das frühzeitige Erkennen technischer Probleme zu unterstützen;",
        "vermeidbare ungeplante Stillstände zu reduzieren;",
        "eine vorhersehbare Wartungsplanung und planbare Wartungsausgaben zu unterstützen;",
        "den Zugang zur technischen Expertise von Weber sicherzustellen;",
        "die Verwaltung von Ersatzteilen und Klingen zu optimieren;",
        "die Betriebs- und Wartungspraktiken zu verbessern; und",
        "die kontinuierliche Optimierung der beim Kunden installierten Ausrüstung zu unterstützen.",
    ],
    "master.clause1.exclusion": (
        "Keine Leistung, kein Rabatt, keine Reaktionszusage und kein sonstiger Vorteil "
        "gilt als eingeschlossen, sofern sie nicht ausdrücklich in dieser Vereinbarung "
        "oder einem ihr zugehörigen Anhang festgehalten ist."
    ),

    # 2. CONTRACT DOCUMENTS AND MODULAR STRUCTURE
    "master.clause2.title": "2. VERTRAGSDOKUMENTE UND MODULARE STRUKTUR",
    "master.clause2.p1": (
        "Diese Vereinbarung besteht aus dieser Rahmenvereinbarung und den nachstehend "
        "aufgeführten Anhängen, die für den Kunden ausgewählt wurden."
    ),
    "master.clause2.annexes": [
        "Anhang 1 - Ausrüstung und Konditionen: stets anwendbar.",
        "Anhang 2 - Wartung und Inspektion: nur anwendbar, wenn das Modul Wartung und Inspektion ausgewählt ist.",
        "Anhang 3 - Service-Support: nur anwendbar, wenn das Modul Service-Support ausgewählt ist.",
        "Anhang 4 - Ersatzteile und Verfügbarkeit: nur anwendbar, wenn das Modul Ersatzteile und Verfügbarkeit ausgewählt ist.",
        "Anhang 5 - Klingenlösungen: nur anwendbar, wenn das Modul Klingenlösungen ausgewählt ist.",
        "Anhang 6 - Schulung und Optimierung: nur anwendbar, wenn das Modul Schulung und Optimierung ausgewählt ist.",
        "Anhang 7 - Digitale Dienstleistungen: nur anwendbar, wenn das Modul Digitale Dienstleistungen ausgewählt ist.",
    ],
    "master.clause2.p2": "Die zutreffenden Anhänge sind wesentlicher Bestandteil dieser Vereinbarung.",
    "master.clause2.p3": (
        "Die Leistungen gelten nur für die in Anhang 1 bezeichneten Maschinen, "
        "Produktionslinien, Module und Standorte, sofern nicht schriftlich etwas "
        "anderes vereinbart ist."
    ),
    "master.clause2.p4": (
        "Bestehen Widersprüche zwischen den Dokumenten dieser Vereinbarung, gilt die "
        "folgende Rangfolge:"
    ),
    "master.clause2.precedence": [
        "Anhang 1 - Ausrüstung und Konditionen;",
        "der jeweilige leistungsspezifische Anhang;",
        "diese Rahmenvereinbarung; und",
        "die allgemeinen Geschäftsbedingungen von Weber.",
    ],
    "master.clause2.p5": (
        "Kundenspezifische Abweichungen, die in Anhang 1 ausdrücklich festgehalten "
        "sind, haben Vorrang vor den Standardbestimmungen zum selben Gegenstand."
    ),

    # 3. DEFINITIONS
    "master.clause3.title": "3. BEGRIFFE",
    "master.clause3.definitions": [
        "Ausrüstung: die in Anhang 1 ausdrücklich aufgeführten Maschinen, Module, Systeme oder sonstige Ausrüstung.",
        "Inspektion: die Beurteilung des tatsächlichen Zustands der Ausrüstung mit dem Ziel, Verschleiß, Unregelmäßigkeiten, erforderliche Wartungen und mögliche Maßnahmen zur Sicherstellung des künftigen Betriebs zu identifizieren.",
        "Vorbeugende Wartung: geplante Maßnahmen zur Reduzierung von Verschleiß und Ausfallrisiko, einschließlich Einstellen, Schmieren, Reinigen, dem Austausch definierter Verschleißteile und sonstiger ausdrücklich in den zutreffenden Leistungsumfang eingeschlossener Tätigkeiten.",
        "Korrekturwartung / Reparatur: Arbeiten zur Wiederherstellung des erforderlichen Betriebszustands der Ausrüstung nach einem Fehler, Ausfall oder festgestellten Defekt.",
        "Verschleißteile: Bauteile, die aufgrund ihrer vorgesehenen Funktion und je nach Betriebs- und Nutzungsbedingungen einen regelmäßigen Austausch erfordern.",
        "Ersatzteile: für die Ausrüstung gelieferte Austauschbauteile.",
        "Leistungen: die ausdrücklich ausgewählten und in den zutreffenden Anhängen beschriebenen Guardian-Leistungen.",
        "Serviceeinsatz: ein vereinbarter physischer Einsatz von Weber-Personal oder eines autorisierten Weber-Servicepartners beim Standort des Kunden.",
        "Remote-Support: technischer Support ohne physischen Einsatz, einschließlich Telefon, E-Mail, digitaler Kommunikation und, sofern verfügbar und autorisiert, der Fernanbindung an die Ausrüstung.",
        "Vertragsjahr: jeder aufeinanderfolgende Zeitraum von zwölf Monaten beginnend am Vertragsbeginn.",
    ],

    # 4. EQUIPMENT COVERED
    "master.clause4.title": "4. ERFASTE AUSRÜSTUNG",
    "master.clause4.p1": (
        "Die Guardian-Vereinbarung gilt ausschließlich für die in Anhang 1 aufgeführte "
        "Ausrüstung."
    ),
    "master.clause4.p2": "Anhang 1 bezeichnet, soweit zutreffend:",
    "master.clause4.identify": [
        "die Produktionslinie des Kunden;",
        "die Maschinenreferenz von Weber;",
        "die Seriennummer;",
        "die Ausrüstungsart;",
        "die enthaltenen Module;",
        "die Servicefrequenz;",
        "die geplante Inspektions- oder Servicezeit;",
        "die ausgewählten Guardian-Module;",
        "der zutreffende Servicepreis; und",
        "sonstige maschinenspezifische Konditionen.",
    ],
    "master.clause4.p3": (
        "Der Kunde informiert Weber schriftlich über jeden Umzug, jede wesentliche "
        "Änderung, Veräußerung oder jeden Verkauf der von dieser Vereinbarung "
        "erfassten Ausrüstung."
    ),
    "master.clause4.p4": (
        "Wird Ausrüstung verkauft oder dauerhaft auf eine andere juristische Person "
        "oder einen anderen Standort übertragen, setzt die Fortführung der "
        "Guardian-Vereinbarung die schriftliche Bestätigung durch Weber voraus."
    ),
    "master.clause4.p5": (
        "Die Parteien können die Ausrüstung während der Vertragslaufzeit durch eine "
        "schriftliche Änderung von Anhang 1 hinzufügen oder entfernen."
    ),

    # 5. GENERAL SERVICE PRINCIPLES
    "master.clause5.title": "5. ALLGEMEINE SERVICEGRUNDSÄTZE",
    "master.clause5.p1": (
        "Weber erbringt die ausgewählten Leistungen mit angemessen qualifiziertem "
        "Personal und in Übereinstimmung mit den allgemein anerkannten technischen "
        "Standards und den für die jeweilige Ausrüstung geltenden "
        "Weber-Serviceverfahren."
    ),
    "master.clause5.p2": (
        "Weber kann für die Erbringung der Leistungen qualifizierte verbundene "
        "Unternehmen von Weber oder autorisierte Weber-Servicepartner einsetzen."
    ),
    "master.clause5.p3": (
        "Weber bestimmt die Anzahl und Qualifikation der Techniker, die für die "
        "jeweilige Serviceaktivität angemessen erforderlich sind, unter "
        "Berücksichtigung der Konfiguration der Ausrüstung und des Arbeitsumfangs."
    ),
    "master.clause5.p4": (
        "Die Guardian-Vereinbarung ist keine Garantie dafür, dass die Ausrüstung ohne "
        "Unterbrechung oder Ausfall betrieben wird."
    ),
    "master.clause5.excluded_intro": (
        "Sofern nicht ausdrücklich in einem zutreffenden Anhang eingeschlossen, sind "
        "Folgendes nicht im festen Guardian-Entgelt enthalten:"
    ),
    "master.clause5.excluded": [
        "Korrekturreparaturen;",
        "Austauschteile;",
        "Verschleißteile und Verbrauchsmaterial;",
        "Upgrades oder Änderungen;",
        "Ausrüstung Dritter;",
        "Arbeiten außerhalb der vereinbarten Servicezeiten;",
        "Notfalleinsätze;",
        "zusätzliche Anfahrten;",
        "spezielle Zugangsausrüstung;",
        "Produktionsmaterial;",
        "Spezialwerkzeuge, die für die betreffende Weber-Ausrüstung normalerweise nicht erforderlich sind; und",
        "Arbeiten, die auf unsachgemäße Verwendung, Schäden, äußere Ursachen oder nicht von Weber genehmigte Änderungen zurückzuführen sind.",
    ],
    "master.clause5.p5": (
        "Solche Leistungen können separat angeboten und bestellt werden."
    ),

    # 6. CUSTOMER COOPERATION
    "master.clause6.title": "6. MITWIRKUNG DES KUNDEN",
    "master.clause6.p1": (
        "Der Kunde leistet die für die Erbringung der Leistungen durch Weber "
        "angemessen erforderliche Mitwirkung."
    ),
    "master.clause6.p2": "Im Einzelnen stellt der Kunde sicher, dass:",
    "master.clause6.obligations": [
        "Weber-Personal einen sicheren und rechtzeitigen Zugang zu der jeweiligen Ausrüstung hat;",
        "die Ausrüstung zur vereinbarten Zeit zur Verfügung steht;",
        "die Ausrüstung in einem angemessen sauberen und zugänglichen Zustand ist;",
        "die Produktion für die vereinbarten Arbeiten bei Bedarf unterbrochen werden kann;",
        "die für die Arbeiten erforderlichen Versorgungsmedien und technischen Anschlüsse einschließlich Strom, Druckluft, Wasser, Netzwerkzugang oder, soweit zutreffend, VPN-Zugang verfügbar sind;",
        "geeignetes Personal des Kunden verfügbar ist, wenn Unterstützung erforderlich ist;",
        "ausreichendes Originalprodukt verfügbar ist, wenn ein Produktions- oder Funktionstest erforderlich ist;",
        "Weber im Voraus über bekannte Fehler, ungewöhnliche Betriebsbedingungen oder Sicherheitsanforderungen informiert wird;",
        "alle standortspezifischen Arbeitssicherheits- und Gesundheitsschutzanforderungen vor Arbeitsbeginn an Weber übermittelt werden; und",
        "ein Vertreter des Kunden mit ausreichender Vollmacht verfügbar ist, um zusätzliche Arbeiten oder den Austausch von Bauteilen bei Bedarf zu genehmigen.",
    ],
    "master.clause6.p3": (
        "Jede Verzögerung, Wartezeit oder zusätzliche Kosten, die aus der "
        "Nichterfüllung dieser Pflichten durch den Kunden resultieren, können gemäß "
        "den zutreffenden Weber-Sätzen separat berechnet werden."
    ),

    # 7. SCHEDULING
    "master.clause7.title": "7. TERMINPLANUNG",
    "master.clause7.p1": (
        "Geplante Inspektionen, Wartungseinsätze, Schulungen und andere geplante "
        "Leistungen werden zwischen Weber und dem Kunden koordiniert."
    ),
    "master.clause7.p2": (
        "Weber unternimmt angemessene Anstrengungen, um den Kunden über das geplante "
        "Datum im Voraus zu informieren."
    ),
    "master.clause7.p3": (
        "Die zutreffende Vorankündigungsfrist, sofern gesondert vereinbart, wird im "
        "jeweiligen Anhang oder in Anhang 1 angegeben."
    ),
    "master.clause7.p4": (
        "Kann eine der Parteien eine vereinbarte Tätigkeit am geplanten Datum nicht "
        "durchführen, informiert sie die andere Partei so früh wie vernünftig möglich."
    ),
    "master.clause7.p5": (
        "Kann ein geplanter Einsatz aus Gründen, die dem Kunden zuzurechnen sind, "
        "nicht durchgeführt werden, kann Weber die angemessen entstandenen Kosten "
        "berechnen, einschließlich Anfahrt, Unterkunft, Wartezeit und reservierter "
        "Kapazität des Personals."
    ),

    # 8. ADDITIONAL WORK IDENTIFIED DURING A SERVICE ACTIVITY
    "master.clause8.title": "8. ZUSÄTZLICHE ARBEITEN BEI EINER SERVICEAKTIVITÄT",
    "master.clause8.p1": (
        "Wenn eine Inspektion, Wartungstätigkeit, Audit oder sonstige "
        "Guardian-Leistung zusätzliche Arbeiten identifiziert, informiert Weber den "
        "Kunden."
    ),
    "master.clause8.p2": (
        "Sofern Anhang 1 nicht ausdrücklich etwas anderes bestimmt, werden solche "
        "zusätzlichen Arbeiten nicht automatisch Teil des festen Guardian-Entgelts."
    ),
    "master.clause8.p3": (
        "Korrekturwartung, Reparaturen, Änderungen, Upgrades und der Austausch von "
        "Teilen, die während einer Inspektion festgestellt werden, bedürfen der "
        "Genehmigung durch den Kunden."
    ),
    "master.clause8.p4": (
        "Wo angemessen, kann Weber nach der Serviceaktivität ein separates Angebot "
        "oder eine Ersatzteil-Empfehlung erstellen."
    ),
    "master.clause8.p5": (
        "Es werden keine zusätzlichen berechnungsfähigen Arbeiten ohne Genehmigung "
        "durch den Kunden durchgeführt, es sei denn, ein unmittelbares Handeln ist "
        "angemessen erforderlich, um ein unmittelbar drohendes Sicherheitsrisiko zu "
        "verhindern, und dieses Handeln ist nach dem geltenden Recht und den "
        "Standortregeln zulässig."
    ),

    # 9. PRICES AND PAYMENT
    "master.clause9.title": "9. PREISE UND ZAHLUNG",
    "master.clause9.p1": (
        "Die für die Guardian-Vereinbarung geltenden Preise sind in Anhang 1 angegeben."
    ),
    "master.clause9.p2": (
        "Sofern nicht ausdrücklich anders angegeben, verstehen sich alle Preise zzgl. "
        "der gesetzlichen Mehrwertsteuer und sonstiger anwendbarer Steuern."
    ),
    "master.clause9.p3": (
        "Die geltende Währung, die Abrechnungshäufigkeit, die Zahlungsbedingungen, "
        "die Anfahrtskonditionen, die Frachtkonditionen, die Rabatte und die "
        "zusätzlichen Servicesätze ergeben sich aus Anhang 1 oder dem jeweiligen "
        "Service-Anhang."
    ),
    "master.clause9.p4": (
        "Wiederkehrende Guardian-Entgelte werden gemäß der in Anhang 1 angegebenen "
        "Abrechnungshäufigkeit abgerechnet."
    ),
    "master.clause9.p5": (
        "Leistungen, Materialien und Aufwendungen, die im vereinbarten "
        "Guardian-Entgelt nicht enthalten sind, werden separat zu den vereinbarten "
        "geltenden Sätzen abgerechnet."
    ),
    "master.clause9.p6": (
        "Weber kann wiederkehrende Preise gemäß dem in Anhang 1 angegebenen "
        "jährlichen Preisanpassungsmechanismus anpassen."
    ),
    "master.clause9.p7": (
        "Jeder vereinbarte Rabatt gilt nur für die im jeweiligen Anhang ausdrücklich "
        "bezeichneten Kategorien und wird nicht mit anderen Rabatten kombiniert, "
        "sofern nicht ausdrücklich vereinbart."
    ),

    # 10. PARTS AND MATERIALS
    "master.clause10.title": "10. TEILE UND MATERIALIEN",
    "master.clause10.p1": (
        "Sofern nicht speziell in Anhang 1 oder einem zutreffenden Service-Anhang "
        "eingeschlossen, sind Ersatzteile, Verschleißteile, Klingen, Schmierstoffe "
        "und sonstige Materialien im Guardian-Serviceentgelt nicht enthalten."
    ),
    "master.clause10.p2": (
        "Von Weber gelieferte Teile werden zum geltenden Preis am Tag der Lieferung "
        "abgerechnet, abzüglich etwaiger ausdrücklich vereinbarter Guardian-Rabatte "
        "gemäß Anhang 4 oder Anhang 5."
    ),
    "master.clause10.p3": (
        "Wird der Kunde zum Zweck der Prüfung mit ausgetauschten Bauteilen versorgt, "
        "ist der Kunde für deren anschließende Entsorgung verantwortlich, sofern "
        "nicht anders vereinbart."
    ),
    "master.clause10.p4": (
        "Weber haftet nicht für Defekte, Schäden, verminderte Leistung oder "
        "Folgewirkungen, die durch nicht originale Bauteile, nicht autorisierte "
        "Änderungen oder Arbeiten von Dritten verursacht werden, soweit nach dem "
        "geltenden Recht zulässig."
    ),
    "master.clause10.p5": (
        "Das Eigentum an den gelieferten Waren verbleibt bei Weber bis zur "
        "vollständigen Bezahlung, soweit dies nach den örtlichen Bedingungen und dem "
        "geltenden Recht zulässig ist."
    ),

    # 11. ACCEPTANCE AND SERVICE REPORTING
    "master.clause11.title": "11. ABNAHME UND SERVICEBERICHTERSTATTUNG",
    "master.clause11.p1": (
        "Wenn die Art einer Leistung eine Funktionsprüfung zulässt, stellt der Kunde "
        "Weber eine angemessene Gelegenheit zur Verfügung, die Ausrüstung nach "
        "Abschluss der Tätigkeit zu prüfen."
    ),
    "master.clause11.p2": (
        "Stellt der Kunde eine wesentliche Mangelhaftigkeit bei der Erbringung einer "
        "Leistung fest, unterrichtet er Weber ohne schuldhaften Verzug und stellt "
        "ausreichende Informationen zur Verfügung, damit Weber den Sachverhalt "
        "beurteilen kann."
    ),
    "master.clause11.p3": (
        "Wurde eine Leistung nachweislich nicht im vereinbarten Umfang erbracht und "
        "ist Weber für den Mangel verantwortlich, wird Weber als vorrangiges Mittel "
        "die betroffene Leistung innerhalb einer angemessenen Frist erneut erbringen "
        "oder den Mangel beheben."
    ),
    "master.clause11.p4": (
        "Serviceberichte, Inspektionsberichte, Audit-Berichte und Empfehlungen "
        "dokumentieren den bei der Tätigkeit festgestellten Zustand und stellen keine "
        "Garantie für die künftige Maschinenleistung dar."
    ),

    # 12. WARRANTY AND LIABILITY
    "master.clause12.title": "12. GEWÄHRLEISTUNG UND HAFTUNG",
    "master.clause12.p1": (
        "Weber erbringt die Leistungen mit angemessener professioneller Sorgfalt und "
        "Fachkenntnis."
    ),
    "master.clause12.p2": (
        "Die Haftung von Weber richtet sich nach den zwingenden Bestimmungen des "
        "geltenden Rechts und den zutreffenden Allgemeinen Geschäftsbedingungen von "
        "Weber."
    ),
    "master.clause12.p3": (
        "Soweit nach dem Gesetz zulässig, haftet Weber nicht für indirekte oder "
        "Folgeschäden, einschließlich Produktionsausfall, entgangenem Gewinn, "
        "Ausfall von Geschäften oder sonstigen mittelbaren wirtschaftlichen Schäden, "
        "es sei denn, eine solche Haftungsbeschränkung ist nach dem geltenden Recht "
        "unzulässig."
    ),
    "master.clause12.p4": (
        "Nichts in dieser Vereinbarung schließt die Haftung aus, die nach dem Gesetz "
        "weder ausgeschlossen noch beschränkt werden kann."
    ),
    "master.clause12.p5": (
        "Wenn ein Ausfall oder eine Verzögerung auf Umstände zurückzuführen ist, die "
        "außerhalb der angemessenen Kontrolle von Weber liegen, einschließlich "
        "Ausfällen oder Verzögerungen bei Lieferanten, Transportstörungen, "
        "Arbeitskämpfen, Naturereignissen, behördlichen Maßnahmen, Cyber-Vorfällen, "
        "Epidemien oder anderen Ereignissen höherer Gewalt, wird der betroffene "
        "Leistungszeitraum angemessen verlängert."
    ),

    # 13. CONTRACT TERM AND RENEWAL
    "master.clause13.title": "13. VERTRAGSLAUFZEIT UND VERLÄNGERUNG",
    "master.clause13.p1": (
        "Diese Vereinbarung tritt am in Anhang 1 angegebenen Vertragsbeginn in Kraft."
    ),
    "master.clause13.term": "Anfängliche Laufzeit",
    "master.clause13.renewal": "Verlängerungslaufzeit",
    "master.clause13.notice": "Kündigungsfrist",
    "master.clause13.p2": (
        "Sofern in Anhang 1 nicht anders angegeben, verlängert sich die Vereinbarung "
        "automatisch um jeweilige Verlängerungszeiträume, sofern sie nicht innerhalb "
        "der zutreffenden Kündigungsfrist schriftlich gekündigt wird."
    ),
    "master.clause13.p3": (
        "Die Kündigung oder der Ablauf der Rahmenvereinbarung beendet alle "
        "Service-Anhänge, sofern nicht ausdrücklich etwas anderes vereinbart ist."
    ),
    "master.clause13.p4": (
        "Einzelne optionale Leistungen können abweichende Beginn- oder Enddaten "
        "haben, sofern dies im jeweiligen Anhang ausdrücklich festgehalten ist."
    ),

    # 14. CHANGES TO THE AGREEMENT
    "master.clause14.title": "14. ÄNDERUNGEN DER VEREINBARUNG",
    "master.clause14.p1": (
        "Änderungen der erfassten Ausrüstung, der Servicefrequenz, der Guardian-Module, "
        "der Rabatte, der Servicelevel, der Preise oder sonstiger wesentlicher "
        "vertraglicher Bedingungen sind schriftlich zu dokumentieren."
    ),
    "master.clause14.p2": (
        "Ein aktualisierter Anhang, der von beiden Parteien erstellt und angenommen "
        "wird, kann eine solche schriftliche Änderung darstellen."
    ),

    # 15. CONFIDENTIALITY
    "master.clause15.title": "15. VERTRAULICHKEIT",
    "master.clause15.p1": (
        "Jede Partei hält alle nicht öffentlichen geschäftlichen, technischen und "
        "operativen Informationen vertraulich, die sie von der anderen Partei im "
        "Zusammenhang mit dieser Vereinbarung erhält."
    ),
    "master.clause15.p2": (
        "Solche Informationen werden ausschließlich für die Erbringung und Verwaltung "
        "der Guardian-Beziehung verwendet."
    ),
    "master.clause15.p3": "Diese Pflicht gilt nicht für Informationen, die:",
    "master.clause15.exceptions": [
        "bereits rechtmäßig öffentlich zugänglich sind;",
        "der empfangenden Partei vor der Offenlegung rechtmäßig bekannt waren;",
        "rechtmäßig von einem Dritten ohne Vertraulichkeitsbeschränkungen erhalten werden; oder",
        "kraft Gesetzes oder auf Verlangen einer zuständigen Behörde offengelegt werden müssen.",
    ],

    # 16. INTELLECTUAL PROPERTY
    "master.clause16.title": "16. GEISTIGES EIGENTUM",
    "master.clause16.p1": (
        "Alle Rechte des geistigen Eigentums an Weber-Dokumentationen, "
        "Serviceverfahren, Checklisten, Software, technischen Informationen, "
        "Schulungsmaterialien, Analysen und sonstigen Weber-eigenen Inhalten "
        "verbleiben im Eigentum von Weber oder des jeweiligen Rechteinhabers."
    ),
    "master.clause16.p2": (
        "Der Kunde kann die im Rahmen dieser Vereinbarung bereitgestellten "
        "Dokumentationen intern für den Betrieb und die Wartung seiner Ausrüstung "
        "verwenden."
    ),
    "master.clause16.p3": (
        "Es werden keine Rechte des geistigen Eigentums auf den Kunden übertragen, "
        "sofern nicht ausdrücklich schriftlich vereinbart."
    ),

    # 17. ASSIGNMENT AND SERVICE PARTNERS
    "master.clause17.title": "17. ABTRETUNG UND SERVICEPARTNER",
    "master.clause17.p1": (
        "Weber kann ihre Verpflichtungen durch Konzerngesellschaften von Weber oder "
        "qualifizierte und autorisierte Weber-Servicepartner wahrnehmen."
    ),
    "master.clause17.p2": (
        "Weber kann Rechte und Pflichten aus dieser Vereinbarung an eine andere "
        "Konzerngesellschaft von Weber abtreten, vorbehaltlich des geltenden Rechts."
    ),
    "master.clause17.p3": (
        "Der Kunde darf diese Vereinbarung nicht ohne vorherige schriftliche "
        "Zustimmung von Weber an einen Dritten abtreten; eine solche Zustimmung wird "
        "nicht unbillig verweigert, wenn die Fortführung der Vertragsbeziehung "
        "kommerziell und technisch möglich ist."
    ),

    # 18. GOVERNING LAW AND JURISDICTION
    "master.clause18.title": "18. ANWENDBARES RECHT UND GERICHTSSTAND",
    "master.clause18.law": "Anwendbares Recht",
    "master.clause18.jurisdiction": "Gerichtsstand",
    "master.clause18.p1": (
        "Die vorstehenden Bestimmungen sind jeweils den zwingenden Vorschriften des "
        "geltenden Rechts unterworfen."
    ),

    # 19. GENERAL PROVISIONS
    "master.clause19.title": "19. ALLGEMEINE BESTIMMUNGEN",
    "master.clause19.p1": (
        "Wenn eine Bestimmung dieser Vereinbarung unwirksam oder nicht durchsetzbar "
        "ist, bleiben die übrigen Bestimmungen unberührt."
    ),
    "master.clause19.p2": (
        "Die Nichtausübung eines vertraglichen Rechts durch eine der Parteien stellt "
        "keinen Verzicht auf dieses Recht dar."
    ),
    "master.clause19.p3": (
        "Diese Vereinbarung und ihre zutreffenden Anhänge bilden die Vereinbarung "
        "zwischen den Parteien hinsichtlich der hier beschriebenen Guardian-Leistungen "
        "und ersetzen frühere Angebote oder Verständigungen, die sich speziell auf "
        "denselben Leistungsumfang beziehen, sofern sie nicht ausdrücklich einbezogen "
        "werden."
    ),
    "master.clause19.p4": "Änderungen sind schriftlich vorzunehmen.",
    "master.clause19.p5": (
        "Elektronische Signaturen können verwendet werden, soweit sie gesetzlich "
        "zulässig sind, und haben die gleiche Wirkung wie handschriftliche Signaturen."
    ),

    # Annex 1 - Equipment & Commercial Schedule
    "annex1.title": "ANHANG 1 - AUSRÜSTUNG UND KONDITIONEN",
    "annex1.info.title": "1. Vertragsinformationen",
    "annex1.info.customer": "Kunde",
    "annex1.info.customer_no": "Kundennr.",
    "annex1.info.site": "Standort",
    "annex1.info.agreement_no": "Vereinbarungs-Nr.",
    "annex1.info.start_date": "Vertragsbeginn",
    "annex1.info.term": "Anfängliche Laufzeit",
    "annex1.info.billing": "Abrechnungshäufigkeit",
    "annex1.info.currency": "Währung",
    "annex1.equipment.title": "2. Erfasste Ausrüstung",
    "annex1.equipment.intro": (
        "Nur die nachstehend aufgeführte Ausrüstung und Maschinenmodule sind durch "
        "die Guardian-Leistungen abgedeckt."
    ),
    "annex1.equipment.h_line": "Produktionslinie",
    "annex1.equipment.h_machine": "Maschine",
    "annex1.equipment.h_serial": "Seriennummer",
    "annex1.equipment.h_type": "Typ",
    "annex1.equipment.h_modules": "Enthaltene Module / Komponenten",
    "annex1.equipment.h_frequency": "Servicefrequenz",
    "annex1.modules.title": "3. Ausgewählte Guardian-Module",
    "annex1.modules.intro": "Die folgenden Guardian-Module sind Bestandteil dieser Vereinbarung:",
    "annex1.modules.outro": (
        "Nur die Anhänge der oben ausgewählten Module werden beigefügt und sind "
        "Bestandteil der Vereinbarung."
    ),
    "annex1.summary.title": "4. Kommerzielle Übersicht",
    "annex1.summary.h_item": "Kommerzielle Position",
    "annex1.summary.h_amount": "Betrag",
    "annex1.summary.travel": "Anfahrt / Aufwendungen",
    "annex1.summary.kit": "Ersatzteile / Wartungs-Kit",
    "annex1.summary.discount": "Guardian-Rabatt",
    "annex1.summary.total": "GESAMTVERTRAGSWERT",
    "annex1.summary.vat_note": (
        "Alle Beträge verstehen sich zzgl. der gesetzlichen Mehrwertsteuer, sofern "
        "nicht anders angegeben."
    ),
    "annex1.billing.title": "5. Abrechnung",
    "annex1.billing.frequency": "Abrechnungshäufigkeit",
    "annex1.billing.terms": "Zahlungsbedingungen",
    "annex1.billing.adjustment": "Preisanpassung",
    "annex1.billing.travel": "Anfahrtskonditionen",
    "annex1.billing.freight": "Frachtkonditionen",
    "annex1.special.title": "6. Besondere kommerzielle Konditionen",

    # Annex 2 - Maintenance & Inspection
    "annex2.title": "ANHANG 2 - WARTUNG UND INSPEKTION",
    "annex2.tagline": (
        "Inspektion, vorbeugende Wartung und Leistungen zum Maschinenzustand."
    ),
    "annex2.purpose.title": "1. Zweck",
    "annex2.purpose.p1": (
        "Das Modul Wartung und Inspektion dient der Beurteilung und Erhaltung des "
        "Zustands der in Anhang 1 bezeichneten Ausrüstung, der Identifizierung "
        "erforderlicher technischer Maßnahmen sowie der Unterstützung eines "
        "zuverlässigen Betriebs und der Wartungsplanung."
    ),
    "annex2.purpose.p2": (
        "Die genauen eingeschlossenen Tätigkeiten richten sich nach den in der "
        "Guardian-Konfiguration ausgewählten Optionen."
    ),
    "annex2.inspection.title": "2. Inspektion",
    "annex2.inspection.p1": (
        "Weber führt Inspektionen der ausgewählten Ausrüstung mit der in Anhang 1 "
        "angegebenen Frequenz durch."
    ),
    "annex2.inspection.p2": (
        "Eine Inspektion kann, soweit auf die ausgewählte Ausrüstung anwendbar, "
        "Folgendes umfassen:"
    ),
    "annex2.inspection.includes": [
        "Überprüfung des allgemeinen Maschinenzustands;",
        "Inspektion anhand der maschinen- oder modulspezifischen Checkliste von Weber;",
        "Überprüfung relevanter Sensoren und elektrischer Bauteile;",
        "Inspektion von Antrieben, Riemen und mechanischen Bauteilen;",
        "Inspektion pneumatischer Bauteile;",
        "Inspektion von Dichtungen und Maschinengehäusen;",
        "Prüfung und Einstellung mechanisch beweglicher Bauteile, soweit angemessen erforderlich;",
        "Überprüfung der relevanten Maschineneinstellungen;",
        "Feststellung sichtbaren Verschleißes oder von Unregelmäßigkeiten;",
        "Feststellung offener Reparatur- oder Wartungsbedarfe;",
        "Besprechung bekannter Probleme mit dem verantwortlichen Personal des Kunden; und",
        "Funktionsprüfung nach der Inspektion, soweit angemessen.",
    ],
    "annex2.inspection.p3": (
        "Soweit sinnvoll und betrieblich möglich, kann Weber den Produktionsprozess "
        "anhand des Originalprodukts des Kunden überprüfen."
    ),
    "annex2.inspection.p4": (
        "Das Öffnen bestimmter geschützter Maschinenbereiche, wie etwa der Gehäuse "
        "von Wäge- oder Schneidköpfen, erfolgt, soweit technisch angemessen und "
        "vereinbart."
    ),
    "annex2.checklist.title": "3. Maschinen-Checkliste",
    "annex2.checklist.p1": (
        "Weber dokumentiert die Inspektion anhand der zutreffenden "
        "Weber-Inspektions-Checkliste."
    ),
    "annex2.checklist.p2": (
        "Die Checkliste erfasst die geprüften Elemente und deren bei der Inspektion "
        "festgestellten Zustand."
    ),
    "annex2.checklist.p3": (
        "Die Checkliste dient als technisches Serviceprotokoll und stellt keine "
        "Bestätigung dar, dass die Ausrüstung frei von Defekten ist oder dass kein "
        "künftiger Ausfall auftreten kann."
    ),
    "annex2.report.title": "4. Inspektionsbericht",
    "annex2.report.p1": (
        "Nach der Inspektion stellt Weber einen Inspektionsbericht bereit, der die "
        "wesentlichen Feststellungen zusammenfasst."
    ),
    "annex2.report.p2": "Der Bericht kann Folgendes umfassen:",
    "annex2.report.includes": [
        "Feststellungen zum Zustand;",
        "festgestellter Verschleiß;",
        "empfohlene Wartungen oder Reparaturen;",
        "empfohlene Ersatzteile;",
        "technische Beobachtungen;",
        "festgestellte Risiken, die weitere Aufmerksamkeit erfordern; und",
        "empfohlene Prioritäten oder nächste Maßnahmen.",
    ],
    "annex2.report.p3": (
        "Wo angemessen, kann Weber ein separates Angebot für empfohlene Teile, "
        "Reparaturen, Upgrades oder sonstige aus der Inspektion resultierende "
        "Tätigkeiten erstellen."
    ),
    "annex2.preventive.title": "5. Vorbeugende Wartung",
    "annex2.preventive.p1": (
        "Weber führt die für die Ausrüstung in Anhang 1 ausdrücklich definierten "
        "Tätigkeiten der vorbeugenden Wartung durch."
    ),
    "annex2.preventive.p2": "Die vorbeugende Wartung kann Folgendes umfassen:",
    "annex2.preventive.includes": [
        "mechanisches Einstellen;",
        "Schmieren;",
        "Reinigen technisch relevanter Bauteile;",
        "Austausch definierter Filter, Dichtungen oder Verschleißbauteile;",
        "Prüfung und Einstellung von Antrieben und Riemen;",
        "Prüfung pneumatischer Elemente;",
        "Prüfung elektrischer Bauteile und Sensoren; und",
        "sonstige maschinenspezifische Wartungsaufgaben, die im zutreffenden Weber-Wartungsplan aufgeführt sind.",
    ],
    "annex2.preventive.p3": (
        "Austauschteile, Verschleißteile und Verbrauchsmaterial sind nicht "
        "enthalten, sofern sie nicht ausdrücklich in Anhang 1 oder in einem "
        "vereinbarten Wartungs-Kit genannt sind."
    ),
    "annex2.kit.title": "6. Ersatzteile / Wartungs-Kit",
    "annex2.kit.p1": (
        "Das Wartungs-Kit enthält ausschließlich die im zutreffenden Angebot oder im "
        "Ausrüstungsplan ausdrücklich bezeichneten Teile."
    ),
    "annex2.kit.p2": "Der Preis des Kits wird in Anhang 1 separat ausgewiesen.",
    "annex2.kit.p3": (
        "Unverwendete Teile unterliegen den in Anhang 1 angegebenen Konditionen."
    ),
    "annex2.repairs.title": "7. Zusätzliche Wartung und Reparaturen",
    "annex2.repairs.p1": (
        "Reparaturen und Korrekturwartungen, die während einer Inspektion festgestellt "
        "werden, sind im Standard-Inspektionspreis nicht enthalten, sofern nicht "
        "gesondert anders angegeben."
    ),
    "annex2.repairs.p2": (
        "Wenn zusätzliche Arbeiten empfohlen werden, holt Weber die Genehmigung des "
        "Kunden ein oder erstellt ein separates Angebot."
    ),
    "annex2.frequency.title": "8. Inspektionsfrequenz",
    "annex2.frequency.value": "Frequenz",
    "annex2.frequency.planned": "Geplante Inspektionen pro Vertragsjahr",
    "annex2.frequency.p1": (
        "Der tatsächliche Zeitplan wird zwischen Weber und dem Kunden koordiniert."
    ),
    "annex2.hours.title": "9. Servicezeiten",
    "annex2.hours.p1": (
        "Die Leistungen werden üblicherweise in folgendem Zeitraum durchgeführt: "
        "{{Standard_Service_Hours}}"
    ),
    "annex2.hours.p2": (
        "Arbeiten, die außerhalb dieser Zeiten angefordert werden, können mit "
        "zusätzlichen Kosten verbunden sein."
    ),

    # Annex 3 - Service Support
    "annex3.title": "ANHANG 3 - SERVICE-SUPPORT",
    "annex3.tagline": (
        "Hotline, Remote-Support und priorisierte technische Reaktionszeit."
    ),
    "annex3.purpose.title": "1. Zweck",
    "annex3.purpose.p1": (
        "Das Modul Service-Support verschafft dem Kunden Zugang zum technischen "
        "Support von Weber für die von dieser Vereinbarung erfasste Ausrüstung."
    ),
    "annex3.purpose.p2": (
        "Das genaue Servicelevel hängt von den nachstehend ausgewählten Optionen ab."
    ),
    "annex3.hotline.title": "2. Standard-Hotline",
    "annex3.hotline.p1": (
        "Der Kunde hat während der zutreffenden Supportzeiten Zugang zur "
        "Service-Hotline von Weber."
    ),
    "annex3.hotline.hours": "Supportzeiten",
    "annex3.hotline.phone": "Telefon",
    "annex3.hotline.email": "E-Mail",
    "annex3.hotline.p2": (
        "Die Hotline bietet technischen Support der ersten Ebene und Koordination."
    ),
    "annex3.hotline.p3": (
        "Wenn das Problem über die Hotline nicht gelöst werden kann, kann Weber "
        "Remote-Support, einen Vor-Ort-Serviceeinsatz, Austauschteile oder sonstige "
        "technische Maßnahmen empfehlen."
    ),
    "annex3.hotline.p4": (
        "Vor-Ort-Service ist nicht allein dadurch eingeschlossen, dass "
        "Standard-Hotline-Support vorhanden ist, sofern es nicht ausdrücklich in "
        "Anhang 1 angegeben ist."
    ),
    "annex3.remote.title": "3. Remote-Support",
    "annex3.remote.p1": (
        "Soweit technisch verfügbar und vom Kunden autorisiert, kann Weber "
        "Remote-Diagnose und technischen Support bereitstellen."
    ),
    "annex3.remote.p2": (
        "Der Kunde stellt die Netzwerkverbindungen, den VPN-Zugang, die "
        "Benutzerautorisierung und die sonstigen technischen Bedingungen bereit, die "
        "für den Fernzugang angemessen erforderlich sind."
    ),
    "annex3.remote.p3": "Remote-Support kann Folgendes umfassen:",
    "annex3.remote.includes": [
        "Remote-Fehleranalyse;",
        "Überprüfung des Maschinenstatus oder von Diagnoseinformationen;",
        "Unterstützung bei Parameter- oder Konfigurationsprüfungen;",
        "Unterstützung des Wartungspersonals des Kunden; und",
        "Empfehlungen für weitere Maßnahmen.",
    ],
    "annex3.remote.p4": (
        "Remote-Support garantiert nicht, dass ein Fehler ohne einen "
        "Vor-Ort-Eingriff behoben werden kann."
    ),
    "annex3.priority.title": "4. Priorisierte Reaktion",
    "annex3.priority.p1": (
        "Anfragen bezüglich der von dieser Vereinbarung erfassten Ausrüstung werden "
        "innerhalb der Serviceorganisation von Weber im Vergleich zu standardmäßigen "
        "Nichtvertragsanfragen priorisiert behandelt, vorbehaltlich der Verfügbarkeit "
        "von Technikern und des zutreffenden Servicelevels."
    ),
    "annex3.priority.target": "Ziel-Erstreaktion",
    "annex3.priority.p2": (
        "Die priorisierte Reaktion bezieht sich auf die Priorisierung der "
        "Supportanfrage. Sie stellt keine garantierte Reparaturzeit, keine "
        "garantierte Maschinenverfügbarkeit und keine garantierte Vor-Ort-"
        "Ankunftszeit dar, sofern nicht ausdrücklich in Anhang 1 anders angegeben."
    ),

    # Annex 4 - Parts & Availability
    "annex4.title": "ANHANG 4 - ERSATZTEILE UND VERFÜGBARKEIT",
    "annex4.tagline": (
        "Kommerzielle Ersatzteil-Konditionen, priorisierte Behandlung und empfohlene "
        "Bestände."
    ),
    "annex4.purpose.title": "1. Zweck",
    "annex4.purpose.p1": (
        "Das Modul Ersatzteile und Verfügbarkeit unterstützt die strukturierte "
        "Ersatzteilplanung und den Zugang zu Original-Ersatzteilen von Weber für die "
        "von dieser Vereinbarung erfasste Ausrüstung."
    ),
    "annex4.discount.title": "2. Ersatzteil-Rabatt",
    "annex4.discount.p1": (
        "Der Kunde erhält den folgenden Rabatt auf die in Betracht kommenden "
        "Original-Ersatzteile von Weber für die durch die Guardian-Vereinbarung "
        "erfasste Ausrüstung:"
    ),
    "annex4.discount.amount": "Guardian-Ersatzteil-Rabatt {{Parts_Discount}} %",
    "annex4.discount.p2": (
        "Der Rabatt gilt für Original-Ersatzteile von Weber, sofern nicht anders "
        "angegeben."
    ),
    "annex4.discount.p3": "Folgendes kann ausgeschlossen werden:",
    "annex4.discount.excluded": [
        "Austauschteile im Tauschverfahren;",
        "Klingen;",
        "Artikel zu Sonderpreisen;",
        "Produkte Dritter;",
        "Fracht- und Expresskosten;",
        "Leistungen und Arbeitsleistung; und",
        "Artikel, die bereits einem anderen Sonderpreis oder Rabatt unterliegen.",
    ],
    "annex4.discount.p4": (
        "Rabatte sind nicht kumulierbar, sofern nicht ausdrücklich vereinbart."
    ),
    "annex4.handling.title": "3. Priorisierte Behandlung",
    "annex4.handling.p1": (
        "Ersatzteil-Anfragen und -Bestellungen bezüglich der von dieser Vereinbarung "
        "erfassten Ausrüstung werden innerhalb der zutreffenden "
        "Ersatzteilorganisation von Weber priorisiert behandelt."
    ),
    "annex4.handling.p2": (
        "Die priorisierte Behandlung umfasst eine beschleunigte interne Bearbeitung, "
        "soweit angemessen möglich."
    ),
    "annex4.handling.p3": (
        "Sie stellt keine garantierte Lieferzeit dar, wenn das angeforderte Teil "
        "nicht vorrätig ist oder wenn die Lieferung von externen Lieferanten, der "
        "Produktion oder dem Transport abhängt."
    ),
    "annex4.parts_list.title": "4. Empfohlene Ersatzteilliste",
    "annex4.parts_list.p1": (
        "Weber stellt, soweit technisch und kommerziell verfügbar, eine empfohlene "
        "Ersatzteilliste für die ausgewählte Ausrüstung bereit."
    ),
    "annex4.parts_list.categories": [
        "A - Lokal / sofort verfügbare Artikel: Teile, die normalerweise bei der zuständigen Organisation von Weber verfügbar sind.",
        "B - Zentrallager-Artikel: Teile, die normalerweise im Zentrallager von Weber verfügbar sind.",
        "C - Empfohlene Kundenvorrats-Artikel: kritische oder risikoreichere Ersatzteile, die Weber dem Kunden zur lokalen Vorratshaltung empfiehlt.",
        "D - Verschleißteile: Teile, die je nach Nutzung einen Austausch erfordern.",
        "E - Fertigung nach Bestellung / langfristige Teile: Teile, die normalerweise nicht auf Lager sind und eine Fertigung oder längere Beschaffungszeiten erfordern können.",
    ],
    "annex4.parts_list.p2": (
        "Die empfohlene Ersatzteilliste ist eine Empfehlung auf Basis der verfügbaren "
        "Maschinenkonfiguration und Serviceinformationen. Sie ist keine Garantie, "
        "dass jedes mögliche Ausfallszenario abgedeckt ist."
    ),
    "annex4.delivery.title": "5. Lieferbedingungen",
    "annex4.delivery.p1": (
        "Die Lagerverfügbarkeit und die Lieferbedingungen richten sich nach Anhang 1."
    ),
    "annex4.delivery.condition": "Standard-Lieferbedingung",
    "annex4.delivery.threshold": "Frachtfreigrenze",
    "annex4.delivery.courier": "Express-/Kurierkosten",
    "annex4.delivery.courier.value": (
        "Wird separat berechnet, sofern nicht anders vereinbart."
    ),

    # Annex 5 - Blade Solutions
    "annex5.title": "ANHANG 5 - KLINGENLÖSUNGEN",
    "annex5.tagline": (
        "Konditionen, Verfügbarkeit und technischer Support für die Klingenprogramme "
        "von Weber."
    ),
    "annex5.intro": (
        "Das Modul Klingenlösungen unterstützt die richtige Auswahl, Verfügbarkeit, "
        "Nutzung und Verwaltung der Weber-Klingen, einschließlich des Prinzips "
        "„Richtige Klinge, richtige Anwendung“."
    ),
    "annex5.discount.title": "1. Klingenrabatt",
    "annex5.discount.p1": (
        "Der Kunde erhält den folgenden Guardian-Rabatt auf die in Betracht "
        "kommenden Klingen von Weber:"
    ),
    "annex5.discount.amount": "Klingenrabatt {{Blade_Discount}} %",
    "annex5.discount.p2": (
        "Die geltenden Klingen, Kundenstandorte, Maschinen, zugesagten Mengen und "
        "etwaige Sonderpreise werden nach Bedarf im Konditionenplan aufgeführt."
    ),
    "annex5.discount.p3": (
        "Klingenrabatte kumulieren nicht mit anderen Klingenaktionen oder "
        "Sonderpreisen, sofern nicht ausdrücklich vereinbart."
    ),
    "annex5.discount.p4": (
        "Wenn Klingenpreise mit fester Laufzeit vereinbart werden, werden die "
        "geltende Laufzeit und die Preisbedingungen in Anhang 1 angegeben."
    ),
    "annex5.stock.title": "2. Bestandsvereinbarung",
    "annex5.stock.p1": (
        "Weber und der Kunde können ein vereinbartes Klingenbestandskonzept auf "
        "Basis des erwarteten Verbrauchs festlegen."
    ),
    "annex5.stock.p2": "Die Bestandsvereinbarung definiert, soweit zutreffend:",
    "annex5.stock.defines": [
        "Klingenreferenzen;",
        "vereinbarte Bestandsmenge;",
        "Mindestbestand;",
        "Maximalbestand;",
        "erwarteter Jahresverbrauch;",
        "Auffüllverfahren;",
        "Lagerort;",
        "Eigentum am Bestand;",
        "Lieferbedingungen; und",
        "Behandlung von veralteten oder unverwendeten Beständen.",
    ],
    "annex5.stock.p3": (
        "Der Kunde stellt angemessen genaue Verbrauchsinformationen bereit und "
        "informiert Weber über wesentliche Änderungen bei der Produktion oder der "
        "Klingennachfrage."
    ),
    "annex5.stock.p4": (
        "Die Bestandsvereinbarung dient der Verbesserung der Verfügbarkeit, stellt "
        "aber keine unbedingte Garantie für eine ununterbrochene Lieferung in "
        "Umständen dar, die außerhalb der angemessenen Kontrolle von Weber liegen."
    ),
    "annex5.sharpening.title": "3. Bewertung des Schleifprozesses",
    "annex5.sharpening.p1": (
        "Weber bewertet nach Vereinbarung den Schleifprozess und die "
        "Prozessfähigkeit beim Schleifen der Klingen des Kunden."
    ),
    "annex5.sharpening.p2": "Die Bewertung kann Folgendes umfassen:",
    "annex5.sharpening.includes": [
        "Schleifeinrichtung;",
        "Schleifprozess;",
        "Handhabung der Klingen;",
        "Zustand der Klingen;",
        "Schleifparameter;",
        "Wartungspraktiken;",
        "Klingenlagerung;",
        "Prozesskonstanz; und",
        "Verbesserungspotenziale.",
    ],
    "annex5.sharpening.p3": (
        "Weber kann nach der Bewertung Empfehlungen aussprechen."
    ),
    "annex5.sharpening.p4": (
        "Sofern nicht speziell eingeschlossen, sind die Umsetzung dieser "
        "Empfehlungen, Reparaturen oder Änderungen an der Schleifeinrichtung und "
        "zusätzliche Schulungen nicht enthalten."
    ),
    "annex5.application.title": "4. Prüfung der Klingenanwendung",
    "annex5.application.p1": (
        "Soweit im ausgewählten Klingenprogramm enthalten, kann Weber die "
        "Klingen-Produkt-Kombination mit dem Ziel überprüfen, das Prinzip „Richtige "
        "Klinge, richtige Anwendung“ zu unterstützen."
    ),
    "annex5.application.p2": (
        "Empfehlungen können Produktart, Schneidebedingungen, Maschinenkonfiguration, "
        "Klingengeometrie und betriebliche Anforderungen berücksichtigen."
    ),

    # Annex 6 - Training & Optimization
    "annex6.title": "ANHANG 6 - SCHULUNG UND OPTIMIERUNG",
    "annex6.tagline": (
        "Bediener-Schulung, Wartungs-Schulung, Linienoptimierung und EPIP-Audits."
    ),
    "annex6.intro": (
        "Das Modul Schulung und Optimierung bietet ausgewählte Tätigkeiten zur "
        "Verbesserung des Maschinenbetriebs, der Wartungskompetenz und der "
        "Produktionsleistung."
    ),
    "annex6.operator.title": "1. Bedienerschulung",
    "annex6.operator.p1": (
        "Weber bietet bedienerorientierte Schulungen für die ausgewählte Ausrüstung."
    ),
    "annex6.operator.p2": (
        "Der Schulungsinhalt kann je nach Maschine und vereinbarten Zielen Folgendes "
        "umfassen:"
    ),
    "annex6.operator.includes": [
        "richtiger Maschinenbetrieb;",
        "grundlegende Maschineneinstellungen;",
        "Betriebsroutinen;",
        "Produktwechsel;",
        "Prüfungen auf Bedienerebene;",
        "Aspekte der Reinigung und Inspektion;",
        "Erkennung auffälligen Maschinenverhaltens; und",
        "bewährte Betriebspraktiken.",
    ],
    "annex6.operator.quantity": "Anzahl der Schulungseinheiten / Tage",
    "annex6.operator.p3": (
        "Die Schulung wird für die vom Kunden benannten Personen durchgeführt."
    ),
    "annex6.operator.p4": (
        "Sofern nicht ausdrücklich anders angegeben, stellt die Schulung keine "
        "formale Zertifizierung des Personals des Kunden dar."
    ),
    "annex6.maintenance.title": "2. Wartungsschulung",
    "annex6.maintenance.p1": (
        "Weber bietet technische Schulungen für das Wartungspersonal des Kunden."
    ),
    "annex6.maintenance.p2": "Die Schulung kann Folgendes umfassen:",
    "annex6.maintenance.includes": [
        "Maschinenbau und Funktionsprinzipien;",
        "vorbeugende Wartung;",
        "Inspektionspunkte;",
        "Identifizierung von Verschleißteilen;",
        "Methodik der Fehlerbehebung;",
        "mechanisches Einstellen;",
        "relevante elektrische oder pneumatische Bauteile;",
        "Wartungsdokumentation; und",
        "empfohlene Wartungspraktiken.",
    ],
    "annex6.maintenance.quantity": "Anzahl der Schulungseinheiten / Tage",
    "annex6.optimization.title": "3. Linienoptimierung",
    "annex6.optimization.p1": (
        "Weber führt eine vereinbarte Überprüfung der ausgewählten Produktionslinie "
        "mit dem Ziel durch, Verbesserungspotenziale für die Leistung zu "
        "identifizieren."
    ),
    "annex6.optimization.p2": "Die Tätigkeit kann Folgendes umfassen:",
    "annex6.optimization.includes": [
        "Überprüfung der Maschinenparameter;",
        "Beobachtung der Produktion;",
        "Analyse der Betriebsbedingungen;",
        "Überprüfung der Linieninteraktion;",
        "Identifizierung von Leistungseinschränkungen;",
        "Einstellen ausgewählter Parameter, soweit angemessen; und",
        "Empfehlungen für weitere Verbesserungen.",
    ],
    "annex6.optimization.quantity": "Anzahl der Optimierungstätigkeiten",
    "annex6.optimization.p3": (
        "Die Linienoptimierung ist keine Garantie für eine bestimmte Ausbringung, "
        "Ausbeute, OEE, Giveaway-Reduzierung oder sonstige Leistungsverbesserung, "
        "sofern nicht ausdrücklich schriftlich eine spezielle Leistungszusage "
        "vereinbart wird."
    ),
    "annex6.epip.title": "4. EPIP-Audit",
    "annex6.epip.p1": (
        "Weber führt ein EPIP-Audit an der in Anhang 1 bezeichneten Ausrüstung oder "
        "den bezeichneten Linien durch."
    ),
    "annex6.epip.p2": (
        "Das Audit umfasst eine Bewertung der ausgewählten Linie und einen Bericht "
        "mit den relevanten Feststellungen, Potenzialen und Prioritätsmaßnahmen."
    ),
    "annex6.epip.p3": (
        "Soweit zutreffend, werden die Ergebnisse mit dem Kunden besprochen und in "
        "den laufenden Guardian-Aktionsplan eingebracht."
    ),
    "annex6.epip.quantity": "Anzahl der EPIP-Audits",
    "annex6.epip.lines": "Erfasste Linien",
    "annex6.epip.p4": (
        "Korrekturmaßnahmen, Reparaturen, Upgrades oder Teile, die aus dem Audit "
        "resultieren, sind nicht enthalten, sofern nicht ausdrücklich angegeben."
    ),
    "annex6.followup.title": "5. Nachbereitung",
    "annex6.followup.p1": (
        "Soweit im ausgewählten Paket enthalten, kann Weber vor und nach den "
        "ausgewählten Tätigkeiten Follow-up-Besprechungen oder -Anrufe durchführen, "
        "um Folgendes zu überprüfen:"
    ),
    "annex6.followup.items": [
        "vereinbarte Ziele;",
        "durchgeführte Tätigkeiten;",
        "festgestellte Auswirkungen;",
        "offene Maßnahmen;",
        "technische Prioritäten; und",
        "nächste Maßnahmen.",
    ],

    # Annex 7 - Digital Services
    "annex7.title": "ANHANG 7 - DIGITALE DIENSTLEISTUNGEN",
    "annex7.tagline": (
        "Factory Cockpit, Leistungsüberprüfung, MRO-Überprüfung und dedizierte "
        "Kundenbetreuung."
    ),
    "annex7.intro": (
        "Das Modul Digitale Dienstleistungen bietet ausgewählte Leistungen für "
        "digitales Monitoring, Leistungsüberprüfungen und Kundenbetreuung."
    ),
    "annex7.cockpit.title": "1. Factory Cockpit",
    "annex7.cockpit.p1": (
        "Wenn die ausgewählte Ausrüstung technisch kompatibel ist, unterstützt "
        "Weber die Anbindung der vereinbarten Ausrüstung an Factory Cockpit gemäß "
        "den zutreffenden Konditionen des digitalen Dienstes."
    ),
    "annex7.cockpit.lines": "Verbundene Linie(n)",
    "annex7.cockpit.p2": (
        "Factory Cockpit kann genutzt werden, um verfügbare Maschinenleistungsdaten "
        "zu erfassen und darzustellen, mit dem Ziel der Leistungsüberprüfung und "
        "Optimierung."
    ),
    "annex7.cockpit.p3": (
        "Der Kunde stellt die Netzwerkinfrastruktur, Berechtigungen und den "
        "technischen Zugang bereit, die für die Anbindung angemessen erforderlich "
        "sind."
    ),
    "annex7.cockpit.p4": (
        "Die Verfügbarkeit bestimmter Daten hängt von der Maschinengeneration, der "
        "installierten Software und der Konnektivität der jeweiligen Ausrüstung ab."
    ),
    "annex7.cockpit.p5": (
        "Etwaige separate Softwarelizenzen oder die für Factory Cockpit geltenden "
        "digitalen Dienst-Konditionen bleiben weiterhin anwendbar."
    ),
    "annex7.performance.title": "2. Leistungsüberprüfung",
    "annex7.performance.p1": (
        "Weber und der Kunde führen regelmäßige Überprüfungen der verfügbaren "
        "Leistungsdaten der Ausrüstung durch."
    ),
    "annex7.performance.frequency": "Überprüfungsfrequenz",
    "annex7.performance.p2": "Die Überprüfung kann Folgendes umfassen:",
    "annex7.performance.includes": [
        "ausgewählte Maschinen-KPIs;",
        "Leistungstrends;",
        "wiederkehrende technische Beobachtungen;",
        "identifizierte Verbesserungspotenziale;",
        "durchgeführte Tätigkeiten;",
        "offene Maßnahmen; und",
        "Prioritäten für den nächsten Überprüfungszeitraum.",
    ],
    "annex7.performance.p3": (
        "Die Parteien können kundenspezifische KPIs und Zielwerte vereinbaren."
    ),
    "annex7.performance.p4": (
        "Sofern nicht ausdrücklich anders vereinbart, sind solche Zielwerte "
        "Managementziele und keine vertraglichen Leistungsgarantien."
    ),
    "annex7.mro.title": "3. MRO-Überprüfung",
    "annex7.mro.p1": (
        "Weber überprüft regelmäßig die verfügbaren Informationen zu Wartungs-, "
        "Reparatur- und Betriebskosten (MRO) der erfassten Ausrüstung."
    ),
    "annex7.mro.p2": "Die Überprüfung kann Folgendes umfassen:",
    "annex7.mro.includes": [
        "Ausgaben für Ersatzteile;",
        "Serviceausgaben;",
        "Ausgaben für Klingen, soweit relevant;",
        "historische Wartungsaktivität;",
        "Informationen zur Installationsbasis;",
        "Wartungstrends;",
        "identifizierte Kostentreiber; und",
        "Vergleich mit einem vereinbarten MRO-Planungsziel.",
    ],
    "annex7.mro.frequency": "Frequenz der MRO-Überprüfung",
    "annex7.mro.target": "Vereinbartes MRO-Ziel, falls zutreffend",
    "annex7.mro.p3": (
        "Zweck der Überprüfung ist es, die Wartungsplanung zu unterstützen und "
        "Verbesserungspotenziale zu identifizieren. Sie stellt keine Garantie dar, "
        "dass ein bestimmtes MRO-Ausgabenniveau erreicht wird."
    ),
    "annex7.account.title": "4. Dediziertes Kundenbetreuungsteam",
    "annex7.account.p1": (
        "Weber benennt eine Guardian-Kundenbetreuungsstruktur für den Kunden."
    ),
    "annex7.account.p2": (
        "Das Team koordiniert die ausgewählten Guardian-Aktivitäten und dient als "
        "zentraler Ansprechpartner für die regelmäßige Programmüberprüfung."
    ),
    "annex7.account.p3": "Der Betreuungsprozess kann Folgendes umfassen:",
    "annex7.account.includes": [
        "geplante Kundenüberprüfungen;",
        "Koordination zwischen den relevanten Funktionen von Weber;",
        "Überprüfung offener Maßnahmen;",
        "Überprüfung anstehender Serviceaktivitäten;",
        "Überprüfung des Ersatzteil- und Klingenbedarfs;",
        "Gespräche zur Leistung;",
        "Optimierungspotenziale; und",
        "Nachverfolgung der vereinbarten Maßnahmen.",
    ],
    "annex7.account.cadence": "Überprüfungsturnus",
    "annex7.account.p4": (
        "Das dedizierte Betreuungsteam ergänzt, ersetzt aber nicht die normalen "
        "operativen Kanäle von Weber für dringende Serviceanfragen, "
        "Ersatzteilbestellungen oder Notfall-Support."
    ),

    # Configuration Summary and Signatures
    "summary.title": "GUARDIAN-KONFIGURATIONSÜBERSICHT",
    "summary.intro": (
        "Die folgende Übersicht bestätigt die vom Kunden im Rahmen dieser "
        "Vereinbarung erworbene Guardian-Konfiguration."
    ),
    "summary.customer": "Kunde",
    "summary.site": "Standort",
    "summary.start": "Vertragsbeginn",
    "summary.term": "Vertragslaufzeit",
    "summary.equipment": "Erfasste Ausrüstung",
    "summary.equipment.value": (
        "{{Number_Of_Machines}} Maschinen / {{Number_Of_Lines}} Produktionslinien"
    ),
    "summary.value": "Jahres- / Vertragswert",
    "summary.scope.title": "GUARDIAN DES KUNDEN",
    "summary.scope.h_module": "Guardian-Modul",
    "summary.scope.h_scope": "Ausgewählter Umfang",
    "summary.signatures.title": "UNTERSCHRIFTEN",
    "summary.signatures.intro": (
        "Mit der Unterzeichnung dieser Vereinbarung bestätigen die Parteien ihre "
        "Annahme der Rahmenvereinbarung und aller in Anhang 1 als zutreffend "
        "bezeichneten Anhänge."
    ),
    "summary.signatures.company": "Unternehmen",
    "summary.signatures.customer": "Für den Kunden",
    "summary.signatures.weber": "Für Weber",
    "summary.signatures.name": "Name",
    "summary.signatures.position": "Funktion",
    "summary.signatures.place": "Ort",
    "summary.signatures.date": "Datum",
    "summary.signatures.signature": "Unterschrift",
}
