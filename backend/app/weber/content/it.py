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
    "module.maintenance_inspection": "Manutenzione e Ispezione",
    "module.service_support": "Assistenza di Servizio",
    "module.parts_availability": "Ricambi e Disponibilità",
    "module.blade_solutions": "Soluzioni per Lame",
    "module.training_optimization": "Formazione e Ottimizzazione",
    "module.digital_services": "Servizi Digitali",

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
    "master.title": "ACCORDO QUADRO WEBER GUARDIAN",
    "master.kv.agreement_no": "N.° d'accordo",
    "master.kv.offer_no": "N.° d'offerta",
    "master.kv.offer_date": "Data dell'offerta",
    "master.kv.start_date": "Data di inizio del contratto",
    "master.kv.term": "Durata iniziale del contratto",
    "master.kv.billing": "Frequenza di fatturazione",
    "master.between": "TRA",
    "master.weber_definition": "di seguito denominato «Weber».",
    "master.customer_definition": "di seguito denominato il «Cliente».",
    "master.parties": "Weber e il Cliente sono individualmente definiti una «Parte» e collettivamente le «Parti».",

    # 1. PURPOSE OF THE AGREEMENT
    "master.clause1.title": "1. FINALITÀ DELL'ACCORDO",
    "master.clause1.p1": (
        "La finalità del presente Accordo Guardian è sostenere un funzionamento affidabile, "
        "efficiente ed economicamente sostenibile dell'attrezzatura Weber del Cliente per "
        "l'intero ciclo di vita."
    ),
    "master.clause1.p2": (
        "Guardian è un programma postventa modulare. A seconda dei moduli selezionati dal "
        "Cliente, l'Accordo può comprendere servizi di ispezione e manutenzione preventiva, "
        "assistenza tecnica, servizi sui ricambi, soluzioni per lame, servizi di formazione e "
        "ottimizzazione e servizi digitali."
    ),
    "master.clause1.p3": "Sono inclusi esclusivamente i servizi espressamente indicati negli Allegati applicabili del presente Accordo.",
    "master.clause1.goals_intro": "L'obiettivo del programma Guardian è:",
    "master.clause1.goals": [
        "migliorare l'affidabilità e la disponibilità dell'Attrezzatura;",
        "sostenere la manutenzione preventiva e l'identificazione precoce dei problemi tecnici;",
        "ridurre i fermi non pianificati evitabili;",
        "favorire una pianificazione della manutenzione e una spesa prevedibili;",
        "garantire l'accesso all'esperienza tecnica di Weber;",
        "ottimizzare la gestione dei ricambi e delle lame;",
        "migliorare le pratiche di esercizio e manutenzione; e",
        "sostenere l'ottimizzazione continua dell'Attrezzatura installata del Cliente.",
    ],
    "master.clause1.exclusion": (
        "Nessun servizio, sconto, impegno di risposta o altro beneficio si intende incluso "
        "a meno che non sia espressamente previsto nel presente Acuerdo o in un Allegato che "
        "ne faccia parte."
    ),

    # 2. CONTRACT DOCUMENTS AND MODULAR STRUCTURE
    "master.clause2.title": "2. DOCUMENTI CONTRATTUALI E STRUTTURA MODULARE",
    "master.clause2.p1": (
        "Il presente Accordo è composto dal presente Accordo Quadro e dagli Allegati elencati "
        "di seguito selezionati per il Cliente."
    ),
    "master.clause2.annexes": [
        "Allegato 1 - Attrezzatura e condizioni commerciali: sempre applicabile.",
        "Allegato 2 - Manutenzione e Ispezione: applicabile solo se viene selezionato il modulo Manutenzione e Ispezione.",
        "Allegato 3 - Assistenza di Servizio: applicabile solo se viene selezionato il modulo Assistenza di Servizio.",
        "Allegato 4 - Ricambi e Disponibilità: applicabile solo se viene selezionato il modulo Ricambi e Disponibilità.",
        "Allegato 5 - Soluzioni per Lame: applicabile solo se viene selezionato il modulo Soluzioni per Lame.",
        "Allegato 6 - Formazione e Ottimizzazione: applicabile solo se viene selezionato il modulo Formazione e Ottimizzazione.",
        "Allegato 7 - Servizi Digitali: applicabile solo se viene selezionato il modulo Servizi Digitali.",
    ],
    "master.clause2.p2": "Gli Allegati applicabili fanno parte integrante del presente Accordo.",
    "master.clause2.p3": (
        "I servizi si applicano esclusivamente alle macchine, alle linee di produzione, ai "
        "moduli e alle sedi indicati nell'Allegato 1, salvo diverso accordo scritto."
    ),
    "master.clause2.p4": (
        "In caso di conflitto tra i documenti che compongono il presente Accordo, si applica "
        "il seguente ordine di prelazione:"
    ),
    "master.clause2.precedence": [
        "Allegato 1 - Attrezzatura e condizioni commerciali;",
        "l'Allegato specifico del servizio interessato;",
        "il presente Accordo Quadro; e",
        "le Condizioni Generali di Vendita applicabili di Weber.",
    ],
    "master.clause2.p5": (
        "Le deroghe specifiche del Cliente espressamente indicate nell'Allegato 1 prevalgono "
        "sulle disposizioni standard relative alla stessa materia."
    ),

    # 3. DEFINITIONS
    "master.clause3.title": "3. DEFINIZIONI",
    "master.clause3.definitions": [
        "Attrezzatura: le macchine, i moduli, i sistemi o altre attrezzature elencate espressamente nell'Allegato 1.",
        "Ispezione: la valutazione dello stato effettivo dell'Attrezzatura al fine di identificare l'usura, le anomalie, la manutenzione richiesta e le azioni necessarie a sostenerne la futura operatività.",
        "Manutenzione preventiva: interventi programmati volti a ridurre il deterioramento e il rischio di guasto, compresi regolazione, lubrificazione, pulizia, sostituzione di parti soggette a usura definite e altre attività espressamente incluse nell'ambito di servizio applicabile.",
        "Manutenzione correttiva / Riparazione: interventi volti a ripristinare lo stato operativo richiesto dell'Attrezzatura a seguito di un guasto, un'avaria o un difetto identificato.",
        "Parti soggette a usura: componenti che, in funzione della loro destinazione e a seconda delle condizioni di esercizio e di utilizzo, richiedono una sostituzione periodica.",
        "Ricambi: componenti di sostituzione forniti per l'Attrezzatura.",
        "Servizi: i servizi Guardian espressamente selezionati e descritti negli Allegati applicabili.",
        "Visita di servizio: una visita fisica concordata del personale Weber o di un partner di servizio autorizzato Weber presso la sede del Cliente.",
        "Assistenza remota: assistenza tecnica fornita senza visita fisica, compreso telefono, posta elettronica, comunicazione digitale e, ove disponibile e autorizzata, connessione remota all'Attrezzatura.",
        "Anno contrattuale: ogni periodo consecutivo di dodici mesi che decorre dalla Data di inizio del contratto.",
    ],

    # 4. EQUIPMENT COVERED
    "master.clause4.title": "4. ATTREZZATURA COPERTA",
    "master.clause4.p1": "L'Accordo Guardian si applica esclusivamente all'Attrezzatura elencata nell'Allegato 1.",
    "master.clause4.p2": "L'Allegato 1 indicherà, ove applicabile:",
    "master.clause4.identify": [
        "la linea di produzione del Cliente;",
        "il riferimento della macchina Weber;",
        "il numero di serie;",
        "il tipo di attrezzatura;",
        "i moduli inclusi;",
        "la frequenza di servizio;",
        "il tempo pianificato di ispezione o di servizio;",
        "i moduli Guardian selezionati;",
        "il prezzo di servizio applicabile; e",
        "ogni condizione commerciale specifica della macchina.",
    ],
    "master.clause4.p3": (
        "Il Cliente notificherà per iscritto a Weber qualsiasi spostamento, modifica "
        "sostanziale, alienazione o vendita dell'Attrezzatura coperta dal presente Accordo."
    ),
    "master.clause4.p4": (
        "Qualora l'Attrezzatura sia venduta o trasferita stabilmente a un'altra entità "
        "giuridica o sede, la prosecuzione dell'Accordo Guardian sarà subordinata alla "
        "conferma scritta di Weber."
    ),
    "master.clause4.p5": "Le Parti possono aggiungere o rimuovere Attrezzatura durante la vigenza del contratto mediante modifica scritta dell'Allegato 1.",

    # 5. GENERAL SERVICE PRINCIPLES
    "master.clause5.title": "5. PRINCIPI GENERALI DI SERVIZIO",
    "master.clause5.p1": (
        "Weber eseguirà i Servizi selezionati con personale adeguatamente qualificato e in "
        "conformità con gli standard tecnicamente generalmente accettati e le procedure di "
        "servizio Weber applicabili all'Attrezzatura interessata."
    ),
    "master.clause5.p2": "Weber può avvalersi di società affiliate qualificate o di partner di servizio autorizzati Weber per l'esecuzione dei Servizi.",
    "master.clause5.p3": (
        "Weber determina il numero e la qualifica dei tecnici ragionevolmente necessari per "
        "l'attività di servizio applicabile, tenendo conto della configurazione "
        "dell'Attrezzatura e dell'ambito dei lavori."
    ),
    "master.clause5.p4": "L'Accordo Guardian non costituisce una garanzia che l'Attrezzatura opererà senza interruzioni né guasti.",
    "master.clause5.excluded_intro": (
        "Salvo espressa inclusione in un Allegato applicabile, i seguenti non sono inclusi "
        "nel corrispettivo fisso Guardian:"
    ),
    "master.clause5.excluded": [
        "riparazioni correttive;",
        "parti di sostituzione;",
        "parti soggette a usura e parti di consumo;",
        "miglioramenti o modifiche;",
        "attrezzature di terzi;",
        "lavori oltre le ore di servizio concordate;",
        "interventi di emergenza;",
        "trasferte aggiuntive;",
        "mezzi di accesso speciali;",
        "materiali di produzione;",
        "strumentazioni speciali non richieste abitualmente per l'Attrezzatura Weber interessata; e",
        "lavori derivanti da uso improprio, danni, cause esterne o modifiche non approvate da Weber.",
    ],
    "master.clause5.p5": "Tali servizi possono essere preventivati e ordinati separatamente.",

    # 6. CUSTOMER COOPERATION
    "master.clause6.title": "6. COLLABORAZIONE DEL CLIENTE",
    "master.clause6.p1": "Il Cliente fornirà la collaborazione ragionevolmente richiesta affinché Weber possa eseguire i Servizi.",
    "master.clause6.p2": "In particolare, il Cliente si assicura che:",
    "master.clause6.obligations": [
        "il personale Weber abbia accesso sicuro e tempestivo all'Attrezzatura interessata;",
        "l'Attrezzatura sia disponibile all'orario concordato;",
        "l'Attrezzatura si trovi in uno stato ragionevolmente pulito e accessibile;",
        "la produzione possa essere interrotta ove necessario per i lavori concordati;",
        "le utenze e le connessioni tecniche richieste per i lavori, compresi elettricità, aria compressa, acqua, accesso alla rete o accesso VPN ove applicabile, siano disponibili;",
        "sia disponibile personale del Cliente idoneo quando sia richiesta assistenza;",
        "sia disponibile prodotto originale sufficiente quando sia richiesta una prova di produzione o funzionale;",
        "Weber sia informata in anticipo dei guasti noti, delle condizioni di esercizio anomale o dei requisiti di sicurezza;",
        "tutti i requisiti di salute e sicurezza specifici della sede siano comunicati a Weber prima dell'inizio dei lavori; e",
        "sia disponibile un rappresentante del Cliente con adeguati poteri per approvare lavori aggiuntivi o la sostituzione di componenti quando necessario.",
    ],
    "master.clause6.p3": (
        "Qualunque ritardo, tempo di attesa o spesa aggiuntiva derivante "
        "dall'inadempimento da parte del Cliente di tali obblighi può essere addebitata "
        "separatamente in conformità alle tariffe Weber applicabili."
    ),

    # 7. SCHEDULING
    "master.clause7.title": "7. PIANIFICAZIONE",
    "master.clause7.p1": (
        "Le ispezioni pianificate, le visite di manutenzione, la formazione e gli altri "
        "Servizi programmati saranno coordinati tra Weber e il Cliente."
    ),
    "master.clause7.p2": "Weber adotterà i ragionevoli sforzi necessari per informare il Cliente con anticipo della data prevista.",
    "master.clause7.p3": "Il periodo di preavviso applicabile, ove specificamente concordato, sarà indicato nell'Allegato interessato o nell'Allegato 1.",
    "master.clause7.p4": "Se una delle Parti non è in grado di svolgere un'attività concordata alla data programmata, ne informerà l'altra Parte il prima ragionevolmente possibile.",
    "master.clause7.p5": (
        "Quando una visita programmata non può essere effettuata per cause attribuibili al "
        "Cliente, Weber può addebitare i costi ragionevolmente sostenuti, comprese "
        "trasferte, pernottamento, tempo di attesa e capacità di personale riservata."
    ),

    # 8. ADDITIONAL WORK IDENTIFIED DURING A SERVICE ACTIVITY
    "master.clause8.title": "8. LAVORI AGGIUNTIVI IDENTIFICATI DURANTE UN'ATTIVITÀ DI SERVIZIO",
    "master.clause8.p1": "Quando un'ispezione, un'attività di manutenzione, un audit o altro servizio Guardian identifica lavori aggiuntivi, Weber ne informerà il Cliente.",
    "master.clause8.p2": "Salvo che l'Allegato 1 preveda espressamente diversamente, tali lavori aggiuntivi non fanno automaticamente parte del corrispettivo fisso Guardian.",
    "master.clause8.p3": (
        "La manutenzione correttiva, le riparazioni, le modifiche, i miglioramenti e la "
        "sostituzione di parti identificate durante un'ispezione richiedono "
        "l'autorizzazione del Cliente."
    ),
    "master.clause8.p4": "Quando opportuno, Weber può emettere un preventivo separato o una raccomandazione di ricambi a seguito dell'attività di servizio.",
    "master.clause8.p5": (
        "Nessun lavoro aggiuntivo soggetto ad addebito sarà intenzionalmente eseguito senza "
        "l'autorizzazione del Cliente, salvo quando sia ragionevolmente necessario agire "
        "tempestivamente per prevenire un rischio imminente per la sicurezza e tale azione "
        "sia consentita dalla legge applicabile e dal regolamento della sede."
    ),

    # 9. PRICES AND PAYMENT
    "master.clause9.title": "9. PREZZI E PAGAMENTO",
    "master.clause9.p1": "I prezzi applicabili all'Accordo Guardian sono indicati nell'Allegato 1.",
    "master.clause9.p2": "Salvo espressa indicazione contraria, tutti i prezzi sono al netto di IVA e di altre imposte applicabili.",
    "master.clause9.p3": (
        "La valuta applicabile, la frequenza di fatturazione, le condizioni di pagamento, le "
        "condizioni di trasferta, le condizioni di trasporto, gli sconti e le tariffe di "
        "servizio aggiuntive sono quelle specificate nell'Allegato 1 o nell'Allegato del "
        "servizio interessato."
    ),
    "master.clause9.p4": "I corrispettivi ricorrenti di Guardian saranno fatturati secondo la frequenza di fatturazione indicata nell'Allegato 1.",
    "master.clause9.p5": (
        "Servizi, materiali e spese non inclusi nel corrispettivo Guardian concordato saranno "
        "fatturati separatamente alle tariffe concordate applicabili."
    ),
    "master.clause9.p6": "Weber può adeguare i prezzi ricorrenti in conformità con il meccanismo di adeguamento annuale dei prezzi indicato nell'Allegato 1.",
    "master.clause9.p7": (
        "Qualunque sconto concordato si applica esclusivamente alle categorie espressamente "
        "indicate nell'Allegato interessato e non è cumulabile con altri sconti salvo "
        "espressa convenzione."
    ),

    # 10. PARTS AND MATERIALS
    "master.clause10.title": "10. PARTI E MATERIALI",
    "master.clause10.p1": (
        "Salvo che siano specificamente inclusi nell'Allegato 1 o in un Allegato di servizio "
        "applicabile, i ricambi, le parti soggette a usura, le lame, i lubrificanti e gli "
        "altri materiali non sono inclusi nel corrispettivo di servizio Guardian."
    ),
    "master.clause10.p2": (
        "Le parti fornite da Weber saranno fatturate al prezzo applicabile alla data di "
        "fornitura, al netto di qualunque sconto Guardian espressamente concordato in virtù "
        "dell'Allegato 4 o dell'Allegato 5."
    ),
    "master.clause10.p3": (
        "Quando i componenti sostituiti sono messi a disposizione del Cliente per "
        "l'ispezione, il Cliente è responsabile del loro successivo smaltimento, salvo "
        "diverso accordo."
    ),
    "master.clause10.p4": (
        "Weber non risponde di difetti, danni, prestazioni ridotte o effetti consecutivi "
        "causati da componenti non originali, modifiche non autorizzate o lavori eseguiti "
        "da terzi, nella misura consentita dalla legge applicabile."
    ),
    "master.clause10.p5": (
        "La proprietà dei beni forniti rimarrà a Weber fino al pieno pagamento, ove "
        "consentito dalle condizioni locali e dalla legge applicabile."
    ),

    # 11. ACCEPTANCE AND SERVICE REPORTING
    "master.clause11.title": "11. ACCETTAZIONE E RENDICONTAZIONE DEI SERVIZI",
    "master.clause11.p1": (
        "Quando la natura di un Servizio consente la verifica funzionale, il Cliente "
        "fornirà a Weber un'opportunità ragionevole di provare l'Attrezzatura a seguito "
        "del completamento dell'attività."
    ),
    "master.clause11.p2": (
        "Quando il Cliente identifica una deficienza sostanziale nell'esecuzione di un "
        "Servizio, ne informerà Weber senza indebito ritardo e fornirà informazioni "
        "sufficienti per consentire a Weber di valutare la questione."
    ),
    "master.clause11.p3": (
        "Se un Servizio è dimostrabilmente non stato eseguito in conformità all'ambito "
        "concordato e Weber è responsabile della deficienza, Weber dovrà, come rimedio "
        "principale, rieseguire o correggere il Servizio interessato entro un termine "
        "ragionevole."
    ),
    "master.clause11.p4": (
        "I rapporti di servizio, i rapporti di ispezione, i rapporti di audit e le "
        "raccomandazioni documentano lo stato riscontrato al momento dell'attività e non "
        "costituiscono una garanzia delle prestazioni future della macchina."
    ),

    # 12. WARRANTY AND LIABILITY
    "master.clause12.title": "12. GARANZIA E RESPONSABILITÀ",
    "master.clause12.p1": "Weber eseguirà i Servizi con la diligenza e la competenza professionale ragionevoli.",
    "master.clause12.p2": (
        "La responsabilità di Weber è regolata dalle disposizioni imperative della legge "
        "applicabile e dalle Condizioni Generali applicabili di Weber."
    ),
    "master.clause12.p3": (
        "Nella massima misura consentita dalla legge, Weber non risponde dei danni indiretti "
        "o consecutivi, compresa la perdita di produzione, la perdita di profitto, la "
        "perdita di affari o altri danni commerciali indiretti, salvo che tale limitazione "
        "sia vietata dalla legge applicabile."
    ),
    "master.clause12.p4": "Nessuna disposizione del presente Acuerdo esclude la responsabilità che non possa legalmente essere esclusa né limitata.",
    "master.clause12.p5": (
        "Quando un inadempimento o un ritardo deriva da circostanze fuori dal ragionevole "
        "controllo di Weber, compreso l'inadempimento o il ritardo di fornitori, disguidi "
        "di trasporto, azioni sindacali, eventi naturali, misure governative, incidenti "
        "informatici, epidemie o altri eventi di forza maggiore, il periodo di esecuzione "
        "interessato sarà prorogato nella misura ragionevolmente necessaria."
    ),

    # 13. CONTRACT TERM AND RENEWAL
    "master.clause13.title": "13. DURATA E RINNOVO DEL CONTRATTO",
    "master.clause13.p1": "Il presente Accordo entra in vigore alla Data di inizio del contratto indicata nell'Allegato 1.",
    "master.clause13.term": "Durata iniziale",
    "master.clause13.renewal": "Durata di rinnovo",
    "master.clause13.notice": "Periodo di preavviso",
    "master.clause13.p2": (
        "Salvo quanto indicato nell'Allegato 1, l'Accordo sarà rinnovato automaticamente "
        "per periodi di rinnovo successivi, salvo disdetta scritta entro il periodo di "
        "preavviso applicabile."
    ),
    "master.clause13.p3": (
        "La risoluzione o la scadenza dell'Accordo Quadro comporta la cessazione di tutti "
        "gli Allegati di servizio, salvo espressa diversa convenzione."
    ),
    "master.clause13.p4": "I singoli servizi opzionali possono avere date di inizio o di scadenza diverse ove espressamente indicato nell'Allegato interessato.",

    # 14. CHANGES TO THE AGREEMENT
    "master.clause14.title": "14. MODIFICHE ALL'ACCORDO",
    "master.clause14.p1": (
        "Le modifiche all'Attrezzatura coperta, alla frequenza di servizio, ai moduli "
        "Guardian, agli sconti, ai livelli di servizio, ai prezzi o ad altre condizioni "
        "contrattuali sostanziali devono essere documentate per iscritto."
    ),
    "master.clause14.p2": "Un Allegato aggiornato generato e accettato da entrambe le Parti può costituire tale modifica scritta.",

    # 15. CONFIDENTIALITY
    "master.clause15.title": "15. RISERVATEZZA",
    "master.clause15.p1": (
        "Ciascuna Parte manterrà riservate tutte le informazioni commerciali, tecniche e "
        "operative non pubbliche ricevute dall'altra Parte in relazione al presente Accordo."
    ),
    "master.clause15.p2": "Tali informazioni saranno utilizzate esclusivamente per l'esecuzione e l'amministrazione del rapporto Guardian.",
    "master.clause15.p3": "Questo obbligo non si applica alle informazioni che:",
    "master.clause15.exceptions": [
        "sono già legittimamente di dominio pubblico;",
        "erano legittimamente note alla Parte ricevente prima della divulgazione;",
        "sono ricevute legittimamente da un terzo senza restrizioni di riservatezza; o",
        "devono essere divulgate per legge o per disposizione di un'autorità competente.",
    ],

    # 16. INTELLECTUAL PROPERTY
    "master.clause16.title": "16. PROPRIETÀ INTELLETTUALE",
    "master.clause16.p1": (
        "Tutti i diritti di proprietà intellettuale sulla documentazione Weber, sui metodi "
        "di servizio, sulle checklist, sul software, sulle informazioni tecniche, sui "
        "materiali di formazione, sulle analisi e su altri contenuti proprietari di Weber "
        "restano di proprietà di Weber o del titolare dei diritti applicabili."
    ),
    "master.clause16.p2": "Il Cliente può utilizzare internamente la documentazione fornita ai sensi del presente Accordo per l'esercizio e la manutenzione della propria Attrezzatura.",
    "master.clause16.p3": "Nessun diritto di proprietà intellettuale è trasferito al Cliente salvo espressa convenzione scritta.",

    # 17. ASSIGNMENT AND SERVICE PARTNERS
    "master.clause17.title": "17. CESSIONE E PARTNER DI SERVIZIO",
    "master.clause17.p1": "Weber può adempiere ai propri obblighi tramite società del gruppo Weber o partner di servizio qualificati e autorizzati Weber.",
    "master.clause17.p2": "Weber può cedere i diritti e gli obblighi derivanti dal presente Accordo a un'altra società del gruppo Weber, fatte salve le disposizioni di legge applicabili.",
    "master.clause17.p3": (
        "Il Cliente non può cedere il presente Accordo a un terzo senza il consenso previo "
        "per iscritto di Weber, consenso che non sarà ingiustificatamente rifiutato quando "
        "la prosecuzione del rapporto contrattuale sia commercialmente e tecnicamente "
        "fattibile."
    ),

    # 18. GOVERNING LAW AND JURISDICTION
    "master.clause18.title": "18. LEGGE APPLICABILE E GIURISDICZIONE",
    "master.clause18.law": "Legge applicabile",
    "master.clause18.jurisdiction": "Foro",
    "master.clause18.p1": "Le disposizioni di cui sopra sono in ogni caso soggette alla legge imperativa applicabile.",

    # 19. GENERAL PROVISIONS
    "master.clause19.title": "19. DISPOSIZIONI GENERALI",
    "master.clause19.p1": (
        "Se una qualsiasi disposizione del presente Acuerdo dovesse essere dichiarata nulla "
        "o inapplicabile, le disposizioni rimanenti restano pienamente valide ed efficaci."
    ),
    "master.clause19.p2": "Il fatto che una delle Parti non eserciti un diritto contrattuale non costituisce rinuncia a tale diritto.",
    "master.clause19.p3": (
        "Il presente Accordo e i relativi Allegati applicabili costituiscono l'accordo tra "
        "le Parti riguardo ai Servizi Guardian qui descritti e sostituiscono proposte o "
        "intese precedenti relative specificamente allo stesso ambito di servizio, salvo che "
        "siano espressamente incorporate."
    ),
    "master.clause19.p4": "Le modifiche saranno formalizzate per iscritto.",
    "master.clause19.p5": (
        "Possono essere utilizzate firme elettroniche ove legalmente consentito, le quali "
        "avranno la stessa efficacia delle firme autografe."
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
    "annex2.tagline": "Ispezione, manutenzione preventiva e servizi sullo stato della macchina.",
    "annex2.purpose.title": "1. Finalità",
    "annex2.purpose.p1": (
        "Il modulo Manutenzione e Ispezione ha per oggetto la valutazione e il mantenimento "
        "dello stato dell'Attrezzatura indicata nell'Allegato 1, l'individuazione delle "
        "azioni tecniche richieste e il sostegno di un esercizio affidabile e della "
        "pianificazione della manutenzione."
    ),
    "annex2.purpose.p2": "Le attività esatte incluse dipendono dalle opzioni selezionate nella configurazione Guardian.",
    "annex2.inspection.title": "2. Ispezione",
    "annex2.inspection.p1": "Weber effettuerà ispezioni dell'Attrezzatura selezionata con la frequenza indicata nell'Allegato 1.",
    "annex2.inspection.p2": "Un'ispezione può includere, ove applicabile all'Attrezzatura selezionata:",
    "annex2.inspection.includes": [
        "verifica dello stato generale della macchina;",
        "ispezione basata sulla checklist specifica di Weber per la macchina o il modulo;",
        "verifica dei sensori e dei componenti elettrici rilevanti;",
        "ispezione di azionamenti, cinghie e componenti meccanici;",
        "ispezione dei componenti pneumatici;",
        "ispezione delle guarnizioni e delle scocche della macchina;",
        "verifica e regolazione dei componenti meccanicamente mobili ove ragionevolmente necessario;",
        "verifica delle regolazioni rilevanti della macchina;",
        "individuazione di usura o anomalie visibili;",
        "individuazione delle necessità di riparazione o manutenzione ancora pendenti;",
        "discussione delle anomalie note con il personale responsabile del Cliente; e",
        "verifica funzionale a seguito dell'ispezione ove opportuno.",
    ],
    "annex2.inspection.p3": (
        "Quando utile e tecnicamente possibile, Weber può verificare il processo di "
        "produzione utilizzando il prodotto originale del Cliente."
    ),
    "annex2.inspection.p4": (
        "L'apertura di aree specifiche protette della macchina, come le scocche di "
        "pesatura o di teste di taglio, sarà effettuata quando tecnicamente appropriata "
        "e concordata."
    ),
    "annex2.checklist.title": "3. Checklist della macchina",
    "annex2.checklist.p1": "Weber documenterà l'ispezione utilizzando la checklist di ispezione Weber applicabile.",
    "annex2.checklist.p2": "La checklist registra gli elementi ispezionati e il loro stato riscontrato al momento dell'ispezione.",
    "annex2.checklist.p3": (
        "La checklist ha natura di registro tecnico di servizio e non costituisce una "
        "certificazione che l'Attrezzatura sia priva di difetti o che non possano "
        "verificarsi guasti futuri."
    ),
    "annex2.report.title": "4. Rapporto di ispezione",
    "annex2.report.p1": "A seguito dell'ispezione, Weber fornirà un rapporto di ispezione che riassuma i principali rilievi.",
    "annex2.report.p2": "Il rapporto può includere:",
    "annex2.report.includes": [
        "rilievi sullo stato;",
        "usura identificata;",
        "manutenzione o riparazioni raccomandate;",
        "ricambi raccomandati;",
        "osservazioni tecniche;",
        "rischi identificati che richiedono ulteriore attenzione; e",
        "priorità o azioni successive raccomandate.",
    ],
    "annex2.report.p3": (
        "Quando opportuno, Weber può predisporre un preventivo separato per parti, "
        "riparazioni, miglioramenti o altre attività derivanti dall'ispezione."
    ),
    "annex2.preventive.title": "5. Manutenzione preventiva",
    "annex2.preventive.p1": "Weber eseguirà le attività di manutenzione preventiva espressamente definite per l'Attrezzatura nell'Allegato 1.",
    "annex2.preventive.p2": "La manutenzione preventiva può includere:",
    "annex2.preventive.includes": [
        "regolazione meccanica;",
        "lubrificazione;",
        "pulizia dei componenti tecnicamente rilevanti;",
        "sostituzione di filtri, guarnizioni o componenti soggetti a usura definiti;",
        "verifica e regolazione di azionamenti e cinghie;",
        "verifica degli elementi pneumatici;",
        "verifica dei componenti elettrici e dei sensori; e",
        "ulteriori attività di manutenzione preventiva specifiche della macchina indicate nel piano di manutenzione Weber applicabile.",
    ],
    "annex2.preventive.p3": (
        "Le parti di sostituzione, le parti soggette a usura e le parti di consumo non sono "
        "inclusi salvo che sia espressamente indicato nell'Allegato 1 o in un kit di "
        "manutenzione concordato."
    ),
    "annex2.kit.title": "6. Ricambi / kit di manutenzione",
    "annex2.kit.p1": (
        "Il kit di manutenzione conterrà esclusivamente le parti espressamente indicate nel "
        "preventivo applicabile o nel programma di attrezzatura."
    ),
    "annex2.kit.p2": "Il prezzo del kit sarà indicato separatamente nell'Allegato 1.",
    "annex2.kit.p3": "Le parti non utilizzate restano soggette alle condizioni commerciali indicate nell'Allegato 1.",
    "annex2.repairs.title": "7. Manutenzione aggiuntiva e riparazioni",
    "annex2.repairs.p1": (
        "Le riparazioni e la manutenzione correttiva identificate durante un'ispezione non "
        "sono incluse nel prezzo standard dell'ispezione, salvo specifica indicazione contraria."
    ),
    "annex2.repairs.p2": "Quando vengono raccomandati lavori aggiuntivi, Weber otterrà l'approvazione del Cliente o emetterà un preventivo separato.",
    "annex2.frequency.title": "8. Frequenza di ispezione",
    "annex2.frequency.value": "Frequenza",
    "annex2.frequency.planned": "Ispezioni pianificate per anno contrattuale",
    "annex2.frequency.p1": "Il calendario effettivo sarà coordinato tra Weber e il Cliente.",
    "annex2.hours.title": "9. Orario di servizio",
    "annex2.hours.p1": "I servizi saranno normalmente eseguiti durante: {{Standard_Service_Hours}}",
    "annex2.hours.p2": "I lavori richiesti oltre tale orario possono comportare costi aggiuntivi.",

    # Annex 3 - Service Support
    "annex3.title": "ALLEGATO 3 - ASSISTENZA DI SERVIZIO",
    "annex3.tagline": "Linea diretta, assistenza remota e risposta tecnica prioritaria.",
    "annex3.purpose.title": "1. Finalità",
    "annex3.purpose.p1": (
        "Il modulo Assistenza di Servizio consente al Cliente di accedere all'assistenza "
        "tecnica di Weber per l'Attrezzatura coperta dal presente Accordo."
    ),
    "annex3.purpose.p2": "Il livello di servizio esatto dipende dalle opzioni selezionate di seguito.",
    "annex3.hotline.title": "2. Linea diretta standard",
    "annex3.hotline.p1": "Il Cliente avrà accesso alla linea diretta di servizio Weber durante l'orario di assistenza applicabile.",
    "annex3.hotline.hours": "Orario di assistenza",
    "annex3.hotline.phone": "Telefono",
    "annex3.hotline.email": "Posta elettronica",
    "annex3.hotline.p2": "La linea diretta offre assistenza tecnica di primo livello e coordinamento.",
    "annex3.hotline.p3": (
        "Quando il problema non può essere risolto tramite la linea diretta, Weber può "
        "raccomandare l'Assistenza remota, una visita di servizio in loco, ricambi o "
        "altra azione tecnica."
    ),
    "annex3.hotline.p4": (
        "Il servizio in loco non è incluso per il solo fatto di disporre dell'assistenza "
        "della linea diretta standard, salvo espressa indicazione nell'Allegato 1."
    ),
    "annex3.remote.title": "3. Assistenza remota",
    "annex3.remote.p1": (
        "Quando tecnicamente disponibile e autorizzata dal Cliente, Weber può fornire "
        "diagnostica e assistenza tecnica remota."
    ),
    "annex3.remote.p2": (
        "Il Cliente fornirà le connessioni di rete, l'accesso VPN, l'autorizzazione degli "
        "utenti e le altre condizioni tecniche ragionevolmente necessarie per l'accesso "
        "remoto."
    ),
    "annex3.remote.p3": "L'Assistenza remota può includere:",
    "annex3.remote.includes": [
        "analisi remota dei guasti;",
        "verifica dello stato della macchina o delle informazioni diagnostiche;",
        "assistenza nelle verifiche dei parametri o della configurazione;",
        "supporto al personale di manutenimento del Cliente; e",
        "raccomandazioni per le azioni successive.",
    ],
    "annex3.remote.p4": "L'Assistenza remota non garantisce che un guasto possa essere corretto senza un intervento in loco.",
    "annex3.priority.title": "4. Risposta prioritaria",
    "annex3.priority.p1": (
        "Le richieste relative all'Attrezzatura coperta dal presente Accordo riceveranno "
        "una gestione prioritaria all'interno dell'organizzazione di servizio di Weber "
        "rispetto alle richieste standard senza contratto, fatte salve la disponibilità "
        "dei tecnici e il livello di servizio applicabile."
    ),
    "annex3.priority.target": "Obiettivo di prima risposta",
    "annex3.priority.p2": (
        "La Risposta prioritaria riguarda la prioritizzazione della richiesta di "
        "assistenza. Non costituisce un tempo di riparazione garantito, una disponibilità "
        "garantita della macchina né un tempo di arrivo in loco garantito, salvo espressa "
        "indicazione contraria nell'Allegato 1."
    ),

    # Annex 4 - Parts & Availability
    "annex4.title": "ALLEGATO 4 - RICAMBI E DISPONIBILITÀ",
    "annex4.tagline": "Condizioni commerciali sui ricambi, gestione prioritaria e scorta consigliata.",
    "annex4.purpose.title": "1. Finalità",
    "annex4.purpose.p1": (
        "Il modulo Ricambi e Disponibilità supporta la pianificazione strutturata dei "
        "ricambi e l'accesso ai ricambi originali Weber per l'Attrezzatura coperta dal "
        "presente Accordo."
    ),
    "annex4.discount.title": "2. Sconto sui ricambi",
    "annex4.discount.p1": (
        "Il Cliente riceverà il seguente sconto sui ricambi originali Weber idonei per "
        "l'Attrezzatura coperta dall'Accordo Guardian:"
    ),
    "annex4.discount.amount": "Sconto Guardian sui ricambi {{Parts_Discount}} %",
    "annex4.discount.p2": "Lo sconto si applica ai ricambi originali Weber, salvo indicazione contraria.",
    "annex4.discount.p3": "I seguenti possono essere esclusi:",
    "annex4.discount.excluded": [
        "parti in scambio (exchange);",
        "lame;",
        "articoli a prezzo speciale;",
        "prodotti di terzi;",
        "costi di trasporto e spedizione urgente;",
        "servizi e manodopera; e",
        "articoli già soggetti a un altro prezzo speciale o sconto.",
    ],
    "annex4.discount.p4": "Gli sconti non sono cumulabili salvo espressa convenzione.",
    "annex4.handling.title": "3. Gestione prioritaria",
    "annex4.handling.p1": (
        "Le richieste e gli ordini di parti relativi all'Attrezzatura coperta dal presente "
        "Accordo riceveranno una gestione prioritaria all'interno dell'organizzazione "
        "ricambi applicabile di Weber."
    ),
    "annex4.handling.p2": "La gestione prioritaria include l'accelerazione dell'elaborazione interna ove ragionevolmente possibile.",
    "annex4.handling.p3": (
        "Non costituisce un tempo di consegna garantito quando la parte richiesta non è "
        "disponibile a magazzino o quando la consegna dipende da fornitori esterni, dalla "
        "produzione o dal trasporto."
    ),
    "annex4.parts_list.title": "4. Elenco dei ricambi consigliati",
    "annex4.parts_list.p1": (
        "Weber fornirà, ove tecnicamente e commercialmente disponibile, un elenco di "
        "ricambi consigliati per l'Attrezzatura selezionata."
    ),
    "annex4.parts_list.categories": [
        "A - Articoli locali / immediatamente disponibili: parti normalmente disponibili presso l'organizzazione Weber responsabile.",
        "B - Articoli a magazzino centrale: parti normalmente disponibili presso il magazzino centrale di Weber.",
        "C - Articoli consigliati a magazzino del Cliente: ricambi critici o a maggiore rischio che Weber raccomanda al Cliente di mantenere localmente.",
        "D - Parti soggette a usura: parti che richiedono sostituzione in funzione dell'utilizzo.",
        "E - Parti su commessa / con tempi di fornitura prolungati: parti normalmente non tenute a magazzino e che possono richiedere produzione o tempi di approvvigionamento prolungati.",
    ],
    "annex4.parts_list.p2": (
        "L'elenco dei ricambi consigliati costituisce una raccomandazione basata sulla "
        "configurazione della macchina e sulle informazioni di servizio disponibili. Non è "
        "una garanzia che ogni possibile scenario di guasto sia coperto."
    ),
    "annex4.delivery.title": "5. Condizioni di consegna",
    "annex4.delivery.p1": "La disponibilità a magazzino e le condizioni di consegna sono soggette all'Allegato 1.",
    "annex4.delivery.condition": "Condizione di consegna standard",
    "annex4.delivery.threshold": "Soglia di trasporto gratuito",
    "annex4.delivery.courier": "Costi di spedizione urgente / corriere",
    "annex4.delivery.courier.value": "Fatturati separatamente, salvo diverso accordo.",

    # Annex 5 - Blade Solutions
    "annex5.title": "ALLEGATO 5 - SOLUZIONI PER LAME",
    "annex5.tagline": "Condizioni commerciali, disponibilità e assistenza tecnica per i programmi di lame di Weber.",
    "annex5.intro": (
        "Il modulo Soluzioni per Lame ha per oggetto il sostegno della corretta selezione, "
        "della disponibilità, dell'utilizzo e della gestione delle lame Weber, compreso il "
        "principio «Lama giusta, applicazione giusta»."
    ),
    "annex5.discount.title": "1. Sconto sulle lame",
    "annex5.discount.p1": "Il Cliente riceverà il seguente sconto Guardian sulle lame Weber idonee:",
    "annex5.discount.amount": "Sconto sulle lame {{Blade_Discount}} %",
    "annex5.discount.p2": (
        "Le lame applicabili, le sedi del Cliente, le macchine, le quantità impegnate e "
        "ogni prezzo speciale saranno elencati nel programma commerciale ove necessario."
    ),
    "annex5.discount.p3": (
        "Gli sconti sulle lame non sono cumulabili con altre promozioni sulle lame o "
        "prezzi speciali salvo espressa convenzione."
    ),
    "annex5.discount.p4": (
        "Quando vengono concordati prezzi delle lame a tempo definito, il termine "
        "applicabile e le condizioni di prezzo saranno indicati nell'Allegato 1."
    ),
    "annex5.stock.title": "2. Accordo sulle scorte",
    "annex5.stock.p1": "Weber e il Cliente possono stabilire un concetto di scorta di lame concordato in base al consumo previsto.",
    "annex5.stock.p2": "L'accordo sulle scorte definirà, ove applicabile:",
    "annex5.stock.defines": [
        "i riferimenti delle lame;",
        "la quantità di scorte concordata;",
        "la scorta minima;",
        "la scorta massima;",
        "il consumo annuo previsto;",
        "il metodo di riordino;",
        "la posizione delle scorte;",
        "la titolarità delle scorte;",
        "le condizioni di consegna; e",
        "la gestione delle scorte obsolete o non utilizzate.",
    ],
    "annex5.stock.p3": (
        "Il Cliente fornirà informazioni di consumo ragionevolmente accurate e informerà "
        "Weber delle variazioni sostanziali nella produzione o nella domanda di lame."
    ),
    "annex5.stock.p4": (
        "L'accordo sulle scorte è volto a migliorare la disponibilità ma non costituisce "
        "una garanzia incondizionata di approvvigionamento ininterrotto in circostanze "
        "fuori dal ragionevole controllo di Weber."
    ),
    "annex5.sharpening.title": "3. Valutazione dell'affilatura",
    "annex5.sharpening.p1": "Weber valuterà il processo e la capacità di affilatura delle lame del Cliente come concordato.",
    "annex5.sharpening.p2": "La valutazione può includere:",
    "annex5.sharpening.includes": [
        "le attrezzature di affilatura;",
        "il processo di affilatura;",
        "la manipolazione delle lame;",
        "lo stato delle lame;",
        "i parametri di rettifica;",
        "le pratiche di manutenzione;",
        "lo stoccaggio delle lame;",
        "la coerenza del processo; e",
        "opportunità di miglioramento.",
    ],
    "annex5.sharpening.p3": "Weber può formulare raccomandazioni a seguito della valutazione.",
    "annex5.sharpening.p4": (
        "Salvo specifica inclusione, l'attuazione di tali raccomandazioni, le riparazioni "
        "o le modifiche all'attrezzatura di affilatura e la formazione aggiuntiva non sono "
        "inclusi."
    ),
    "annex5.application.title": "4. Verifica dell'applicazione delle lame",
    "annex5.application.p1": (
        "Quando incluso nel programma di lame selezionato, Weber può verificare la "
        "combinazione lama-prodotto con l'obiettivo di sostenere il principio «Lama "
        "giusta, applicazione giusta»."
    ),
    "annex5.application.p2": (
        "Le raccomandazioni possono considerare il tipo di prodotto, le condizioni di "
        "taglio, la configurazione della macchina, la geometria della lama e i requisiti "
        "operativi."
    ),

    # Annex 6 - Training & Optimization
    "annex6.title": "ALLEGATO 6 - FORMAZIONE E OTTIMIZZAZIONE",
    "annex6.tagline": "Formazione degli operatori, formazione sulla manutenzione, ottimizzazione di linea e audit EPIP.",
    "annex6.intro": (
        "Il modulo Formazione e Ottimizzazione offre attività selezionate volte a "
        "migliorare l'esercizio delle macchine, la capacità di manutenzione e le "
        "prestazioni della produzione."
    ),
    "annex6.operator.title": "1. Formazione degli operatori",
    "annex6.operator.p1": "Weber fornirà formazione rivolta agli operatori per l'Attrezzatura selezionata.",
    "annex6.operator.p2": "Il contenuto della formazione può includere, a seconda della macchina e degli obiettivi concordati:",
    "annex6.operator.includes": [
        "la corretta operazione della macchina;",
        "le regolazioni di base della macchina;",
        "le routine operative;",
        "il cambio di prodotto;",
        "le verifiche a livello di operatore;",
        "le attenzioni relative a pulizia e ispezione;",
        "l'individuazione del comportamento anomalo della macchina; e",
        "le buone pratiche operative.",
    ],
    "annex6.operator.quantity": "Numero di sessioni / giorni",
    "annex6.operator.p3": "La formazione sarà erogata al personale designato dal Cliente.",
    "annex6.operator.p4": (
        "Salvo espressa indicazione contraria, la formazione non costituisce una "
        "certificazione formale del personale del Cliente."
    ),
    "annex6.maintenance.title": "2. Formazione sulla manutenzione",
    "annex6.maintenance.p1": "Weber fornirà formazione tecnica al personale di manutenzione del Cliente.",
    "annex6.maintenance.p2": "La formazione può includere:",
    "annex6.maintenance.includes": [
        "la costruzione della macchina e i suoi principi funzionali;",
        "la manutenzione preventiva;",
        "i punti di ispezione;",
        "l'identificazione delle parti soggette a usura;",
        "la metodologia di risoluzione dei problemi;",
        "la regolazione meccanica;",
        "i componenti elettrici o pneumatici rilevanti;",
        "la documentazione di manutenzione; e",
        "le pratiche di manutenzione raccomandate.",
    ],
    "annex6.maintenance.quantity": "Numero di sessioni / giorni",
    "annex6.optimization.title": "3. Ottimizzazione di linea",
    "annex6.optimization.p1": (
        "Weber effettuerà una verifica concordata della linea di produzione selezionata "
        "con l'obiettivo di identificare opportunità di miglioramento delle prestazioni."
    ),
    "annex6.optimization.p2": "L'attività può includere:",
    "annex6.optimization.includes": [
        "la verifica dei parametri della macchina;",
        "l'osservazione della produzione;",
        "l'analisi delle condizioni di esercizio;",
        "la verifica dell'interazione tra linee;",
        "l'individuazione dei vincoli alle prestazioni;",
        "la regolazione di parametri selezionati ove opportuno; e",
        "raccomandazioni per ulteriori miglioramenti.",
    ],
    "annex6.optimization.quantity": "Numero di attività di ottimizzazione",
    "annex6.optimization.p3": (
        "L'Ottimizzazione di linea non costituisce una garanzia di una produzione, di un "
        "rendimento, di un OEE, di una riduzione del giveaway o di altro miglioramento "
        "delle prestazioni determinati, salvo che venga espressamente concordato per "
        "iscritto un impegno prestazionale specifico."
    ),
    "annex6.epip.title": "4. Audit EPIP",
    "annex6.epip.p1": "Weber effettuerà un audit EPIP sull'Attrezzatura o sulle linee specificate nell'Allegato 1.",
    "annex6.epip.p2": (
        "L'audit comprenderà una valutazione della linea selezionata e un rapporto che "
        "identifichi i rilievi, le opportunità e le azioni prioritarie rilevanti."
    ),
    "annex6.epip.p3": (
        "Ove applicabile, i risultati saranno esaminati con il Cliente e inseriti nel "
        "piano d'azione Guardian in corso."
    ),
    "annex6.epip.quantity": "Numero di audit EPIP",
    "annex6.epip.lines": "Linee coperte",
    "annex6.epip.p4": (
        "Le azioni correttive, le riparazioni, i miglioramenti o le parti derivanti "
        "dall'audit non sono inclusi salvo espressa indicazione."
    ),
    "annex6.followup.title": "5. FOLLOW-UP",
    "annex6.followup.p1": (
        "Quando incluso nel pacchetto selezionato, Weber può svolgere incontri o chiamate "
        "di follow-up prima e dopo le attività selezionate per esaminare:"
    ),
    "annex6.followup.items": [
        "gli obiettivi concordati;",
        "le attività svolte;",
        "l'impatto riscontrato;",
        "le azioni pendenti;",
        "le priorità tecniche; e",
        "le azioni successive.",
    ],

    # Annex 7 - Digital Services
    "annex7.title": "ALLEGATO 7 - SERVIZI DIGITALI",
    "annex7.tagline": "Factory Cockpit, revisione delle prestazioni, revisione MRO e gestione dedicata dell'account.",
    "annex7.intro": (
        "Il modulo Servizi Digitali offre servizi selezionati di monitoraggio digitale, "
        "revisione delle prestazioni e gestione dell'account."
    ),
    "annex7.cockpit.title": "1. Factory Cockpit",
    "annex7.cockpit.p1": (
        "Quando l'Attrezzatura selezionata è tecnicamente compatibile, Weber supporterà "
        "la connessione dell'Attrezzatura concordata a Factory Cockpit in conformità con "
        "le condizioni del servizio digitale applicabili."
    ),
    "annex7.cockpit.lines": "Linea/e connessa/e",
    "annex7.cockpit.p2": (
        "Factory Cockpit può essere utilizzato per raccogliere e visualizzare i dati di "
        "prestazione disponibili delle macchine al fine della revisione e "
        "dell'ottimizzazione delle prestazioni."
    ),
    "annex7.cockpit.p3": (
        "Il Cliente fornirà l'infrastruttura di rete, le autorizzazioni e l'accesso "
        "tecnico ragionevolmente richiesti per la connessione."
    ),
    "annex7.cockpit.p4": (
        "La disponibilità di dati specifici dipende dalla generazione di macchina, dal "
        "software installato e dalla connettività dell'Attrezzatura interessata."
    ),
    "annex7.cockpit.p5": (
        "Qualunque licenza software separata o condizioni del servizio digitale "
        "applicabili a Factory Cockpit restano applicabili."
    ),
    "annex7.performance.title": "2. Revisione delle prestazioni",
    "annex7.performance.p1": "Weber e il Cliente effettueranno revisioni periodiche dei dati di prestazione disponibili dell'Attrezzatura.",
    "annex7.performance.frequency": "Frequenza di revisione",
    "annex7.performance.p2": "La revisione può includere:",
    "annex7.performance.includes": [
        "i KPI selezionati della macchina;",
        "le tendenze delle prestazioni;",
        "osservazioni tecniche ricorrenti;",
        "opportunità di miglioramento identificate;",
        "le attività svolte;",
        "le azioni in sospeso; e",
        "le priorità del prossimo periodo di revisione.",
    ],
    "annex7.performance.p3": "Le Parti possono concordare KPI e valori obiettivo specifici del Cliente.",
    "annex7.performance.p4": (
        "Salvo espressa convenzione contraria, tali valori obiettivo sono obiettivi di "
        "gestione e non garanzie contrattuali delle prestazioni."
    ),
    "annex7.mro.title": "3. Revisione MRO",
    "annex7.mro.p1": (
        "Weber esaminerà periodicamente le informazioni disponibili sulla spesa di "
        "Manutenzione, Riparazione e Operazioni (MRO) dell'Attrezzatura coperta."
    ),
    "annex7.mro.p2": "La revisione può includere:",
    "annex7.mro.includes": [
        "la spesa per i ricambi;",
        "la spesa per i servizi;",
        "la spesa per le lame ove rilevante;",
        "lo storico dell'attività di manutenzione;",
        "le informazioni sulla base installata;",
        "le tendenze di manutenzione;",
        "i fattori di costo identificati; e",
        "il confronto con un obiettivo di pianificazione MRO concordato.",
    ],
    "annex7.mro.frequency": "Frequenza di revisione MRO",
    "annex7.mro.target": "Obiettivo MRO concordato, ove applicabile",
    "annex7.mro.p3": (
        "Lo scopo della revisione è sostenere la pianificazione della manutenzione e "
        "identificare opportunità di miglioramento. Non costituisce una garanzia che "
        "venga raggiunto un determinato livello di spesa MRO."
    ),
    "annex7.account.title": "4. Team dedicato all'account",
    "annex7.account.p1": "Weber assegnerà una struttura di gestione dell'account Guardian per il Cliente.",
    "annex7.account.p2": (
        "Il team coordinerà le attività Guardian selezionate e fungerà da punto centrale "
        "per la revisione periodica del programma."
    ),
    "annex7.account.p3": "Il processo di gestione dell'account può includere:",
    "annex7.account.includes": [
        "revisioni periodiche del Cliente;",
        "il coordinamento tra le funzioni Weber rilevanti;",
        "la revisione delle azioni aperte;",
        "la revisione delle prossime attività di servizio;",
        "la revisione delle esigenze di ricambi e lame;",
        "discussioni sulle prestazioni;",
        "opportunità di ottimizzazione; e",
        "il monitoraggio delle azioni concordate.",
    ],
    "annex7.account.cadence": "Cadenza di revisione",
    "annex7.account.p4": (
        "Il team dedicato all'account integra, ma non sostituisce, i canali operativi "
        "normali di Weber per richieste di servizio urgenti, ordini di ricambi o "
        "assistenza di emergenza."
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
