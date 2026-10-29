"""Italian overrides for the Guardian agreement content (full catalog).

Responsibility: translate every translatable node id to Italian. Any node id
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
    "module.customer_service": "Assistenza clienti",
    "module.spare_parts": "Ricambi e disponibilità",
    "module.academy": "Academy",
    "module.blade_solutions": "Lame e soluzioni",
    "module.optimization": "Ottimizzazione e prestazioni",
    "module.digital_services": "Servizi digitali",

    # Always-on rows of the annex/summary tables
    "annex1.summary.inspection": "Ispezione e manutenzione",
    "summary.scope.inspection": "Ispezione e manutenzione",

    # Guardian contract types (labels.GUARDIAN_TYPE_LABELS)
    "guardian_type.audit": "Ispezione",
    "guardian_type.off_guardian": "Off-Guardian",
    "guardian_type.guardian": "Basic Kit",

    # Cover
    "cover.title": "CONTRATTO DI MANUTENZIONE",
    "cover.executor.label": "Tra la società:",
    "cover.executor.alias": "(di seguito, l'Esecutore)",
    "cover.customer.label": "E la società:",
    "cover.customer.alias": "(di seguito, il Committente)",
    "cover.preamble": (
        "si conclude il seguente contratto di ispezione e manutenzione "
        '(di seguito, il "Contratto"):'
    ),

    # Commercial breakdown (legacy Annex 1)
    "breakdown.title": "ALLEGATO 1, Elenco delle macchine e dei moduli",
    "breakdown.date": "Data",
    "breakdown.offer_no": "N.° d'offerta",
    "breakdown.frequency": "Frequenza di ispezione",
    "breakdown.type": "Tipo",
    "breakdown.col.line": "Riga",
    "breakdown.col.module": "Modulo",
    "breakdown.col.amount": "Importo",
    "breakdown.total": "Totale",
    "breakdown.kit": "Kit base di ricambi",
    "breakdown.discount": "Sconto con contratto di manutenzione",
    "breakdown.grand_total": "Importo totale (IVA esclusa)",
    "breakdown.intro": (
        "Entrambe le Parti concordano il seguente preventivo di ispezione Weber alle "
        "condizioni di seguito indicate:"
    ),
    "breakdown.notes": [
        "include trasferte, manodopera e documentazione.",
        "controllo di sensori, componenti elettrici, trasmissioni, cinghie dentate e "
        "lame (il kit base comprende la sostituzione delle cinghie principali della "
        "testa, del mandrino e dei moduli ausiliari).",
        "regolazione delle parti meccaniche dei diversi moduli.",
        "revisione e ottimizzazione dei programmi.",
        "registrazione di tutte le riparazioni previste.",
    ],
    "breakdown.notes_title": "NOTE:",
    "breakdown.discount_notes": [
        "Sconto del 15% sull'assistenza tecnica per le linee contrattualizzate.",
        "Sconto del 5% sui ricambi per le linee contrattualizzate (non applicabile agli "
        "sconti vigenti).",
        "Sconto del 5% sulle lame per scatole complete di 3 lame (non applicabile agli "
        "sconti vigenti).",
        "include una visita di follow-up gratuita dopo 6 mesi.",
        "tutte le parti, i materiali di consumo e i ricambi fuori preventivo, nonché le ore "
        "fuori dall'orario normale, l'attesa e le riparazioni fuori preventivo, sono "
        "fatturati separatamente.",
    ],

    # Master Agreement
    "master.clause0.title": "0. DEFINIZIONI",
    "master.clause0.intro": "I termini utilizzati nel presente contratto hanno il seguente significato:",
    "master.clause0.machine.term": "Macchina / Moduli",
    "master.clause0.machine.definition": (
        "Un'unità funzionale, un'apparecchiatura o un sistema a cui si riferiscono i "
        "servizi forniti nell'ambito del presente contratto."
    ),
    "master.clause0.inspection.term": "Ispezione",
    "master.clause0.inspection.definition": (
        "La determinazione e la valutazione dello stato effettivo di una macchina / "
        "modulo, compresa la determinazione delle cause dell'usura e delle conseguenti "
        "ripercussioni sull'utilizzo futuro."
    ),
    "master.clause0.maintenance.term": "Manutenzione",
    "master.clause0.maintenance.definition": (
        "Le misure volte a ritardare il deterioramento degli elementi soggetti a usura "
        "esistenti («manutenzione preventiva»), in particolare mediante regolazioni o "
        "sostituzione di filtri, guarnizioni e lubrificanti, pulizia tecnica, ecc."
    ),
    "master.clause0.replacement.term": "Riparazione",
    "master.clause0.replacement.definition": (
        "Qualsiasi misura volta a riportare una macchina / modulo alla condizione "
        "concordata, in particolare mediante la sostituzione di parti, comprese le parti "
        "soggette a usura. Anche le misure volte a mantenere la condizione concordata al "
        "di fuori dei servizi di manutenzione fanno parte della riparazione."
    ),

    # I. PURPOSE OF THE CONTRACT
    "master.clause1.title": "I. OGGETTO DEL CONTRATTO",
    "master.clause1.p1": (
        "(0) Il presente contratto di ispezione ha per oggetto l'ispezione delle macchine "
        "e dei moduli elencati nell'Allegato 1, con tali servizi fatturati sulla base di "
        "un corrispettivo fisso (Allegato 1). La manutenzione delle macchine e dei "
        "componenti sarà addebitata in base ai costi effettivamente sostenuti e secondo le "
        "tariffe vigenti."
    ),
    "master.clause1.p2": (
        "L'oggetto del Contratto è prolungare la vita utile delle macchine e dei moduli, "
        "ridurre i tempi di inattività e mantenere sotto controllo i costi di manutenzione "
        "mediante un'adeguata ispezione e manutenzione."
    ),
    "master.clause1.p3": (
        "(1) Ai sensi del presente Contratto, l'Esecutore assume i seguenti servizi per le "
        "macchine e i moduli elencati:"
    ),
    "master.clause1.services": [
        "Servizio di linea diretta",
        "Fornitura di ricambi",
        "Manutenzione",
        "Visita di cortesia dopo la manutenzione",
        "Programma Lame (detenzione a magazzino)",
    ],
    "master.clause1.p4": "(2) Il servizio dell'Esecutore comprende, nei seguenti casi:",
    "master.clause1.p5": "(2.1) Qualora venga contattato il servizio di linea diretta o il centro di assistenza telefonica:",
    "master.clause1.hotline": [
        "Servizio di linea diretta dal lunedì al venerdì, dalle 07:30 alle 17:30.",
        "Telefono: 938 23 32 33",
    ],
    "master.clause1.p6": (
        "(2.2) Distribuzione dei ricambi: fornitura dei ricambi disponibili a magazzino "
        "(nella Penisola Iberica e in Germania) entro 24-48 ore. Qualora il ricambio "
        "richiesto non sia disponibile a magazzino, sarà ordinato e consegnato il prima "
        "possibile."
    ),
    "master.clause1.p7": "(2.3) Ispezione: ispezione delle macchine in conformità all'Allegato 1.",
    "master.clause1.p8": "(2.4) Manutenzione: esecuzione delle riparazioni in conformità al punto I.3 del Contratto.",
    "master.clause1.p9": (
        "(2.5) Programma di detenzione a scorta delle lame: sconto del 5% a partire dalla "
        "prima scatola di 3 unità, in conformità all'Allegato 2."
    ),
    "master.clause1.p10": (
        "(3) Qualsiasi lavoro di manutenzione o altro servizio (ad esempio, modifiche a "
        "macchine e sistemi) derivante dall'ispezione richiederà un separato ordine di "
        "acquisto e sarà fatturato dietro preventivo aggiuntivo."
    ),
    "master.clause1.p11": (
        "(4) Il numero di macchine incluse nell'Allegato 1, nonché l'ambito dei servizi "
        "derivanti dal presente Contratto, sarà verificato dalle parti contraenti "
        "nell'ultimo trimestre del Contratto."
    ),
    "master.clause1.p12": (
        "(5) Le modifiche al numero di macchine incluse nell'accordo e le modifiche "
        "all'ambito del servizio da parte del Committente saranno registrate per iscritto, "
        "modificando l'Allegato 1. Il presente accordo di servizio è valido per i 12 mesi "
        "della durata del Contratto o fino alla cessazione del Contratto."
    ),
    "master.clause1.p13": (
        "(6) Visita di cortesia da effettuarsi qualora la successiva manutenzione sia "
        "eseguita dall'Esecutore."
    ),

    # II. PRICE AND PAYMENT
    "master.clause2.title": "II. PREZZO E PAGAMENTO",
    "master.clause2.p1": (
        "(1) Il prezzo del lavoro di ispezione è calcolato in conformità all'Allegato 1. "
        "Il rapporto deriva dal modello di macchina e dai moduli selezionati ai sensi del "
        "punto I del Contratto."
    ),
    "master.clause2.p2": (
        '(2) Il prezzo per i moduli "Ispezione" e "Manutenzione" comprende le spese di '
        "viaggio, trasporto, alloggio e soggiorno. Salvo eccezioni concordate con il "
        "Committente."
    ),
    "master.clause2.p3": "(3) Le parti sostituite saranno presentate al Committente per il suo controllo.",
    "master.clause2.p4": (
        "(4) Il prezzo del lavoro del personale di ispezione sarà pagato entro 30 giorni "
        "dall'emissione della fattura. La fatturazione avviene dopo l'esecuzione "
        "dell'ispezione."
    ),
    "master.clause2.p5": (
        "(5) L'Esecutore ha diritto di rivedere annualmente il prezzo del lavoro in "
        "conformità all'Allegato 1. Ne darà notifica al Committente almeno 3 mesi prima "
        "della sua entrata in vigore. La variazione di prezzo si applicherà nel periodo di "
        "pagamento successivo."
    ),
    "master.clause2.p6": (
        "(6) Non è accettata la ritenuta dei pagamenti o la compensazione per presunti "
        "controcrediti da parte del Committente."
    ),
    "master.clause2.p7": (
        "(7) L'Esecutore offre uno sconto del 15% per i servizi di assistenza alle "
        "macchine e uno sconto massimo del 5% sui ricambi, non cumulabili, come indicato "
        "nell'Allegato 1."
    ),

    # III. CLIENT PARTICIPATION AND TECHNICAL CONTRIBUTION
    "master.clause3.title": "III. PARTECIPAZIONE DEL COMMITTENTE E CONTRIBUTO TECNICO",
    "master.clause3.p1": "(1) Il Committente garantisce che:",
    "master.clause3.obligations": [
        "I lavori possano essere eseguiti puntualmente nei tempi concordati e sulle "
        "macchine concordate, e garantirà il libero accesso alle macchine e ai moduli.",
        "La macchina sia in condizioni di funzionamento, disponibile e pulita (senza "
        "residui di prodotto).",
        "Una volta completati i lavori, possa essere eseguito un controllo funzionale con "
        "i prodotti originali del cliente in quantità sufficiente.",
        "I guasti in corso siano registrati sui disegni della macchina.",
        "La produzione sia organizzata in modo da poter essere fermata durante "
        "l'ispezione.",
    ],
    "master.clause3.p2": (
        "(2.a) Il Committente sostiene i costi sostenuti dal personale di ispezione "
        "durante l'ispezione e la manutenzione."
    ),
    "master.clause3.p3": (
        "Il Committente adotta le misure speciali necessarie per la protezione delle "
        "persone e dei beni nel luogo dell'ispezione/manutenzione. Informa inoltre il "
        "personale della società esecutrice delle misure di sicurezza speciali, nella "
        "misura in cui queste siano rilevanti per il personale di ispezione e "
        "manutenzione. Il Committente notifica all'esecutore eventuali violazioni commesse "
        "dal personale che contravvengono a tali norme di sicurezza."
    ),
    "master.clause3.p4": (
        "(b) Il Committente si impegna a sostenere i costi del contributo tecnico, in "
        "particolare a fornire assistenza, officina, mezzi ausiliari quali acqua ed "
        "elettricità gratuitamente, compresi i necessari collegamenti."
    ),
    "master.clause3.p5": (
        "(c) Al fine di decidere se i lavori possano essere eseguiti e/o le parti indicate "
        "al punto I.3 possano essere sostituite durante l'intervallo di ispezione, il "
        "Committente designa una persona con potere decisionale."
    ),

    # IV. COMPLIANCE WITH CONTRACT DEADLINES
    "master.clause4.title": "IV. RISPETTO DEI TERMINI CONTRATTUALI",
    "master.clause4.p1": (
        "(1) L'Esecutore si impegna a eseguire un'ispezione entro l'intervallo di tempo "
        "concordato nell'Allegato 1."
    ),
    "master.clause4.p2": (
        "(2) L'Esecutore notifica al Committente la data esatta dell'ispezione con almeno "
        "6 settimane di anticipo, salvo che sia stata concordata una data specifica tra le "
        "parti contraenti."
    ),
    "master.clause4.p3": "(3) L'Esecutore fornisce i servizi nei seguenti periodi:",
    "master.clause4.service_periods": [
        "Ispezione e manutenzione dal lunedì al venerdì, dalle 08:00 alle 18:00.",
        "Salvo diverso accordo reciproco.",
    ],
    "master.clause4.p4": (
        "(4) Se il Committente o l'Esecutore non è in grado di eseguire i lavori alla data "
        "programmata, entrambe le parti si informano reciprocamente con almeno 2 giorni "
        "lavorativi di anticipo. Se l'Esecutore non si presenta alla data concordata, "
        "l'Esecutore non fattura i costi di viaggio per la data successiva; se la linea non "
        "è disponibile alla data concordata dal Committente, il Committente paga "
        "all'Esecutore i costi di viaggio sostenuti."
    ),
    "master.clause4.p5": (
        "(5) Se l'ispezione/la manutenzione è ritardata a causa di circostanze derivanti "
        "da conflitti di lavoro, in particolare scioperi e interruzioni, o da eventi non "
        "imputabili all'Esecutore, l'ispezione/la manutenzione sarà adeguatamente "
        "prorogata, purché sia dimostrabile che tali impedimenti abbiano un impatto "
        "significativo sul completamento dell'ispezione/della manutenzione. Ciò si applica "
        "anche qualora tali circostanze si verifichino dopo che l'Esecutore non ha "
        "rispettato il termine di preavviso di cui al comma precedente."
    ),

    # V. COMMENCEMENT AND TERM
    "master.clause5.title": "V. DECORRENZA E DURATA DEL CONTRATTO",
    "master.clause5.p1": (
        "(1) Il Contratto è valido dalla firma di entrambe le parti. La durata del "
        "Contratto è di 12 mesi e può essere risolto da ciascuna delle parti."
    ),
    "master.clause5.p2": (
        "(2) Il Contratto si rinnova automaticamente per ulteriori 12 mesi, salvo "
        "disdetta scritta 3 mesi prima della sua scadenza."
    ),

    # VI. WARRANTY AND LIABILITY
    "master.clause6.title": "VI. GARANZIA E RESPONSABILITÀ",
    "master.clause6.p1": (
        "(1) Se l'ispezione/la manutenzione non è stata completamente eseguita, "
        "l'Esecutore la riesamina o la rettifica senza alcun costo."
    ),
    "master.clause6.p2": (
        "(2) L'Esecutore pone rimedio gratuitamente a tutti i danni causati da sé o dai "
        "suoi agenti alle macchine e agli impianti che dovevano essere sottoposti a "
        "manutenzione. L'importo dell'obbligo di riparazione è limitato al corrispettivo "
        "annuo stipulato nel contratto."
    ),
    "master.clause6.p3": (
        "(3) Se l'Esecutore non adempie al proprio obbligo di riparazione, di rimedio o di "
        "riparazione dei danni, il Committente può fissare un'adeguata proroga. Se, per "
        "colpa dell'Esecutore, tale termine trascorre senza esito, il Committente può, a "
        "sua scelta, chiedere una riduzione dei corrispettivi di manutenzione e ispezione "
        "o risolvere immediatamente il Contratto. Sia l'Esecutore sia il Committente "
        "concordano espressamente che l'Esecutore sarà responsabile dei danni solo qualora "
        "sia dimostrabile dolo o colpa grave da parte sua o dei suoi agenti. In "
        "particolare, le parti escludono espressamente la responsabilità per danni o "
        "perdite indiretti."
    ),
    "master.clause6.p4": (
        "(4) Qualsiasi altro diritto di pretesa del Committente si applica solo in caso di "
        "dolo o colpa grave. Inoltre, il Committente non può far valere alcun altro "
        "diritto di compensazione nei confronti dell'Esecutore, in particolare nessun "
        "diritto al risarcimento dei danni o altri diritti per qualsiasi inconveniente "
        "relativo al Contratto di ispezione, indipendentemente dalle ragioni."
    ),
    "master.clause6.p5": (
        "(5) L'Esecutore non è responsabile per danni o difetti causati da parti non "
        "originali."
    ),

    # VII. LIMITATION PERIOD
    "master.clause7.title": "VII. TERMINE DI PRESCRIZIONE",
    "master.clause7.p1": (
        "I diritti di garanzia del Committente decadono dodici mesi dopo l'accettazione "
        "del corrispondente servizio di ispezione/manutenzione. Il periodo di garanzia è "
        "prorogato per la durata dei lavori di rimedio."
    ),

    # VIII. OTHER PROVISIONS
    "master.clause8.title": "VIII. ALTRE DISPOSIZIONI",
    "master.clause8.p1": (
        "(1) Al personale di ispezione/manutenzione è concesso l'accesso alle macchine e "
        "agli impianti durante l'orario di lavoro normale/orario di servizio, affinché "
        "possa eseguire i lavori di ispezione e manutenzione annunciati. Il Committente "
        "fornisce tutte le informazioni necessarie sulle macchine e sui moduli indicati "
        "nell'Allegato 1 e mette a disposizione la documentazione corrispondente."
    ),
    "master.clause8.p2": (
        "(2) Se il Committente trasferisce macchine e impianti a terzi, resta responsabile "
        "del pagamento dei corrispettivi, salvo che il terzo subentri nel contratto previa "
        "autorizzazione dell'Esecutore. L'Esecutore può rifiutare il consenso solo per "
        "motivi giustificati."
    ),
    "master.clause8.p3": (
        "(3) L'Esecutore ha il diritto di trasferire a terzi i diritti e gli obblighi "
        "assunti ai sensi del presente contratto."
    ),
    "master.clause8.p4": (
        "(4) Gli accordi aggiuntivi e le modifiche al contratto devono essere stipulati per "
        "iscritto."
    ),
    "master.clause8.p5": (
        "(5) Se una qualsiasi disposizione del presente contratto diventa invalida, tutte "
        "le altre disposizioni o accordi restano validi."
    ),

    # IX. PLACE OF JURISDICTION
    "master.clause9.title": "IX. FORO COMPETENTE",
    "master.clause9.p1": (
        "Nella misura consentita dalla legge, il luogo di esecuzione e il foro competente "
        "sono la sede legale dell'Esecutore. Si applica esclusivamente la legge spagnola."
    ),

    # Annex 1 - Equipment & Commercial Schedule
    "annex1.title": "ALLEGATO 1 - ATTREZZATURA E CONDIZIONI COMMERCIALI",
    "annex1.info.title": "1. Informazioni sul contratto",
    "annex1.info.customer": "Cliente",
    "annex1.info.customer_no": "N.° cliente",
    "annex1.info.site": "Sede",
    "annex1.info.agreement_no": "N.° d'accordo",
    "annex1.info.start_date": "Data di inizio del contratto",
    "annex1.info.term": "Durata iniziale",
    "annex1.info.billing": "Frequenza di fatturazione",
    "annex1.info.currency": "Valuta",
    "annex1.equipment.title": "2. Attrezzatura coperta",
    "annex1.equipment.intro": "Solo l'Attrezzatura e i moduli di macchina elencati di seguito sono coperti dai Servizi Guardian.",
    "annex1.equipment.h_line": "Linea di produzione",
    "annex1.equipment.h_machine": "Macchina",
    "annex1.equipment.h_serial": "N.° di serie",
    "annex1.equipment.h_type": "Tipo",
    "annex1.equipment.h_modules": "Moduli / componenti inclusi",
    "annex1.equipment.h_frequency": "Frequenza di servizio",
    "annex1.modules.title": "3. Moduli Guardian selezionati",
    "annex1.modules.intro": "I seguenti moduli Guardian fanno parte del presente Accordo:",
    "annex1.modules.outro": (
        "Solo gli Allegati corrispondenti ai moduli selezionati sopra sono allegati e "
        "fanno parte dell'Accordo."
    ),
    "annex1.summary.title": "4. Riepilogo commerciale",
    "annex1.summary.h_item": "Voce commerciale",
    "annex1.summary.h_amount": "Importo",
    "annex1.summary.travel": "Trasferte / spese",
    "annex1.summary.kit": "Ricambi / kit di manutenzione",
    "annex1.summary.discount": "Sconto Guardian",
    "annex1.summary.total": "VALORE TOTALE DEL CONTRATTO",
    "annex1.summary.vat_note": "Tutti gli importi sono al netto dell'IVA applicabile, salvo indicazione contraria.",
    "annex1.billing.title": "5. Fatturazione",
    "annex1.billing.frequency": "Frequenza di fatturazione",
    "annex1.billing.terms": "Condizioni di pagamento",
    "annex1.billing.adjustment": "Adeguamento dei prezzi",
    "annex1.billing.travel": "Condizioni di trasferta",
    "annex1.billing.freight": "Condizioni di trasporto",
    "annex1.special.title": "6. Condizioni commerciali speciali",

    # Annex 2 - Maintenance & Inspection
    "annex2.title": "ALLEGATO 2 - MANUTENZIONE E ISPEZIONE",
    "annex2.tagline": "Servizi di ispezione, manutenzione preventiva e verifica dello stato della macchina.",
    "annex2.purpose.title": "1. Finalità",
    "annex2.purpose.p1": (
        "Il modulo Manutenzione e Ispezione è destinato a valutare e mantenere lo stato "
        "dell'Attrezzatura identificata nell'Allegato 1, a individuare le azioni tecniche "
        "necessarie e a sostenere un esercizio affidabile nonché la pianificazione della "
        "manutenzione."
    ),
    "annex2.purpose.p2": "Le attività esatte incluse dipendono dalle opzioni selezionate nella configurazione Guardian.",
    "annex2.inspection.title": "S301 Ispezione Tecnica Programmata",
    "annex2.inspection.p1": (
        "Un'ispezione valuta lo stato dell'attrezzatura selezionata all'intervallo "
        "concordato mediante la checklist applicabile basata sulla linea o sui moduli. "
        "L'ambito tecnico è adattato al tipo e alla configurazione dell'attrezzatura."
    ),
    "annex2.inspection.p2": (
        "Prima dell'ispezione, Weber e il Cliente riesaminano i problemi operativi noti, "
        "lo storico dell'attrezzatura e la disponibilità produttiva pianificata. Dopo "
        "l'ispezione, i rilievi sono discussi con il rappresentante designato del Cliente "
        "e registrati in un rapporto di ispezione."
    ),
    "annex2.checklist.title": "Checklist Macchina",
    "annex2.checklist.p1": (
        "Per le linee di affettatura, la checklist standard può comprendere quanto segue, "
        "ove tecnicamente applicabile e accessibile in condizioni di sicurezza:"
    ),
    "annex2.checklist.items": [
        "prova di funzionamento con prodotto originale, ove disponibile; stato "
        "dell'attrezzatura e osservazioni relative alla sicurezza;",
        "sensori, elettronica, impostazioni della macchina, funzioni elettriche e "
        "pneumatiche; azionamenti, cinghie dentate e trasmissioni selezionate;",
        "regolazioni meccaniche, carter e guarnizioni, trasportatori ed elementi mobili; "
        "moduli di linea e componenti ausiliari Weber;",
        "individuazione di usura, riparazioni pendenti, anomalie della macchina e "
        "raccomandazioni per ulteriori azioni;",
        "accesso ai carter di pesatura o della testa di taglio solo se espressamente "
        "concordato e autorizzato in condizioni di sicurezza;",
        "predisposizione di una checklist di ispezione basata sui moduli, di un rapporto "
        "e di un eventuale preventivo di follow-up per i ricambi.",
    ],
    "annex2.checklist.p2": (
        "Per le macchine confezionatrici Weber, la checklist di ispezione può inoltre "
        "comprendere controlli di stato specifici per il confezionamento. Etichettatrici, "
        "pompe e dispositivi di fine linea di terzi sono esclusi salvo espressa elencazione."
    ),
    "annex2.report.title": "S305 Visita di Follow-up e Rapporto",
    "annex2.report.p1": (
        "Ove concordato, Weber eseguirà un follow-up definito successivamente a "
        "un'ispezione o a un intervento di manutenzione, che può essere in sito o remoto "
        "in funzione del servizio concordato."
    ),
    "annex2.report.p2": (
        "La visita di follow-up non è inclusa automaticamente nell'ispezione e può essere "
        "subordinata all'esecuzione da parte di Weber dei lavori di manutenzione "
        "specificati, come indicato nel calendario del Cliente."
    ),
    "annex2.preventive.title": "S303 Manutenzione Preventiva",
    "annex2.preventive.p1": (
        "La manutenzione preventiva consiste in regolazioni pianificate, lubrificazione, "
        "pulizia di componenti tecnici definiti e sostituzione di parti soggette a usura "
        "specificate, secondo l'elenco delle attività concordato e i vincoli "
        "dell'attrezzatura."
    ),
    "annex2.preventive.p2": (
        "L'ambito delle parti fornite, delle parti installate, della manodopera prevista, "
        "della frequenza e dei tempi di inattività richiesti è specificato per ciascuna "
        "macchina nell'Allegato 1."
    ),
    "annex2.preventive.p3": (
        "La manutenzione preventiva è distinta dalla riparazione correttiva; i servizi al "
        "di fuori dell'elenco delle attività pianificate sono autorizzati e fatturati "
        "separatamente, salvo espressa inclusione."
    ),
    "annex2.kit.title": "S402 Kit Base di Ricambi - Solo Fornitura",
    "annex2.kit.p1": (
        "Il Kit Base di Ricambi è costituito dagli articoli e dalle quantità esatti "
        "elencati nel Programma del Kit sottoscritto. Esso sostiene la sostituzione "
        "pianificata o la scorta detenuta dal Cliente, ma non costituisce un diritto "
        "illimitato ai materiali di consumo."
    ),
    "annex2.kit.p2": (
        "Weber fornisce gli articoli elencati alle condizioni di ordinazione, consegna e "
        "prezzo specificate. L'installazione non è inclusa nel kit di sola fornitura."
    ),
    "annex2.repairs.title": "S304 Manutenzione Correttiva / Riparazione",
    "annex2.repairs.p1": (
        "I lavori di riparazione conseguono a un guasto, difetto o anomalia identificati "
        "e mirano a ripristinare una condizione concordata, subordinatamente all'accesso, "
        "alla fattibilità tecnica e alla disponibilità dei ricambi."
    ),
    "annex2.repairs.p2": (
        "Salvo che un'allocazione di riparazione sia espressamente prezzata e selezionata, "
        "la manodopera correttiva, i ricambi, le trasferte e gli altri costi sono "
        "preventivati o fatturati secondo le tariffe di servizio selezionate e "
        "l'autorizzazione del Cliente."
    ),
    "annex2.repairs.p3": (
        "Un intervento, una diagnosi guasti o un'attività di riparazione non sono "
        "rappresentati come ripristino garantito della produzione entro un determinato "
        "periodo, salvo espressa pattuizione scritta."
    ),
    "annex2.frequency.title": "Frequenza di Ispezione",
    "annex2.frequency.value": "Frequenza",
    "annex2.frequency.p1": "Il calendario effettivo è coordinato tra Weber e il Cliente.",

    # Annex 3 - Service Support
    "annex3.title": "ALLEGATO 3 - ASSISTENZA DI SERVIZIO",
    "annex3.tagline": "Assistenza al cliente e supporto tecnico.",
    "annex3.purpose.title": "1. Finalità",
    "annex3.purpose.p1": (
        "Il modulo Assistenza di Servizio consente al Cliente di accedere al supporto "
        "tecnico di Weber per l'Attrezzatura coperta dal presente Accordo."
    ),
    "annex3.purpose.p2": "Il livello di servizio effettivo dipende dalle opzioni selezionate di seguito.",
    "annex3.rates.title": "2. Tariffe di Servizio",
    "annex3.rates.hours": "Fascia oraria",
    "annex3.rates.weekdays": "Lunedì - Venerdì",
    "annex3.rates.saturday": "Sabato",
    "annex3.rates.sunday": "Domenica / festivo",
    "annex3.rates.band": "Fascia",
    "annex3.rates.without": "Senza contratto",
    "annex3.rates.with": "Con contratto",
    "annex3.hotline.title": "S101 Linea Diretta Standard",
    "annex3.hotline.p1": (
        "Weber garantirà l'accesso al canale di contatto tecnico standard selezionato "
        "durante la finestra di disponibilità concordata. Il presente è un servizio di "
        "comunicazione; non implica alcun tempo di intervento in sito."
    ),
    "annex3.hotline.phone": "Referente",
    "annex3.hotline.email": "E-mail",
    "annex3.hotline.hours": "Lunedì - Venerdì",
    "annex3.hotline.p2": (
        "La disponibilità all'accettazione delle chiamate non costituisce, di per sé, "
        "garanzia di risoluzione diagnostica, di intervento in sito o di invio dei ricambi."
    ),
    "annex3.remote.title": "S103 Supporto Tecnico Remoto",
    "annex3.remote.p1": (
        "Weber potrà fornire una prima analisi del guasto per telefono, e-mail, "
        "connessione remota supportata o comunicazione video, previo accordo sull'accesso "
        "sicuro e sull'assistenza del Cliente."
    ),
    "annex3.remote.p2": (
        "Le modalità di connessione, di rete e di cybersicurezza devono essere concordate "
        "prima dell'attivazione. Il Supporto Tecnico Remoto non sostituisce un intervento "
        "in sito necessario."
    ),
    "annex3.priority.title": "S104 Servizio in Sito e Risposta Prioritaria",
    "annex3.priority.p1": (
        "L'assistenza tecnica in sito è disponibile nel territorio concordato, "
        "subordinatamente alla disponibilità dei tecnici e alle condizioni applicabili di "
        "invio e di prenotazione. Qualsiasi livello di priorità deve essere espressamente "
        "concordato."
    ),
    "annex3.priority.p2": (
        "I costi di intervento, la manodopera, le trasferte, i tempi di attesa, gli "
        "straordinari, l'alloggio e i materiali sono calcolati secondo il tariffario "
        "approvato."
    ),

    # Annex 4 - Parts & Availability
    "annex4.title": "ALLEGATO 4 - RICAMBI E DISPONIBILITÀ",
    "annex4.tagline": "Condizioni commerciali dei ricambi, gestione prioritaria e scorta consigliata.",
    "annex4.purpose.title": "1. Finalità",
    "annex4.purpose.p1": (
        "Il modulo Ricambi e Disponibilità supporta la pianificazione strutturata dei "
        "ricambi e l'accesso ai ricambi originali Weber per l'Attrezzatura coperta dal "
        "presente Accordo."
    ),
    "annex4.discount.title": "S201 Condizioni Commerciali dei Ricambi",
    "annex4.discount.p1": (
        "Le categorie selezionate di ricambi sono fornite ai prezzi e agli sconti "
        "concordati, con esclusione e trattamento espressamente indicati per le parti in "
        "scambio, le lame, gli ordini speciali e le attrezzature aggiornate."
    ),
    "annex4.discount.p2": "Gli sconti non sono cumulabili salvo espressa convenzione.",
    "annex4.handling.title": "S203 Gestione Prioritaria dei Ricambi",
    "annex4.handling.p1": (
        "Fatte salve la disponibilità e le modalità concordate di inoltro dell'ordine, "
        "gli ordini idonei possono ricevere un'elaborazione o una spedizione prioritaria "
        "secondo l'accordo locale."
    ),
    "annex4.parts_list.title": "S202 Lista Ricambi Consigliati",
    "annex4.parts_list.p1": (
        "Weber potrà predisporre una lista di ricambi consigliati specifica per la "
        "macchina, distinguendo le parti soggette a usura pianificata dai ricambi ad alto "
        "rischio raccomandati per la scorta del Cliente. Le liste saranno riesaminate in "
        "funzione dell'età, della specifica e della supportabilità dell'attrezzatura."
    ),
    "annex4.parts_list.p2": (
        "Ove la filiale locale applichi la classificazione di tipo Benelux, A/B indicano "
        "le parti soggette a usura o critiche consigliate, mentre C/D/E possono "
        "identificare scorta locale, altra scorta Weber o produzione su ordinazione; uno "
        "stesso ricambio può riportare sia una raccomandazione sia uno stato di "
        "disponibilità."
    ),
    "annex4.parts_list.categories": [
        "A - Parti soggette a usura consigliate.",
        "B - Ricambi critici / a maggiore rischio di guasto proposti per la scorta in sito.",
        "C - Disponibili presso la scorta locale Weber (salvo conferma).",
        "D - Disponibili presso un'altra sede Weber (salvo conferma).",
        "E - Produzione su ordinazione / nessuna scorta attuale.",
    ],
    "annex4.parts_list.p3": (
        "La lista ha valore indicativo e non costituisce garanzia di disponibilità a "
        "magazzino, di idoneità a tutte le configurazioni né impegno a fornire "
        "automaticamente le quantità consigliate."
    ),
    "annex4.parts_list.p4": (
        "Weber fornisce una lista di ricambi specifica per la macchina a titolo "
        "indicativo, senza fornitura di materiale né installazione salvo ordine separato."
    ),

    # Annex 5 - Blade Solutions
    "annex5.title": "ALLEGATO 5 - SOLUZIONI PER LAME",
    "annex5.tagline": "Consulenza applicativa, affilatura e programma per lame.",
    "annex5.intro": (
        "Il modulo Soluzioni per Lame supporta la corretta selezione, disponibilità, "
        "utilizzo e gestione delle lame Weber, incluso il principio «lama giusta, "
        "applicazione giusta»."
    ),
    "annex5.discount.title": "S603 Partnership di Fornitura Lame",
    "annex5.discount.p1": (
        "Qualora il Cliente selezioni l'opzione Partnership per le Lame, le parti "
        "concordano un catalogo definito di riferimenti di lama, quantità, prezzi, "
        "calendario degli ordini e durata commerciale nel Programma Lame."
    ),
    "annex5.discount.p2": (
        "Eventuali budget mensili fissi o piani rateali, previsioni di consumo, impegni "
        "minimi, periodi di blocco del prezzo, sconti, ordini di rilascio, programmi di "
        "reso o modalità di consegna speciali si applicano esclusivamente se specificati "
        "in detto programma."
    ),
    "annex5.stock.title": "Accordo di Stock Lame",
    "annex5.stock.p1": (
        "Ove sia selezionato un accordo di stock lame, le parti definiscono i "
        "riferimenti, le quantità, il metodo di riapprovvigionamento, l'ubicazione dello "
        "stock e la titolarità nel programma sottoscritto."
    ),
    "annex5.stock.p2": (
        "Le quantità acquistate o consegnate devono essere contabilizzate distintamente "
        "dal consumo stimato o dallo stock interno di lame."
    ),
    "annex5.sharpening.title": "S602 Valutazione dell'Affilatura",
    "annex5.sharpening.p1": (
        "Weber valuta l'approccio di affilatura attuale del Cliente, i processi, i "
        "parametri delle macchine e i potenziali miglioramenti del controllo qualità o "
        "della manipolazione, nell'ambito concordato."
    ),
    "annex5.application.title": "S601 Consulenza Applicativa Lame",
    "annex5.application.p1": (
        "Weber esamina con il Cliente l'applicazione di taglio selezionata, le "
        "caratteristiche del prodotto, la configurazione di taglio e la geometria o "
        "specifica rilevante della lama."
    ),
    "annex5.application.p2": (
        "Risultato: un insieme documentato di raccomandazioni tecniche per una "
        "combinazione lama/applicazione idonea, soggette a verifica nell'applicazione "
        "reale."
    ),

    # Annex 6 - Training & Optimization
    "annex6.title": "ALLEGATO 6 - FORMAZIONE E OTTIMIZZAZIONE",
    "annex6.tagline": (
        "Formazione degli operatori e dei tecnici di manutenzione, ottimizzazione della "
        "linea e audit EPIP."
    ),
    "annex6.intro": (
        "Il modulo Formazione e Ottimizzazione offre attività selezionate destinate a "
        "migliorare l'esercizio delle macchine, la capacità di manutenzione e le "
        "prestazioni produttive."
    ),
    "annex6.operator.title": "S501 Formazione Operatori",
    "annex6.operator.p1": (
        "Formazione destinata agli operatori sull'uso sicuro ed efficiente "
        "dell'Attrezzatura definita, comprese le procedure operative selezionate, le "
        "regolazioni, le pratiche di pulizia e i controlli operativi di base, nella "
        "misura appropriata."
    ),
    "annex6.maintenance.title": "S502 Formazione Tecnici di Manutenzione",
    "annex6.maintenance.p1": (
        "Formazione destinata al team di manutenzione del Cliente sull'architettura "
        "della macchina, sui controlli preventivi, sul riconoscimento dei guasti, sulla "
        "risoluzione sicura dei problemi e sulle procedure di manutenzione, entro i "
        "permessi di accesso concordati."
    ),
    "annex6.optimization.title": "S702 Ottimizzazione Linea",
    "annex6.optimization.p1": (
        "Weber esamina i vincoli tecnici e produttivi individuati e può raccomandare o "
        "eseguire miglioramenti concordati delle impostazioni della macchina o del "
        "processo entro l'ambito accettato."
    ),
    "annex6.optimization.p2": (
        "Eventuali aggiornamenti capitali o interventi di riparazione restano separati."
    ),
    "annex6.epip.title": "S701 Audit EPIP / Attrezzature",
    "annex6.epip.p1": (
        "Weber esegue la valutazione approfondita dell'Attrezzatura selezionata o "
        "l'audit in stile EPIP sulle linee di produzione specificate e fornisce un "
        "rapporto di valutazione."
    ),
    "annex6.epip.p2": (
        "Il rapporto distingue la condizione osservata, le azioni prioritarie, le "
        "riparazioni raccomandate e le opportunità di miglioramento."
    ),

    # Annex 7 - Digital Services
    "annex7.title": "ALLEGATO 7 - SERVIZI DIGITALI",
    "annex7.tagline": "Factory Cockpit, revisioni delle prestazioni, revisioni MRO e gestione dedicata dell'account.",
    "annex7.intro": (
        "Il modulo Servizi Digitali offre servizi selezionati di monitoraggio digitale, "
        "revisione delle prestazioni e gestione dell'account."
    ),
    "annex7.cockpit.title": "S801 Factory Cockpit / Monitoraggio",
    "annex7.cockpit.p1": (
        "Ove disponibile e selezionato, Weber fornisce la connessione o l'accesso "
        "concordati alla funzionalità designata Factory Cockpit o al monitoraggio "
        "digitale supportato per l'Attrezzatura idonea."
    ),
    "annex7.cockpit.p2": (
        "L'architettura di connessione, la disponibilità del servizio, la conservazione "
        "dei dati, i diritti di accesso e le responsabilità in materia di cybersicurezza "
        "sono definiti nelle condizioni del servizio digitale."
    ),
    "annex7.performance.title": "S802 Revisione delle Prestazioni e Report di Tendenza",
    "annex7.performance.p1": (
        "Weber può predisporre o riesaminare le informazioni concordate sulle prestazioni "
        "dell'Attrezzatura, le tendenze operative e le aree di follow-up individuate "
        "sulla base dei dati resi disponibili."
    ),
    "annex7.performance.p2": (
        "I valori possono essere influenzati dalla qualità dei dati, dalle pratiche "
        "operative, dal mix di prodotti e da sistemi di terzi. I report hanno natura "
        "analitica e non costituiscono garanzie delle prestazioni produttive."
    ),
    "annex7.mro.title": "S803 Revisione MRO Servizio / Ricambi",
    "annex7.mro.p1": (
        "Weber può riesaminare la spesa concordata per i servizi e l'utilizzo dei ricambi "
        "rispetto a un riferimento MRO definito o a un obiettivo di pianificazione "
        "concordato."
    ),
    "annex7.mro.p2": (
        "I corrispettivi fissi Guardian, gli interventi di manutenzione effettivi e i "
        "ricambi consumati restano elementi dati distinti; non si applicano duplicazioni "
        "di costi né si desumono guasti dai totali delle fatture."
    ),
    "annex7.account.title": "S105 Revisioni Account Dedicato",
    "annex7.account.p1": (
        "Ove selezionato, un referente account o After-Sales assegnato coordina revisioni "
        "periodiche dell'erogazione concordata del servizio, delle attività completate, "
        "delle azioni aperte e dei requisiti futuri."
    ),

    # Configuration Summary and Signatures
    "summary.title": "RIEPILOGO CONFIGURAZIONE GUARDIAN",
    "summary.intro": (
        "Il seguente riepilogo conferma la configurazione Guardian acquistata dal Cliente "
        "ai sensi del presente Accordo."
    ),
    "summary.customer": "Cliente",
    "summary.site": "Sede",
    "summary.start": "Inizio del contratto",
    "summary.term": "Durata del contratto",
    "summary.equipment": "Attrezzatura coperta",
    "summary.equipment.value": "{{Number_Of_Machines}} macchine / {{Number_Of_Lines}} linee di produzione",
    "summary.value": "Valore annuale / del contratto",
    "summary.scope.title": "GUARDIAN DEL CLIENTE",
    "summary.scope.h_module": "Modulo Guardian",
    "summary.scope.h_scope": "Ambito selezionato",
    "summary.signatures.title": "FIRME",
    "summary.signatures.intro": (
        "Firmando il presente Accordo, le Parti confermano l'accettazione dell'Accordo "
        "Quadro e di tutti gli Allegati indicati nell'Allegato 1 come applicabili."
    ),
    "summary.signatures.company": "Società",
    "summary.signatures.customer": "Per il Cliente",
    "summary.signatures.weber": "Per Weber",
    "summary.signatures.name": "Nome",
    "summary.signatures.position": "Carica",
    "summary.signatures.place": "Luogo",
    "summary.signatures.date": "Data",
    "summary.signatures.signature": "Firma",
}
