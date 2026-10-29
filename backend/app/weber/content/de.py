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
    "module.customer_service": "Kundenservice",
    "module.spare_parts": "Ersatzteile und Verfügbarkeit",
    "module.academy": "Akademie",
    "module.blade_solutions": "Messer- und Klingenlösungen",
    "module.optimization": "Optimierung und Performance",
    "module.digital_services": "Digitale Services",

    # Always-on rows of the annex/summary tables
    "annex1.summary.inspection": "Inspektion und Wartung",
    "summary.scope.inspection": "Inspektion und Wartung",

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
    "master.clause0.title": "0. BEGRIFFSBESTIMMUNGEN",
    "master.clause0.intro": "Die in diesem Vertrag verwendeten Begriffe haben folgende Bedeutung:",
    "master.clause0.machine.term": "Maschine / Module",
    "master.clause0.machine.definition": (
        "Eine funktionelle Einheit, Ausrüstung oder Anlage, auf die sich die aus diesem "
        "Vertrag erbrachten Leistungen beziehen."
    ),
    "master.clause0.inspection.term": "Inspektion",
    "master.clause0.inspection.definition": (
        "Die Feststellung und Bewertung des tatsächlichen Zustands einer Maschine bzw. "
        "eines Moduls, einschließlich der Ermittlung der Ursachen von Verschleiß und der "
        "daraus folgenden Konsequenzen für die künftige Nutzung."
    ),
    "master.clause0.maintenance.term": "Wartung",
    "master.clause0.maintenance.definition": (
        "Maßnahmen, die darauf gerichtet sind, die Verschlechterung vorhandener "
        "Verschleißteile hinauszuzögern („vorbeugende Wartung“), insbesondere durch "
        "Einstellungen oder durch den Austausch von Filtern, Dichtungen und "
        "Schmierstoffen, technische Reinigung usw."
    ),
    "master.clause0.replacement.term": "Instandsetzung",
    "master.clause0.replacement.definition": (
        "Jede Maßnahme, um eine Maschine bzw. ein Modul in den vereinbarten Zustand "
        "zurückzuversetzen, insbesondere durch den Austausch von Teilen, einschließlich "
        "Verschleißteilen. Auch Maßnahmen zur Erhaltung des vereinbarten Zustands "
        "außerhalb der Wartungsleistungen sind Bestandteil der Instandsetzung."
    ),

    # I. Purpose of the contract
    "master.clause1.title": "I. ZWECK DES VERTRAGS",
    "master.clause1.p1": (
        "(0) Gegenstand des Inspektionsvertrags ist die Inspektion der in Anhang 1 "
        "aufgeführten Maschinen und Module, wobei diese Leistungen auf Grundlage einer "
        "festen Vergütung (Anhang 1) in Rechnung gestellt werden. Die Wartung der "
        "Maschinen und Komponenten wird nach Aufwand und gemäß den jeweils geltenden "
        "Sätzen berechnet."
    ),
    "master.clause1.p2": (
        "Zweck des Vertrags ist es, die Nutzungsdauer der Maschinen und Module zu "
        "verlängern, Stillstände zu reduzieren und die Wartungskosten durch eine "
        "angemessene Inspektion und Wartung unter Kontrolle zu halten."
    ),
    "master.clause1.p3": (
        "(1) Im Rahmen dieses Vertrags übernimmt der Auftragnehmer für die aufgeführten "
        "Maschinen und Module folgende Leistungen:"
    ),
    "master.clause1.services": [
        "Hotline-Service",
        "Lieferung von Ersatzteilen",
        "Wartung",
        "Kontrollbesuch nach der Wartung",
        "Klingenprogramm (Lagerhaltung)",
    ],
    "master.clause1.p4": "(2) Die Leistung des Auftragnehmers umfasst in den folgenden Fällen:",
    "master.clause1.p5": "(2.1) Bei Kontaktaufnahme mit der Hotline oder dem telefonischen Servicezentrum:",
    "master.clause1.hotline": [
        "Hotline-Service von Montag bis Freitag, 07:30 bis 17:30 Uhr.",
        "Telefon: 938 23 32 33",
    ],
    "master.clause1.p6": (
        "(2.2) Vertrieb von Ersatzteilen: Lieferung der auf Lager verfügbaren "
        "Ersatzteile (auf der Iberischen Halbinsel und in Deutschland) innerhalb von "
        "24 bis 48 Stunden. Ist das angeforderte Ersatzteil nicht auf Lager, wird es "
        "bestellt und so bald wie möglich geliefert."
    ),
    "master.clause1.p7": "(2.3) Inspektion: Inspektion der Maschinen gemäß Anhang 1.",
    "master.clause1.p8": (
        "(2.4) Wartung: Durchführung von Reparaturen gemäß Punkt I.3 des Vertrags."
    ),
    "master.clause1.p9": (
        "(2.5) Klingen-Lagerhaltungsprogramm: 5 % Rabatt ab der ersten Schachtel mit 3 "
        "Einheiten, gemäß Anhang 2."
    ),
    "master.clause1.p10": (
        "(3) Alle Wartungsarbeiten oder sonstigen Leistungen (beispielsweise Änderungen "
        "an Maschinen und Anlagen), die sich aus der Inspektion ergeben, bedürfen eines "
        "gesonderten Bestellauftrags und werden auf Grundlage eines zusätzlichen "
        "Angebots in Rechnung gestellt."
    ),
    "master.clause1.p11": (
        "(4) Die Anzahl der in Anhang 1 enthaltenen Maschinen sowie der Umfang der aus "
        "diesem Vertrag resultierenden Leistungen werden von den Vertragsparteien im "
        "letzten Quartal des Vertrags überprüft."
    ),
    "master.clause1.p12": (
        "(5) Änderungen der Anzahl der in die Vereinbarung einbezogenen Maschinen sowie "
        "Änderungen des Leistungsumfangs durch den Auftraggeber sind schriftlich "
        "festzuhalten und Anhang 1 entsprechend anzupassen. Diese Leistungsvereinbarung "
        "gilt für die 12 Monate der Vertragslaufzeit oder bis zur Beendigung des "
        "Vertrags."
    ),
    "master.clause1.p13": (
        "(6) Kontrollbesuch, der durchzuführen ist, sofern die anschließende Wartung "
        "durch den Auftragnehmer erfolgt."
    ),

    # II. Price and payment
    "master.clause2.title": "II. PREIS UND ZAHLUNG",
    "master.clause2.p1": (
        "(1) Der Preis der Inspektionsarbeiten wird gemäß Anhang 1 berechnet. Die "
        "Bemessungsgrundlage ergibt sich aus dem Maschinenmodell und den gemäß Punkt I "
        "des Vertrags ausgewählten Modulen."
    ),
    "master.clause2.p2": (
        "(2) Der Preis für die Module „Inspektion“ und „Wartung“ umfasst Reise-, "
        "Transport-, Unterkunfts- und Verpflegungskosten. Ausgenommen sind mit dem "
        "Auftraggeber vereinbarte Ausnahmen."
    ),
    "master.clause2.p3": (
        "(3) Ausgetauschte Teile sind dem Auftraggeber zur Kontrolle vorzulegen."
    ),
    "master.clause2.p4": (
        "(4) Der Preis für die Arbeiten des Inspektionspersonals ist innerhalb von 30 "
        "Tagen nach Rechnungsstellung zu zahlen. Die Rechnungsstellung erfolgt nach "
        "Durchführung der Inspektion."
    ),
    "master.clause2.p5": (
        "(5) Der Auftragnehmer ist berechtigt, den Preis der Arbeiten gemäß Anhang 1 "
        "jährlich zu überprüfen. Er teilt dem Auftraggeber eine solche Überprüfung "
        "mindestens 3 Monate vor deren Wirksamwerden mit. Die Preisänderung gilt im "
        "folgenden Zahlungszeitraum."
    ),
    "master.clause2.p6": (
        "(6) Die Zurückbehaltung von Zahlungen oder die Aufrechnung wegen behaupteter "
        "Gegenansprüche des Auftraggebers wird nicht anerkannt."
    ),
    "master.clause2.p7": (
        "(7) Der Auftragnehmer gewährt einen Rabatt von 15 % auf "
        "Maschinenunterstützungsleistungen und einen Rabatt von höchstens 5 % auf "
        "Ersatzteile, nicht kumulierbar, wie in Anhang 1 angegeben."
    ),

    # III. Client participation and technical contribution
    "master.clause3.title": "III. MITWIRKUNG UND TECHNISCHE BEISTELLUNG DES AUFTRAGGEBERS",
    "master.clause3.p1": "(1) Der Auftraggeber stellt sicher, dass:",
    "master.clause3.obligations": [
        "die Arbeiten zu den vereinbarten Zeiten und an den vereinbarten Maschinen "
        "pünktlich ausgeführt werden können, und gewährleistet den freien Zugang zu den "
        "Maschinen und Modulen.",
        "die Maschine betriebsbereit, verfügbar und sauber ist (ohne Produktrückstände).",
        "nach Abschluss der Arbeiten eine Funktionsprüfung mit den Originalprodukten des "
        "Kunden in ausreichender Menge durchgeführt werden kann.",
        "bestehende Störungen in den Maschinenzeichnungen vermerkt sind.",
        "die Produktion so organisiert ist, dass sie während der Inspektion angehalten "
        "werden kann.",
    ],
    "master.clause3.p2": (
        "(2.a) Der Auftraggeber trägt die Kosten, die dem Inspektionspersonal während "
        "der Inspektion und Wartung entstehen."
    ),
    "master.clause3.p3": (
        "Der Auftraggeber trifft die besonderen Maßnahmen, die für den Personen- und "
        "Sachschutz am Inspektions-/Wartungsort erforderlich sind. Er unterrichtet "
        "ferner das Personal des ausführenden Unternehmens über die besonderen "
        "Sicherheitsmaßnahmen, soweit diese für das Inspektions- und Wartungspersonal "
        "von Bedeutung sind. Der Auftraggeber teilt dem Auftragnehmer Verstöße des "
        "Personals gegen diese Sicherheitsvorschriften mit."
    ),
    "master.clause3.p4": (
        "(b) Der Auftraggeber verpflichtet sich, die Kosten der technischen Beistellung "
        "zu tragen, insbesondere Unterstützung, Werkstatt sowie Hilfsmittel wie Wasser "
        "und Strom einschließlich der erforderlichen Anschlüsse kostenlos "
        "bereitzustellen."
    ),
    "master.clause3.p5": (
        "(c) Um zu entscheiden, ob die Arbeiten ausgeführt und/oder die in Punkt I.3 "
        "genannten Teile während des Inspektionsintervalls ausgetauscht werden können, "
        "benennt der Auftraggeber eine Person mit Entscheidungsbefugnis."
    ),

    # IV. Compliance with contract deadlines
    "master.clause4.title": "IV. EINHALTUNG DER VERTRAGSFRISTEN",
    "master.clause4.p1": (
        "(1) Der Auftragnehmer verpflichtet sich, eine Inspektion innerhalb des in "
        "Anhang 1 vereinbarten Zeitintervalls durchzuführen."
    ),
    "master.clause4.p2": (
        "(2) Der Auftragnehmer teilt dem Auftraggeber den genauen Inspektionstermin "
        "mindestens 6 Wochen im Voraus mit, sofern nicht zwischen den Vertragsparteien "
        "ein konkreter Termin vereinbart wurde."
    ),
    "master.clause4.p3": (
        "(3) Der Auftragnehmer erbringt die Leistungen in folgenden Zeiträumen:"
    ),
    "master.clause4.service_periods": [
        "Inspektion und Wartung von Montag bis Freitag, 08:00 bis 18:00 Uhr.",
        "Ausgenommen nach gegenseitiger Vereinbarung.",
    ],
    "master.clause4.p4": (
        "(4) Kann der Auftraggeber oder der Auftragnehmer die Arbeiten am geplanten "
        "Termin nicht durchführen, teilen beide Parteien dies einander mindestens 2 "
        "Werktage im Voraus mit. Erscheint der Auftragnehmer nicht zum vereinbarten "
        "Termin, stellt der Auftragnehmer die Reisekosten für den nächsten Termin nicht "
        "in Rechnung; ist die Linie am vom Auftraggeber vereinbarten Termin nicht "
        "verfügbar, zahlt der Auftraggeber dem Auftragnehmer die entstandenen "
        "Reisekosten."
    ),
    "master.clause4.p5": (
        "(5) Verzögert sich die Inspektion/Wartung aufgrund von Umständen aus "
        "Arbeitsstreitigkeiten, insbesondere Streiks und Betriebsstilllegungen, oder "
        "aufgrund von Ereignissen, die dem Auftragnehmer nicht zuzurechnen sind, "
        "verlängert sich die Inspektion/Wartung entsprechend, sofern nachgewiesen werden "
        "kann, dass diese Hindernisse die Fertigstellung der Inspektion/Wartung "
        "erheblich beeinträchtigen. Dies gilt auch, wenn solche Umstände eintreten, "
        "nachdem der Auftragnehmer die im vorstehenden Absatz festgelegte "
        "Ankündigungsfrist versäumt hat."
    ),

    # V. Commencement and term
    "master.clause5.title": "V. BEGINN UND LAUFZEIT DES VERTRAGS",
    "master.clause5.p1": (
        "(1) Der Vertrag gilt ab der Unterzeichnung durch beide Parteien. Die Laufzeit "
        "des Vertrags beträgt 12 Monate und er kann von jeder Partei gekündigt werden."
    ),
    "master.clause5.p2": (
        "(2) Der Vertrag verlängert sich automatisch um weitere 12 Monate, sofern er "
        "nicht 3 Monate vor seinem Ende schriftlich gekündigt wird."
    ),

    # VI. Warranty and liability
    "master.clause6.title": "VI. GEWÄHRLEISTUNG UND HAFTUNG",
    "master.clause6.p1": (
        "(1) Wurde die Inspektion/Wartung nicht vollständig ausgeführt, überprüft oder "
        "berichtigt der Auftragnehmer diese kostenlos."
    ),
    "master.clause6.p2": (
        "(2) Der Auftragnehmer behebt kostenlos alle Schäden, die er oder seine "
        "Erfüllungsgehilfen an den zu wartenden Maschinen und Anlagen verursacht haben. "
        "Der Umfang der Instandsetzungspflicht ist auf das im Vertrag festgelegte "
        "jährliche Entgelt begrenzt."
    ),
    "master.clause6.p3": (
        "(3) Erfüllt der Auftragnehmer seine Pflicht zur Instandsetzung, Nachbesserung "
        "oder Schadensbehebung nicht, kann der Auftraggeber eine angemessene Nachfrist "
        "setzen. Verstreicht diese Frist aus Gründen, die der Auftragnehmer zu vertreten "
        "hat, ergebnislos, kann der Auftraggeber nach seiner Wahl eine Herabsetzung der "
        "Wartungs- und Inspektionsentgelte verlangen oder den Vertrag fristlos kündigen. "
        "Auftragnehmer und Auftraggeber vereinbaren ausdrücklich, dass der Auftragnehmer "
        "für Schäden nur haftet, wenn Vorsatz oder grobe Fahrlässigkeit seinerseits oder "
        "seitens seiner Erfüllungsgehilfen nachgewiesen werden kann. Insbesondere "
        "schließen die Parteien die Haftung für mittelbare Schäden oder Verluste "
        "ausdrücklich aus."
    ),
    "master.clause6.p4": (
        "(4) Sonstige Ansprüche des Auftraggebers bestehen nur bei Vorsatz oder grober "
        "Fahrlässigkeit. Darüber hinaus kann der Auftraggeber keine weiteren "
        "Aufrechnungsrechte gegenüber dem Auftragnehmer geltend machen, insbesondere "
        "kein Recht auf Schadensersatz oder sonstige Rechte wegen etwaiger "
        "Unannehmlichkeiten im Zusammenhang mit dem Inspektionsvertrag, gleich aus "
        "welchem Grund."
    ),
    "master.clause6.p5": (
        "(5) Der Auftragnehmer haftet nicht für Schäden oder Mängel, die durch "
        "Nicht-Originalteile verursacht werden."
    ),

    # VII. Limitation period
    "master.clause7.title": "VII. VERJÄHRUNG",
    "master.clause7.p1": (
        "Die Gewährleistungsansprüche des Auftraggebers verjähren zwölf Monate nach "
        "Abnahme der jeweiligen Inspektions-/Wartungsleistung. Die Gewährleistungsfrist "
        "verlängert sich um die Dauer der Nachbesserungsarbeiten."
    ),

    # VIII. Other provisions
    "master.clause8.title": "VIII. SONSTIGE BESTIMMUNGEN",
    "master.clause8.p1": (
        "(1) Dem Inspektions-/Wartungspersonal ist während der normalen "
        "Arbeitszeit/Servicezeit Zugang zu den Maschinen und Anlagen zu gewähren, damit "
        "es die angekündigten Inspektions- und Wartungsarbeiten durchführen kann. Der "
        "Auftraggeber erteilt alle erforderlichen Informationen über die in Anhang 1 "
        "genannten Maschinen und Module und stellt die entsprechende Dokumentation "
        "bereit."
    ),
    "master.clause8.p2": (
        "(2) Überträgt der Auftraggeber Maschinen und Anlagen auf Dritte, bleibt er zur "
        "Zahlung der Entgelte verpflichtet, sofern der Dritte nicht mit vorheriger "
        "Zustimmung des Auftragnehmers in den Vertrag eintritt. Der Auftragnehmer darf "
        "die Zustimmung nur aus sachlichen Gründen verweigern."
    ),
    "master.clause8.p3": (
        "(3) Der Auftragnehmer ist berechtigt, die aus diesem Vertrag übernommenen "
        "Rechte und Pflichten auf Dritte zu übertragen."
    ),
    "master.clause8.p4": (
        "(4) Zusatzvereinbarungen und Änderungen des Vertrags bedürfen der Schriftform."
    ),
    "master.clause8.p5": (
        "(5) Wird eine Bestimmung dieses Vertrags unwirksam, bleiben alle übrigen "
        "Bestimmungen oder Vereinbarungen wirksam."
    ),

    # IX. Place of jurisdiction
    "master.clause9.title": "IX. GERICHTSSTAND",
    "master.clause9.p1": (
        "Soweit gesetzlich zulässig, sind Erfüllungsort und Gerichtsstand der Sitz des "
        "Auftragnehmers. Es gilt ausschließlich das Recht Spaniens."
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
        "Zustands der in Anhang 1 bezeichneten Ausrüstung, der Identifizierung der "
        "erforderlichen technischen Maßnahmen sowie der Unterstützung eines "
        "zuverlässigen Betriebs und einer zuverlässigen Wartungsplanung."
    ),
    "annex2.purpose.p2": (
        "Die genauen eingeschlossenen Tätigkeiten richten sich nach den in der "
        "Guardian-Konfiguration ausgewählten Optionen."
    ),
    "annex2.inspection.title": "S301 Geplante technische Inspektion",
    "annex2.inspection.p1": (
        "Eine Inspektion bewertet den Zustand der ausgewählten Ausrüstung im "
        "vereinbarten Intervall anhand der anwendbaren linien- bzw. modulbasierten "
        "Checkliste. Der technische Umfang ist an Ausrüstungstyp und -konfiguration "
        "anzupassen."
    ),
    "annex2.inspection.p2": (
        "Vor der Inspektion erörtern Weber und der Kunde bekannte Betriebsprobleme, "
        "die Ausrüstungshistorie und die geplante Produktionsverfügbarkeit. Nach der "
        "Inspektion werden die Feststellungen mit dem benannten Vertreter des Kunden "
        "besprochen und in einem Inspektionsbericht festgehalten."
    ),
    "annex2.checklist.title": "Maschinen-Checkliste",
    "annex2.checklist.p1": (
        "Für Schneidemaschinenlinien kann die Standard-Checkliste die folgenden "
        "Punkte umfassen, soweit technisch anwendbar und sicher zugänglich:"
    ),
    "annex2.checklist.items": [
        "Funktionsprüfung mit Originalprodukt, soweit verfügbar; Zustand der "
        "Ausrüstung und sicherheitsrelevante Feststellungen;",
        "Sensoren, Elektronik, Maschineneinstellungen, elektrische und pneumatische "
        "Funktionen; Antriebe, Zahnriemen und ausgewählte Antriebsstränge;",
        "mechanische Einstellungen, Gehäuse und Dichtungen, Förderer und bewegliche "
        "Elemente; Linienmodule und zugehörige Weber-Bauteile;",
        "Feststellung von Verschleiß, ausstehenden Reparaturen, Maschinenanomalien "
        "und Empfehlungen für weitere Maßnahmen;",
        "Zugang zu Gehäusen von Waagen oder Schneidköpfen ausschließlich nach "
        "ausdrücklicher Vereinbarung und sicherer Autorisierung;",
        "Erstellung einer modulbasierten Inspektions-Checkliste, eines Berichts und "
        "eines optionalen Folgeangebots für Ersatzteile.",
    ],
    "annex2.checklist.p2": (
        "Für Weber-Verpackungsmaschinen kann die Inspektions-Checkliste zusätzlich "
        "definierte verpackungsspezifische Zustandsprüfungen umfassen. "
        "Etikettiermaschinen, Pumpen und End-of-Line-Geräte von Drittanbietern sind "
        "ausgenommen, sofern sie nicht ausdrücklich aufgeführt sind."
    ),
    "annex2.report.title": "S305 Folgebesuch und Berichterstattung",
    "annex2.report.p1": (
        "Soweit vereinbart, führt Weber nach einer Inspektion oder einem "
        "Wartungsereignis einen definierten Folgebesuch durch, der je nach "
        "vereinbarter Leistung vor Ort oder aus der Ferne erfolgen kann."
    ),
    "annex2.report.p2": (
        "Ein Folgebesuch ist nicht automatisch in einer Inspektion enthalten und kann "
        "davon abhängen, dass Weber bestimmte Wartungsarbeiten gemäß dem Zeitplan des "
        "Kunden durchführt."
    ),
    "annex2.preventive.title": "S303 Vorbeugende Wartung",
    "annex2.preventive.p1": (
        "Die vorbeugende Wartung umfasst geplante Einstellungen, Schmierung, "
        "Reinigung definierter technischer Bauteile und den Austausch festgelegter "
        "Verschleißteile gemäß der vereinbarten Tätigkeitsliste und den "
        "Einschränkungen der Ausrüstung."
    ),
    "annex2.preventive.p2": (
        "Der Umfang der gelieferten Teile, der eingebauten Teile, das "
        "Arbeitszeitkontingent, die Häufigkeit und die erforderliche Ausfallzeit sind "
        "je Maschine in Anhang 1 anzugeben."
    ),
    "annex2.preventive.p3": (
        "Die vorbeugende Wartung ist von einer korrektiven Reparatur zu "
        "unterscheiden; Leistungen außerhalb der geplanten Aufgabenliste werden "
        "gesondert genehmigt und berechnet, sofern sie nicht ausdrücklich "
        "eingeschlossen sind."
    ),
    "annex2.kit.title": "S402 Basis-Ersatzteil-Kit - Nur Lieferung",
    "annex2.kit.p1": (
        "Das Basis-Ersatzteil-Kit besteht aus den im unterzeichneten Kit-Zeitplan "
        "aufgeführten Artikeln und Mengen. Es unterstützt den geplanten Austausch "
        "oder den vom Kunden gehaltenen Bestand, stellt jedoch keinen unbegrenzten "
        "Anspruch auf Verbrauchsmaterial dar."
    ),
    "annex2.kit.p2": (
        "Weber liefert die aufgeführten Artikel zu den festgelegten Bestell-, "
        "Liefer- und Preisbedingungen. Die Montage ist bei einem Kit, das "
        "ausschließlich die Lieferung umfasst, nicht enthalten."
    ),
    "annex2.repairs.title": "S304 Korrektive Wartung / Reparatur",
    "annex2.repairs.p1": (
        "Reparaturarbeiten erfolgen nach einem festgestellten Ausfall, Fehler oder "
        "Defekt und dienen der Wiederherstellung eines vereinbarten Zustands, "
        "vorbehaltlich des Zugangs, der technischen Machbarkeit und der Verfügbarkeit "
        "von Teilen."
    ),
    "annex2.repairs.p2": (
        "Sofern keine Reparaturpauschale ausdrücklich bepreist und ausgewählt ist, "
        "werden korrektive Arbeitsleistungen, Ersatzteile, Anfahrtskosten und "
        "sonstige Kosten gemäß den ausgewählten Servicepreisen und der Genehmigung "
        "durch den Kunden angeboten oder berechnet."
    ),
    "annex2.repairs.p3": (
        "Ein Einsatz, eine Fehlerdiagnose oder eine Reparaturtätigkeit gilt nicht als "
        "garantierte Wiederherstellung der Produktion innerhalb eines bestimmten "
        "Zeitraums, sofern dies nicht ausdrücklich schriftlich vereinbart ist."
    ),
    "annex2.frequency.title": "Inspektionshäufigkeit",
    "annex2.frequency.value": "Häufigkeit",
    "annex2.frequency.p1": (
        "Der tatsächliche Zeitplan wird zwischen Weber und dem Kunden koordiniert."
    ),

    # Annex 3 - Service Support
    "annex3.title": "ANHANG 3 - SERVICE-SUPPORT",
    "annex3.tagline": "Kundenservice und technischer Support.",
    "annex3.purpose.title": "1. Zweck",
    "annex3.purpose.p1": (
        "Das Modul Service-Support gewährt dem Kunden Zugang zum technischen Support "
        "von Weber für die von dieser Vereinbarung erfasste Ausrüstung."
    ),
    "annex3.purpose.p2": (
        "Das genaue Servicelevel hängt von den nachstehend ausgewählten Optionen ab."
    ),
    "annex3.rates.title": "2. Servicetarife",
    "annex3.rates.hours": "Zeitfenster",
    "annex3.rates.weekdays": "Montag - Freitag",
    "annex3.rates.saturday": "Samstag",
    "annex3.rates.sunday": "Sonntag / Feiertag",
    "annex3.rates.band": "Stufe",
    "annex3.rates.without": "Ohne Wartungsvertrag",
    "annex3.rates.with": "Mit Wartungsvertrag",
    "annex3.hotline.title": "S101 Standard-Hotline",
    "annex3.hotline.p1": (
        "Weber gewährt während des vereinbarten Verfügbarkeitszeitfensters Zugang zu "
        "dem ausgewählten standardmäßigen technischen Servicekontaktkanal. Es handelt "
        "sich um eine Kommunikationsleistung; eine Vor-Ort-Reaktionszeit ist damit "
        "nicht verbunden."
    ),
    "annex3.hotline.phone": "Ansprechpartner",
    "annex3.hotline.email": "E-Mail",
    "annex3.hotline.hours": "Montag - Freitag",
    "annex3.hotline.p2": (
        "Die Verfügbarkeit zur Anrufannahme stellt für sich genommen weder eine "
        "garantierte diagnostische Lösung noch einen Vor-Ort-Einsatz oder die "
        "Entsendung von Ersatzteilen dar."
    ),
    "annex3.remote.title": "S103 Technischer Fernsupport",
    "annex3.remote.p1": (
        "Weber kann eine erste Fehleranalyse per Telefon, E-Mail, unterstützter "
        "Fernverbindung oder Videokommunikation bereitstellen, vorbehaltlich der "
        "Einigung über einen sicheren Zugang und der Unterstützung durch den Kunden."
    ),
    "annex3.remote.p2": (
        "Die Bedingungen für Verbindung, Netzwerk und Cybersicherheit sind vor der "
        "Aktivierung zu vereinbaren. Der Fernsupport ersetzt keinen erforderlichen "
        "Vor-Ort-Service."
    ),
    "annex3.priority.title": "S104 Vor-Ort-Service und prioritäre Reaktion",
    "annex3.priority.p1": (
        "Technische Unterstützung vor Ort ist im vereinbarten Gebiet nach Maßgabe der "
        "Verfügbarkeit von Technikern sowie der geltenden Entsendungs- und "
        "Buchungsbedingungen verfügbar. Jede Priorisierungseinstufung bedarf einer "
        "ausdrücklichen Vereinbarung."
    ),
    "annex3.priority.p2": (
        "Serviceeinsatzkosten, Arbeitszeit, Reisezeit, Wartezeit, Überstunden, "
        "Unterkunft und Materialien werden nach dem genehmigten Tarifwerk "
        "abgerechnet."
    ),

    # Annex 4 - Parts & Availability
    "annex4.title": "ANHANG 4 - ERSATZTEILE UND VERFÜGBARKEIT",
    "annex4.tagline": (
        "Kommerzielle Ersatzteilbedingungen, priorisierte Bearbeitung und empfohlene "
        "Bestände."
    ),
    "annex4.purpose.title": "1. Zweck",
    "annex4.purpose.p1": (
        "Das Modul Ersatzteile und Verfügbarkeit unterstützt die strukturierte "
        "Ersatzteilplanung und den Zugang zu Original-Ersatzteilen von Weber für die "
        "von dieser Vereinbarung erfasste Ausrüstung."
    ),
    "annex4.discount.title": "S201 Kommerzielle Ersatzteilbedingungen",
    "annex4.discount.p1": (
        "Ausgewählte Ersatzteilkategorien werden zu den vereinbarten Preisen und "
        "Rabatten geliefert, wobei Ausschlüsse sowie die Behandlung von "
        "Austauschteilen, Klingen, Sonderbestellungen und aufgerüsteter Ausrüstung "
        "ausdrücklich angegeben werden."
    ),
    "annex4.discount.p2": (
        "Rabatte sind nicht kumulierbar, sofern nicht ausdrücklich vereinbart."
    ),
    "annex4.handling.title": "S203 Priorisierte Ersatzteilbearbeitung",
    "annex4.handling.p1": (
        "Vorbehaltlich der Verfügbarkeit und der vereinbarten Auftragserteilung "
        "können berechtigte Aufträge je nach lokaler Regelung eine vorrangige "
        "Bearbeitung oder einen vorrangigen Versand erhalten."
    ),
    "annex4.parts_list.title": "S202 Empfohlene Ersatzteilliste",
    "annex4.parts_list.p1": (
        "Weber kann eine maschinenspezifische empfohlene Ersatzteilliste erstellen, "
        "die geplante Verschleißteile von risikoreichen Ersatzteilen unterscheidet, "
        "die für den Kundenbestand empfohlen werden. Die Listen sind nach Alter, "
        "Spezifikation und Supportfähigkeit der Ausrüstung zu überprüfen."
    ),
    "annex4.parts_list.p2": (
        "Sofern die lokale Tochtergesellschaft die Klassifizierung nach "
        "Benelux-Muster anwendet, bezeichnen A/B empfohlene Verschleiß- bzw. "
        "kritische Teile und C/D/E können lokalen Bestand, sonstigen Weber-Bestand "
        "oder Fertigung auf Bestellung kennzeichnen; ein bestimmtes Teil kann sowohl "
        "eine Empfehlung als auch einen Verfügbarkeitsstatus tragen."
    ),
    "annex4.parts_list.categories": [
        "A - Empfohlene Verschleißteile.",
        "B - Kritische Ersatzteile bzw. Ersatzteile mit höherem Ausfallrisiko, die für den Vor-Ort-Bestand vorgeschlagen werden.",
        "C - Verfügbar aus lokalem Weber-Bestand (vorbehaltlich Bestätigung).",
        "D - Verfügbar aus einem anderen Weber-Standort (vorbehaltlich Bestätigung).",
        "E - Fertigung auf Bestellung / kein aktueller Bestand.",
    ],
    "annex4.parts_list.p3": (
        "Die Liste dient der Beratung und stellt keine Garantie für die "
        "Lagerverfügbarkeit oder die Eignung für alle Konfigurationen dar und "
        "begründet keine Verpflichtung, die empfohlenen Mengen automatisch zu "
        "liefern."
    ),
    "annex4.parts_list.p4": (
        "Weber liefert eine beratende maschinenspezifische Teileliste, ohne "
        "Materiallieferung oder Installation, sofern diese nicht gesondert bestellt "
        "werden."
    ),

    # Annex 5 - Blade Solutions
    "annex5.title": "ANHANG 5 - KLINGENLÖSUNGEN",
    "annex5.tagline": (
        "Klingenanwendungsberatung, Schärfung und das Klingenprogramm."
    ),
    "annex5.intro": (
        "Das Modul Klingenlösungen unterstützt die richtige Auswahl, Verfügbarkeit, "
        "Nutzung und Verwaltung der Weber-Klingen, einschließlich des Prinzips "
        "„Richtige Klinge, richtige Anwendung“."
    ),
    "annex5.discount.title": "S603 Klingenlieferpartnerschaft",
    "annex5.discount.p1": (
        "Wählt der Kunde die Option Klingenpartnerschaft, vereinbaren die Parteien "
        "einen festgelegten Katalog von Klingenreferenzen, Mengen, Preisen, "
        "Bestellplan und Vertragslaufzeit im Klingenprogrammplan."
    ),
    "annex5.discount.p2": (
        "Ein etwaiges festes Monatsbudget oder ein Ratenzahlungsplan, eine "
        "Verbrauchsprognose, eine Mindestabnahme, eine Preisbindungsfrist, ein "
        "Rabatt, eine Abrufbestellung, ein Rückgabeprogramm oder eine besondere "
        "Liefervereinbarung gilt nur, wenn dies im genannten Plan festgelegt ist."
    ),
    "annex5.stock.title": "Klingenlagervereinbarung",
    "annex5.stock.p1": (
        "Wird eine Klingenlagervereinbarung gewählt, legen die Parteien die "
        "Referenzen, Mengen, das Wiederauffüllverfahren, den Lagerort und das "
        "Eigentum im unterzeichneten Plan fest."
    ),
    "annex5.stock.p2": (
        "Gekaufte oder gelieferte Mengen sind getrennt vom geschätzten Verbrauch "
        "oder vom internen Klingenlager zu erfassen."
    ),
    "annex5.sharpening.title": "S602 Schärfebewertung",
    "annex5.sharpening.p1": (
        "Weber bewertet im vereinbarten Umfang das derzeitige Schärfeverfahren des "
        "Kunden, dessen Prozesse, Maschinenparameter sowie mögliche Verbesserungen "
        "der Qualitätskontrolle oder der Handhabung."
    ),
    "annex5.application.title": "S601 Klingenanwendungsberatung",
    "annex5.application.p1": (
        "Weber überprüft mit dem Kunden die ausgewählte Schneidanwendung, die "
        "Produkteigenschaften, die Schnittkonfiguration und die relevante "
        "Klingengeometrie oder -spezifikation."
    ),
    "annex5.application.p2": (
        "Ergebnis: eine dokumentierte Reihe technischer Empfehlungen für eine "
        "geeignete Klingen-/Anwendungskombination, vorbehaltlich der Überprüfung in "
        "der tatsächlichen Anwendung."
    ),

    # Annex 6 - Training & Optimization
    "annex6.title": "ANHANG 6 - SCHULUNG UND OPTIMIERUNG",
    "annex6.tagline": (
        "Bediener- und Wartungsschulung, Linienoptimierung und EPIP-Audits."
    ),
    "annex6.intro": (
        "Das Modul Schulung und Optimierung bietet ausgewählte Tätigkeiten zur "
        "Verbesserung des Maschinenbetriebs, der Wartungskompetenz und der "
        "Produktionsleistung."
    ),
    "annex6.operator.title": "S501 Bediener-Schulung",
    "annex6.operator.p1": (
        "Schulung für Bediener zur sicheren und effizienten Nutzung der festgelegten "
        "Ausrüstung, einschließlich ausgewählter Betriebsverfahren, Einstellungen, "
        "Reinigungspraxis und grundlegender Betriebsprüfungen, soweit angemessen."
    ),
    "annex6.maintenance.title": "S502 Schulung für Wartungstechniker",
    "annex6.maintenance.p1": (
        "Schulung für das Wartungsteam des Auftraggebers in Bezug auf "
        "Maschinenaufbau, vorbeugende Prüfungen, Fehlererkennung, sichere "
        "Fehlerbehebung und Wartungsverfahren im Rahmen der vereinbarten "
        "Zugriffsberechtigungen."
    ),
    "annex6.optimization.title": "S702 Linienoptimierung",
    "annex6.optimization.p1": (
        "Weber überprüft festgestellte technische und produktionstechnische "
        "Einschränkungen und kann im vereinbarten Umfang vereinbarte "
        "Maschineneinstellungs- oder Prozessverbesserungen empfehlen oder durchführen."
    ),
    "annex6.optimization.p2": (
        "Etwaige Investitions-Upgrades oder Reparaturpositionen bleiben gesondert."
    ),
    "annex6.epip.title": "S701 EPIP- / Anlagen-Audit",
    "annex6.epip.p1": (
        "Weber führt die ausgewählte eingehende Anlagenbewertung / das EPIP-Audit an "
        "den bezeichneten Produktionslinien durch und stellt einen Bewertungsbericht "
        "bereit."
    ),
    "annex6.epip.p2": (
        "Der Bericht hat den festgestellten Zustand, Prioritätsmaßnahmen, empfohlene "
        "Reparaturen und Verbesserungspotenziale zu unterscheiden."
    ),

    # Annex 7 - Digital Services
    "annex7.title": "ANHANG 7 - DIGITALE DIENSTLEISTUNGEN",
    "annex7.tagline": (
        "Factory Cockpit, Performance-Überprüfungen, MRO-Überprüfungen und "
        "dedizierte Account-Reviews."
    ),
    "annex7.intro": (
        "Das Modul Digitale Dienstleistungen bietet ausgewählte digitale "
        "Monitoring-, Performance-Überprüfungs- und Account-Management-Leistungen."
    ),
    "annex7.cockpit.title": "S801 Factory Cockpit / Monitoring",
    "annex7.cockpit.p1": (
        "Sofern verfügbar und ausgewählt, stellt Weber die vereinbarte Anbindung "
        "oder den vereinbarten Zugang zu der bezeichneten Factory-Cockpit- oder "
        "unterstützten digitalen Monitoring-Funktionalität für geeignete "
        "Ausrüstung bereit."
    ),
    "annex7.cockpit.p2": (
        "Verbindungsarchitektur, Dienstverfügbarkeit, Aufbewahrung, Zugriffsrechte "
        "und Verantwortlichkeiten für die Cybersicherheit werden in den Bedingungen "
        "für digitale Dienstleistungen festgelegt."
    ),
    "annex7.performance.title": (
        "S802 Performance-Überprüfung und Trendberichte"
    ),
    "annex7.performance.p1": (
        "Weber kann auf Grundlage der bereitgestellten Daten vereinbarte "
        "Informationen zur Ausrüstungsleistung, Betriebstrends und identifizierte "
        "Bereiche für Folgeaktivitäten erstellen oder überprüfen."
    ),
    "annex7.performance.p2": (
        "Die Werte können durch Datenqualität, Betriebspraktiken, Produktmix und "
        "Systeme Dritter beeinflusst werden. Berichte sind analytischer Natur und "
        "stellen keine Garantien für die Produktionsleistung dar."
    ),
    "annex7.mro.title": "S803 Service-/Ersatzteil-MRO-Überprüfung",
    "annex7.mro.p1": (
        "Weber kann die vereinbarten Serviceausgaben und den Ersatzteilverbrauch "
        "anhand einer definierten MRO-Referenz oder eines vereinbarten "
        "Planungsziels überprüfen."
    ),
    "annex7.mro.p2": (
        "Feste Entgelte von Guardian, tatsächliche Wartungseinsätze und verbrauchte "
        "Ersatzteile bleiben getrennte Datenelemente; es erfolgen keine doppelten "
        "Kosten und keine Ableitung von Ausfällen aus Rechnungssummen."
    ),
    "annex7.account.title": "S105 Dedizierte Account-Reviews",
    "annex7.account.p1": (
        "Sofern ausgewählt, koordiniert ein zugewiesener Account- oder "
        "After-Sales-Ansprechpartner regelmäßige Überprüfungen der vereinbarten "
        "Serviceerbringung, der abgeschlossenen Aktivitäten, der offenen Maßnahmen "
        "und der anstehenden Anforderungen."
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
