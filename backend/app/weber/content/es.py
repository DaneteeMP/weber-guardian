"""Spanish overrides for the Guardian agreement content (full catalog).

Responsibility: translate every translatable node id to Spanish. Any node id
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
    "module.customer_service": "Atención al cliente",
    "module.spare_parts": "Recambios y disponibilidad",
    "module.academy": "Academia",
    "module.blade_solutions": "Cuchillas y soluciones",
    "module.optimization": "Optimización y rendimiento",
    "module.digital_services": "Servicios digitales",

    # Always-on rows of the annex/summary tables
    "annex1.summary.inspection": "Inspección y mantenimiento",
    "summary.scope.inspection": "Inspección y mantenimiento",

    # Guardian contract types (labels.GUARDIAN_TYPE_LABELS)
    "guardian_type.audit": "Inspección",
    "guardian_type.off_guardian": "Off-Guardian",
    "guardian_type.guardian": "Basic Kit",

    # Cover
    "cover.title": "CONTRATO DE MANTENIMIENTO",
    "cover.executor.label": "Entre la empresa:",
    "cover.executor.alias": "(en adelante, el Ejecutor)",
    "cover.customer.label": "Y la empresa:",
    "cover.customer.alias": "(en adelante, el Ordenante)",
    "cover.preamble": (
        "se celebra el siguiente contrato de inspección y mantenimiento "
        '(en adelante, el "Contrato"):'
    ),

    # Commercial breakdown (legacy Annex 1)
    "breakdown.title": "ANEXO 1, Relación de máquinas y módulos",
    "breakdown.date": "Fecha",
    "breakdown.offer_no": "N.º oferta",
    "breakdown.frequency": "Frecuencia de Inspección",
    "breakdown.type": "Tipo",
    "breakdown.col.line": "Nº DE LÍNEA",
    "breakdown.col.module": "MÓDULO",
    "breakdown.col.amount": "IMPORTE",
    "breakdown.total": "Total",
    "breakdown.kit": "Kit básico de recambios",
    "breakdown.discount": "Descuento con contrato de mantenimiento",
    "breakdown.grand_total": "Importe total (sin IVA)",
    "breakdown.intro": (
        "Ambas partes acuerdan el siguiente presupuesto de inspección de Weber "
        "según condiciones adjuntas:"
    ),
    "breakdown.notes": [
        "incluye desplazamientos, mano de obra y documentación.",
        "comprobación de sensores, componentes eléctricos, transmisiones, correas "
        "dentadas y cuchillas (en el kit básico se incluye la sustitución de las "
        "correas principales del cabezal, husillo y módulos auxiliares).",
        "ajuste de las piezas mecánicas de los diferentes módulos.",
        "revisión y optimización de programas.",
        "registro de todas las reparaciones previstas.",
    ],
    "breakdown.notes_title": "NOTAS:",
    "breakdown.discount_notes": [
        "Descuento del 15% en la asistencia técnica de las líneas contratadas.",
        "Descuento del 5% en los recambios de las líneas contratadas (no aplicable a "
        "descuentos vigentes).",
        "Descuento del 5% en cuchillas para cajas completas de 3 cuchillas (no aplicable "
        "a descuentos vigentes).",
        "Incluye una visita gratuita de seguimiento a los 6 meses.",
        "Todas las piezas, consumibles y recambios fuera de presupuesto, así como horas "
        "fuera de horario normal, espera y reparación fuera de presupuesto, se facturarán "
        "aparte.",
    ],

    # Master Agreement (legacy maintenance contract: 0 + I-IX)
    "master.clause0.title": "0. DEFINICIONES",
    "master.clause0.intro": "Los términos utilizados en este acuerdo tienen los siguientes significados:",
    "master.clause0.machine.term": "Máquina / Módulos",
    "master.clause0.machine.definition": (
        "Unidad funcional, equipo o sistema al que se refieren los servicios que se prestarán en "
        "virtud del presente contrato."
    ),
    "master.clause0.inspection.term": "Inspección",
    "master.clause0.inspection.definition": (
        "La determinación y evaluación del estado real de una máquina / módulo, incluida la "
        "determinación de las causas del desgaste y la derivación de las consecuencias necesarias "
        "para el uso futuro."
    ),
    "master.clause0.maintenance.term": "Mantenimiento",
    "master.clause0.maintenance.definition": (
        "Las medidas para retrasar el desmantelamiento de las existencias de desgaste existentes "
        '("mantenimiento preventivo"), en particular mediante ajustes o mediante la sustitución de '
        "filtros, sellos y lubricantes, limpieza técnica, etc."
    ),
    "master.clause0.replacement.term": "Reposición",
    "master.clause0.replacement.definition": (
        "Cualquier medida para devolver una máquina / módulo a la condición acordada, en particular "
        "mediante la sustitución de piezas, incluidas las piezas de desgaste. Las medidas para "
        "mantener la condición acordada fuera de los servicios de mantenimiento también son parte "
        "de la reparación."
    ),

    # I. Objeto del contrato
    "master.clause1.title": "I. OBJETO DEL CONTRATO",
    "master.clause1.p1": (
        "(0) El Contrato de inspección tiene por objeto la inspección de las máquinas y módulos "
        "enumerados en el Anexo 1, facturación de estos servicios sobre la base de una tarifa fija "
        "(Anexo 1). El mantenimiento de las máquinas y componentes, a computar según se incurra en "
        "el mismo y según tarifas vigentes."
    ),
    "master.clause1.p2": (
        "El objetivo del Contrato es extender la vida útil de las máquinas y los módulos, reducir "
        "los tiempos de inactividad y mantener los costos de mantenimiento bajo control mediante "
        "una inspección y un mantenimiento adecuados."
    ),
    "master.clause1.p3": (
        "(1) En el marco de este Contrato, el Ejecutor asume los siguientes servicios para las "
        "máquinas y módulos enumerados:"
    ),
    "master.clause1.services": [
        "Servicio de atención telefónica",
        "Suministro de piezas de repuesto",
        "Mantenimiento",
        "Visita de cortesía posterior al mantenimiento",
        "Programa de Cuchillas (resguardo de stock)",
    ],
    "master.clause1.p4": "(2) El servicio del Ejecutor comprende, en los siguientes casos:",
    "master.clause1.p5": "(2.1) En los que se acceda a la línea o centro de atención telefónica:",
    "master.clause1.hotline": [
        "El servicio de atención telefónica de lunes a viernes de 07:30 h a 17:30 h.",
        "Teléfono: 938 23 32 33",
    ],
    "master.clause1.p6": (
        "(2.2) La distribución de piezas de repuesto: El suministro de piezas de repuesto "
        "existentes (en stock) en almacén (en la Península Ibérica y Alemania) en un plazo de "
        "24-48 horas. En el caso de no disponer de la pieza de repuesto solicitada en stock, se "
        "solicitará y se entregará con la mayor brevedad posible."
    ),
    "master.clause1.p7": "(2.3) La inspección: Inspección de las máquinas en conformidad con el ANEXO 1.",
    "master.clause1.p8": "(2.4) El mantenimiento: Ejecución de reparaciones de conformidad con el punto I.3 del Contrato.",
    "master.clause1.p9": (
        "(2.5) Programa de resguardo de stock de Cuchillas: descuento del 5% a partir de la 1ª caja "
        "de 3 unidades, en conformidad con el ANEXO 2."
    ),
    "master.clause1.p10": (
        "(3) Cualquier trabajo de mantenimiento u otros servicios (por ejemplo, cambios en las "
        "máquinas y sistemas) que resulten de la inspección requerirán de una orden de compra "
        "separada; y se facturará en función de una oferta adicional."
    ),
    "master.clause1.p11": (
        "(4) El número de las máquinas incluidas en el ANEXO 1, así como el alcance de los "
        "servicios derivados del presente Contrato se verificarán, por parte de las partes "
        "contratantes, en el último trimestre del Contrato"
    ),
    "master.clause1.p12": (
        "(5) Las modificaciones en referencia al número de máquinas incluidas en el acuerdo y las "
        "modificaciones del alcance del servicio por parte del Ordenante se harán constar por "
        "escrito, modificando el Anexo 1. Este acuerdo de servicios es válido por los 12 meses de "
        "validez de Contrato o hasta la finalización del Contrato"
    ),
    "master.clause1.p13": "(6) Visita de cortesía a realizar si el mantenimiento posterior es realizado por el Ejecutor.",

    # II. Precio y pago
    "master.clause2.title": "II. PRECIO Y PAGO",
    "master.clause2.p1": (
        "(1) El precio del trabajo de inspección se calcula según el ANEXO 1. La relación se deduce "
        "del modelo de máquina y de los módulos seleccionados conforme al punto I del Contrato."
    ),
    "master.clause2.p2": (
        '(2) El precio para los módulos "Inspección" y "Mantenimiento" incluye gastos de '
        "desplazamiento, transporte, alojamiento y dietas. Salvo excepciones acordadas con el "
        "Ordenante."
    ),
    "master.clause2.p3": "(3) Las piezas sustituidas se le presentarán al Ordenante para su control.",
    "master.clause2.p4": (
        "(4) El precio del trabajo del personal de inspección se abonará una vez emitida la "
        "factura, en el plazo de 30 días. La facturación tiene lugar después de haber realizado "
        "la inspección."
    ),
    "master.clause2.p5": (
        "(5) El Ejecutor tiene derecho a revisar el precio del trabajo conforme a lo establecido en "
        "el Anexo 1 anualmente. Le notificará dicha revisión al Ordenante al menos 3 meses antes de "
        "la entrada en vigor. La modificación del precio se aplicará en el siguiente periodo de pago."
    ),
    "master.clause2.p6": (
        "(6) No se acepta la retención de pagos ni la compensación por eventuales contraprestaciones "
        "alegadas por parte del Ordenante."
    ),
    "master.clause2.p7": (
        "(7) El Ejecutor ofrece un descuento del 15 % para los servicios de asistencia de máquinas y "
        "un 5% de descuento máximo en recambios no acumulable como indica el ANEXO 1."
    ),

    # III. Participación y contribución técnica del Ordenante
    "master.clause3.title": "III. PARTICIPACIÓN Y CONTRIBUCIÓN TÉCNICA DEL ORDENANTE",
    "master.clause3.p1": "(1) El Ordenante velará por qué:",
    "master.clause3.obligations": [
        "Los trabajos puedan llevarse a cabo puntualmente a las horas y en las máquinas acordadas "
        "y garantizará el libre acceso a las máquinas y módulos.",
        "La máquina se encuentre en estado operativo, esté disponible y limpia (sin restos de producto).",
        "Una vez finalizados los trabajos, pueda llevarse a cabo una comprobación funcional con los "
        "productos originales del cliente en una cantidad suficiente.",
        "Se registren las averías en curso en los planos de máquinas.",
        "El transcurso de la producción se oriente de tal modo que, durante la inspección, sea "
        "posible detener el mismo.",
    ],
    "master.clause3.p2": (
        "(2.a) El Ordenante correrá con los gastos originados por el personal de inspección durante "
        "la ejecución de la inspección y del mantenimiento."
    ),
    "master.clause3.p3": (
        "El Ordenante tomará las medidas especiales necesarias para la protección personal y "
        "material en el lugar de inspección/mantenimiento. Asimismo, el Ordenante informará al "
        "personal de la empresa ejecutora acerca de las medidas especiales de seguridad, siempre "
        "que estas resulten relevantes para el personal de inspección y mantenimiento. El Ordenante "
        "notificará al ejecutor las infracciones cometidas por parte del personal que vulneren "
        "dichas prescripciones de seguridad."
    ),
    "master.clause3.p4": (
        "(b) El Ordenante se compromete a correr con los gastos de la contribución técnica, en "
        "particular, a ofrecer gratuitamente asistencia, taller, medios auxiliares como el agua y "
        "la electricidad, incluyendo las conexiones necesarias."
    ),
    "master.clause3.p5": (
        "(c) Para decidir si los trabajos pueden efectuarse y/o las piezas que indica el punto I.3. "
        "pueden reemplazarse durante el intervalo de inspección, el Ordenante designa a una persona "
        "con capacidad para la toma de decisiones."
    ),

    # IV. Cumplimiento de los plazos del contrato
    "master.clause4.title": "IV. CUMPLIMIENTO DE LOS PLAZOS DEL CONTRATO",
    "master.clause4.p1": "(1) El Ejecutor se compromete a efectuar una inspección en el marco del intervalo de tiempo acordado en el Anexo 1.",
    "master.clause4.p2": (
        "(2) El Ejecutor notifica al Ordenante la fecha exacta de la inspección con al menos con 6 "
        "semanas de antelación, en caso de que entre las partes del contrato no se haya acordado "
        "una determinada fecha."
    ),
    "master.clause4.p3": "(3) El Ejecutor prestará los servicios en los siguientes periodos:",
    "master.clause4.service_periods": [
        "Inspección y mantenimiento de lunes a viernes de 08:00 h a 18:00 h.",
        "Salvo excepciones de mutuo acuerdo.",
    ],
    "master.clause4.p4": (
        "(4) En caso de que al Ordenante o al Ejecutor no le fuese posible llevar a cabo los "
        "trabajos en la fecha prevista, ambas partes se lo notificarán recíprocamente con al menos "
        "2 días laborables de antelación. Si el día acordado el Ejecutor no se presenta, el "
        "Ejecutor no le facturará los gastos de desplazamiento en la siguiente fecha; en caso de "
        "que la línea no esté disponible el día acordado por parte del Ordenante, este pagará al "
        "Ejecutor los gastos incurridos del desplazamiento."
    ),
    "master.clause4.p5": (
        "(5) Si la inspección/mantenimiento se retrasa por circunstancias originadas por conflictos "
        "laborales, en particular, huelgas y paros, así como por hechos acaecidos no imputables al "
        "Ejecutor, tendrá lugar una adecuada prolongación de la inspección/mantenimiento, siempre "
        "que pueda probarse que dichos impedimentos tienen una notoria repercusión para terminar la "
        "inspección/mantenimiento. Esto también se aplicará cuando dichas circunstancias se "
        "produzcan una vez el Ejecutor haya incumplido el plazo de preaviso establecido en el "
        "párrafo anterior."
    ),

    # V. Inicio y duración del contrato
    "master.clause5.title": "V. INICIO Y DURACIÓN DEL CONTRATO",
    "master.clause5.p1": (
        "(1) El Contrato adquiere validez desde la firma de ambas partes. La duración del Contrato "
        "es de 12 meses, y será revocable por ambas partes."
    ),
    "master.clause5.p2": (
        "(2) El Contrato se prorrogará automáticamente por otros 12 meses, en el caso de que no se "
        "haya rescindido por escrito 3 meses anteriores a la finalización del mismo."
    ),

    # VI. Garantía y responsabilidad
    "master.clause6.title": "VI. GARANTÍA Y RESPONSABILIDAD",
    "master.clause6.p1": (
        "(1) En caso de que la inspección / el mantenimiento no se haya completado en su totalidad, "
        "Ejecutor la revisará o rectificará sin coste alguno."
    ),
    "master.clause6.p2": (
        "(2) El Ejecutor subsanará gratuitamente todos los daños que él o sus agentes hayan "
        "provocado en las máquinas e instalaciones a las que debía efectuarse el mantenimiento. La "
        "cuantía de la obligación de reparación se limita a la cuota anual estipulada por contrato."
    ),
    "master.clause6.p3": (
        "(3) En el caso de que el Ejecutor incumpla su deber de reparación, mejora o reparación del "
        "daño, el Ordenante podrá establecer una prórroga adecuada. Si por la culpa del Ejecutor, "
        "este plazo transcurre sin obtenerse resultado, el Ordenante podrá, a su elección, exigir "
        "una reducción de las cuotas de mantenimiento e inspección o bien rescindir de inmediato el "
        "Contrato. Tanto el ejecutor como el Ordenante acuerdan expresamente que el ejecutor será "
        "responsable de los daños únicamente cuando pueda demostrarse dolo o negligencia grave por "
        "su parte o por parte de sus agentes. En particular, las partes acuerdan expresamente la "
        "exclusión de la responsabilidad derivada de daños o pérdidas indirectas."
    ),
    "master.clause6.p4": (
        "(4) Cualquier otro derecho a reclamación del Ordenante se aplicará únicamente en caso de "
        "dolo o negligencia grave. Además de esto, el Ordenante no podrá hacer valer ningún otro "
        "derecho de compensación ante el Ejecutor, en particular, ningún derecho a compensación por "
        "daños ni otros derechos por eventuales inconvenientes relacionados con el Contrato de "
        "inspección, independientemente de las razones que se aduzcan."
    ),
    "master.clause6.p5": "(5) Cualquier daño o desperfecto causado por piezas no originales, el Ejecutor no se hará responsable.",

    # VII. Período de prescripción
    "master.clause7.title": "VII. PERÍODO DE PRESCRIPCIÓN",
    "master.clause7.p1": (
        "Los derechos de garantía del Ordenante pierden su validez a los doce meses, a contar desde "
        "la aceptación del correspondiente servicio de inspección/mantenimiento. El plazo de "
        "garantía se prolongará mientras duren los trabajos de subsanación."
    ),

    # VIII. Otras disposiciones
    "master.clause8.title": "VIII. OTRAS DISPOSICIONES",
    "master.clause8.p1": (
        "(1) Al personal de inspección/mantenimiento se le facilitará el acceso a las máquinas e "
        "instalaciones durante las horas habituales de trabajo/tiempo de servicio con la finalidad "
        "de que pueda efectuar los trabajos de inspección y mantenimiento anunciados. El Ordenante "
        "aportará toda la información necesaria acerca de las máquinas y módulos indicados en el "
        "(Anexo 1) y proveerá la documentación correspondiente."
    ),
    "master.clause8.p2": (
        "(2) Si el Ordenante cede máquinas e instalaciones a terceros, sigue permaneciendo obligado "
        "al pago de las cuotas, a menos que el tercero se adhiera al contrato, previa autorización "
        "del ejecutor. El ejecutor únicamente podrá denegar el consentimiento por causa justificada."
    ),
    "master.clause8.p3": "(3) El Ejecutor tiene derecho a transferir a terceros los derechos y deberes contraídos con el presente contrato.",
    "master.clause8.p4": "(4) Los acuerdos adicionales y las modificaciones del contrato deben efectuarse por escrito.",
    "master.clause8.p5": (
        "(5) En el caso de que una de las disposiciones del presente contrato deje de ser válida, "
        "todas las demás disposiciones o acuerdos seguirán manteniendo su validez."
    ),

    # IX. Lugar de jurisdicción
    "master.clause9.title": "IX. LUGAR DE JURISDICCIÓN",
    "master.clause9.p1": (
        "En la medida en que lo permita la ley, el lugar de cumplimiento y jurisdicción será el "
        "domicilio social del Ejecutor. Se aplicará exclusivamente la legislación de España."
    ),

    # Annex 1 - Equipment & Commercial Schedule
    "annex1.title": "ANEXO 1 - EQUIPOS Y CONDICIONES COMERCIALES",
    "annex1.info.title": "1. Información del contrato",
    "annex1.info.customer": "Cliente",
    "annex1.info.customer_no": "N.º de cliente",
    "annex1.info.site": "Centro",
    "annex1.info.agreement_no": "N.º de acuerdo",
    "annex1.info.start_date": "Fecha de inicio del contrato",
    "annex1.info.term": "Duración inicial",
    "annex1.info.billing": "Frecuencia de facturación",
    "annex1.info.currency": "Moneda",
    "annex1.equipment.title": "2. Equipamiento cubierto",
    "annex1.equipment.intro": "Solo el equipamiento y los módulos de máquina listados a continuación están cubiertos por los Servicios Guardian.",
    "annex1.equipment.h_line": "Línea de producción",
    "annex1.equipment.h_machine": "Máquina",
    "annex1.equipment.h_serial": "N.º de serie",
    "annex1.equipment.h_type": "Tipo",
    "annex1.equipment.h_modules": "Módulos / componentes incluidos",
    "annex1.equipment.h_frequency": "Frecuencia de servicio",
    "annex1.modules.title": "3. Módulos Guardian seleccionados",
    "annex1.modules.intro": "Los siguientes módulos Guardian forman parte del presente Acuerdo:",
    "annex1.modules.outro": (
        "Solo los Anexos correspondientes a los módulos seleccionados anteriormente se adjuntan y "
        "forman parte del Acuerdo."
    ),
    "annex1.summary.title": "4. Resumen comercial",
    "annex1.summary.h_item": "Concepto comercial",
    "annex1.summary.h_amount": "Importe",
    "annex1.summary.travel": "Desplazamiento / gastos",
    "annex1.summary.kit": "Repuestos / kit de mantenimiento",
    "annex1.summary.discount": "Descuento Guardian",
    "annex1.summary.total": "VALOR TOTAL DEL CONTRATO",
    "annex1.summary.vat_note": "Todos los importes no incluyen el IVA aplicable, salvo que se indique lo contrario.",
    "annex1.billing.title": "5. Facturación",
    "annex1.billing.frequency": "Frecuencia de facturación",
    "annex1.billing.terms": "Condiciones de pago",
    "annex1.billing.adjustment": "Ajuste de precios",
    "annex1.billing.travel": "Condiciones de desplazamiento",
    "annex1.billing.freight": "Condiciones de porte",
    "annex1.special.title": "6. Condiciones comerciales especiales",

    # Annex 2 - Maintenance & Inspection
    "annex2.title": "ANEXO 2 - MANTENIMIENTO E INSPECCIÓN",
    "annex2.tagline": "Servicios de inspección, mantenimiento preventivo y estado de la máquina.",
    "annex2.purpose.title": "1. Objeto",
    "annex2.purpose.p1": (
        "El módulo de Mantenimiento e Inspección tiene por objeto evaluar y mantener el estado del "
        "Equipamiento identificado en el Anexo 1, identificar las acciones técnicas requeridas y "
        "favorecer la operación fiable y la planificación del mantenimiento."
    ),
    "annex2.purpose.p2": "Las actividades exactas incluidas dependen de las opciones seleccionadas en la configuración Guardian.",
    "annex2.inspection.title": "S301 Inspección Técnica Programada",
    "annex2.inspection.p1": (
        "Una inspección evalúa el estado del equipamiento seleccionado en el intervalo acordado "
        "mediante la lista de verificación aplicable basada en la línea o el módulo. El alcance "
        "técnico se adaptará al tipo y la configuración del equipamiento."
    ),
    "annex2.inspection.p2": (
        "Antes de la inspección, Weber y el Cliente revisarán las incidencias de funcionamiento "
        "conocidas, el historial del equipamiento y la disponibilidad de producción prevista. Tras "
        "la inspección, los hallazgos se comentarán con el representante designado del Cliente y se "
        "registrarán en un informe de inspección."
    ),
    "annex2.checklist.title": "Lista de Verificación de la Máquina",
    "annex2.checklist.p1": (
        "Para las líneas de corte, la lista de verificación estándar podrá incluir lo siguiente, "
        "cuando sea técnicamente aplicable y accesible de forma segura:"
    ),
    "annex2.checklist.items": [
        "prueba de funcionamiento con el producto original cuando esté disponible; observaciones "
        "sobre el estado del equipamiento y la seguridad;",
        "sensores, electrónica, ajustes de la máquina, funciones eléctricas y neumáticas; "
        "transmisiones, correas de distribución y trenes de accionamiento seleccionados;",
        "ajustes mecánicos, carcasas y juntas, transportadores y elementos móviles; módulos de "
        "línea y componentes auxiliares de Weber;",
        "identificación de desgaste, reparaciones pendientes, anomalías de la máquina y "
        "recomendaciones para acciones adicionales;",
        "acceso a las carcasas de báscula o de cabeza de corte únicamente cuando se acuerde "
        "expresamente y se autorice de forma segura;",
        "preparación de una lista de verificación de inspección basada en módulos, informe y "
        "presupuesto opcional de repuestos de seguimiento.",
    ],
    "annex2.checklist.p2": (
        "Para las máquinas de envasado de Weber, la lista de verificación de inspección también "
        "podrá incluir comprobaciones de estado específicas de envasado definidas. Las "
        "etiquetadoras, bombas y dispositivos de fin de línea de terceros quedan excluidos salvo "
        "que se relacionen expresamente."
    ),
    "annex2.report.title": "S305 Visita de Seguimiento e Informes",
    "annex2.report.p1": (
        "Cuando se acuerde, Weber realizará un seguimiento definido tras una inspección o un evento "
        "de mantenimiento, que podrá ser presencial o remoto según el servicio acordado."
    ),
    "annex2.report.p2": (
        "Una visita de seguimiento no se incluye automáticamente con una inspección y podrá estar "
        "condicionada a que Weber realice los trabajos de mantenimiento especificados, según lo "
        "indicado en el calendario del Cliente."
    ),
    "annex2.preventive.title": "S303 Mantenimiento Preventivo",
    "annex2.preventive.p1": (
        "El mantenimiento preventivo consiste en ajustes planificados, lubricación, limpieza de "
        "componentes técnicos definidos y sustitución de piezas de desgaste especificadas de "
        "acuerdo con la lista de actividades acordada y las limitaciones del equipamiento."
    ),
    "annex2.preventive.p2": (
        "El alcance de las piezas suministradas, las piezas instaladas, la mano de obra prevista, la "
        "frecuencia y el tiempo de inactividad requerido se especificarán por máquina en el Anexo 1."
    ),
    "annex2.preventive.p3": (
        "El mantenimiento preventivo es distinto de una reparación correctiva; los servicios fuera "
        "de la lista de tareas planificadas se autorizan y facturan por separado salvo que se "
        "incluyan expresamente."
    ),
    "annex2.kit.title": "S402 Kit Básico de Repuestos - Solo Suministro",
    "annex2.kit.p1": (
        "El Kit Básico de Repuestos está compuesto por los artículos y cantidades exactos que "
        "figuran en el Programa de Kits firmado. Sirve de apoyo a la sustitución planificada o al "
        "stock en poder del Cliente, pero no constituye un derecho ilimitado a consumibles."
    ),
    "annex2.kit.p2": (
        "Weber suministra los artículos relacionados conforme a las condiciones de pedido, entrega "
        "y precio especificadas. La instalación no está incluida en un kit de solo suministro."
    ),
    "annex2.repairs.title": "S304 Mantenimiento Correctivo / Reparación",
    "annex2.repairs.p1": (
        "El trabajo de reparación se realiza tras un fallo, avería o defecto identificado y tiene "
        "por objeto restablecer un estado acordado, sujeto a acceso, viabilidad técnica y "
        "disponibilidad de repuestos."
    ),
    "annex2.repairs.p2": (
        "Salvo que una asignación de reparación esté expresamente valorada y seleccionada, la mano "
        "de obra correctiva, las piezas de repuesto, los desplazamientos y otros costes se "
        "presupuestarán o facturarán según las tarifas de servicio seleccionadas y la autorización "
        "del Cliente."
    ),
    "annex2.repairs.p3": (
        "Una asistencia, un diagnóstico de averías o una tarea de reparación no se considerará una "
        "restauración garantizada de la producción en un plazo determinado salvo que se acuerde "
        "expresamente por escrito."
    ),
    "annex2.frequency.title": "Frecuencia de Inspección",
    "annex2.frequency.value": "Frecuencia",
    "annex2.frequency.p1": "El calendario real se coordinará entre Weber y el Cliente.",

    # Annex 3 - Service Support
    "annex3.title": "ANEXO 3 - SOPORTE DE SERVICIO",
    "annex3.tagline": "Atención al cliente y soporte técnico.",
    "annex3.purpose.title": "1. Objeto",
    "annex3.purpose.p1": (
        "El módulo de Soporte de Servicio proporciona al Cliente acceso al soporte técnico de "
        "Weber para el Equipamiento cubierto por el presente Acuerdo."
    ),
    "annex3.purpose.p2": "El nivel de servicio exacto depende de las opciones seleccionadas a continuación.",
    "annex3.rates.title": "2. Tarifas de Servicio",
    "annex3.rates.hours": "Horario",
    "annex3.rates.weekdays": "Lunes - Viernes",
    "annex3.rates.saturday": "Sábado",
    "annex3.rates.sunday": "Domingo / festivo",
    "annex3.rates.band": "Banda",
    "annex3.rates.without": "Sin contrato",
    "annex3.rates.with": "Con contrato",
    "annex3.hotline.title": "S101 Línea Directa Estándar",
    "annex3.hotline.p1": (
        "Weber proporcionará acceso al canal de contacto técnico estándar seleccionado durante la "
        "ventana de disponibilidad acordada. Se trata de un servicio de comunicación; no implica "
        "tiempo de respuesta en sitio."
    ),
    "annex3.hotline.phone": "Punto de contacto",
    "annex3.hotline.email": "Correo electrónico",
    "annex3.hotline.hours": "Lunes - Viernes",
    "annex3.hotline.p2": (
        "La disponibilidad para la aceptación de llamadas no constituye, por sí misma, una "
        "resolución de diagnóstico garantizada, una asistencia en sitio ni el envío de repuestos."
    ),
    "annex3.remote.title": "S103 Soporte Técnico Remoto",
    "annex3.remote.p1": (
        "Weber podrá proporcionar un análisis inicial de fallos por teléfono, correo electrónico, "
        "conexión remota admitida o comunicación por vídeo, sujeto al acuerdo sobre el acceso "
        "seguro y la asistencia del Cliente."
    ),
    "annex3.remote.p2": (
        "Las condiciones de conexión, red y ciberseguridad deberán acordarse antes de la "
        "activación. El soporte remoto no sustituye a un servicio en sitio necesario."
    ),
    "annex3.priority.title": "S104 Servicio en Sitio y Respuesta Prioritaria",
    "annex3.priority.p1": (
        "La asistencia técnica en sitio está disponible en el territorio acordado, sujeto a la "
        "disponibilidad de técnicos y a las condiciones aplicables de envío y reserva. Cualquier "
        "clasificación de prioridad deberá acordarse expresamente."
    ),
    "annex3.priority.p2": (
        "Los cargos por desplazamiento, mano de obra, viajes, tiempo de espera, horas "
        "extraordinarias, alojamiento y materiales se calcularán conforme al tarifario aprobado."
    ),

    # Annex 4 - Parts & Availability
    "annex4.title": "ANEXO 4 - REPUESTOS Y DISPONIBILIDAD",
    "annex4.tagline": "Condiciones comerciales de repuestos, trato prioritario y stock recomendado.",
    "annex4.purpose.title": "1. Objeto",
    "annex4.purpose.p1": (
        "El módulo de Repuestos y Disponibilidad respalda la planificación estructurada de "
        "repuestos y el acceso a los repuestos originales de Weber para el Equipamiento cubierto "
        "por el presente Acuerdo."
    ),
    "annex4.discount.title": "S201 Condiciones Comerciales de Repuestos",
    "annex4.discount.p1": (
        "Las categorías de repuestos seleccionadas se suministran a los precios y descuentos "
        "acordados, con las exclusiones y el tratamiento de piezas de recambio, cuchillas, pedidos "
        "especiales y equipamiento actualizado expresamente indicados."
    ),
    "annex4.discount.p2": "Los descuentos no son acumulables salvo acuerdo expreso.",
    "annex4.handling.title": "S203 Trato Prioritario de Repuestos",
    "annex4.handling.p1": (
        "Sujeto a la disponibilidad y a las condiciones acordadas para la realización de pedidos, "
        "los pedidos elegibles podrán recibir procesamiento prioritario o envío prioritario "
        "conforme al acuerdo local."
    ),
    "annex4.parts_list.title": "S202 Lista de Repuestos Recomendados",
    "annex4.parts_list.p1": (
        "Weber podrá preparar una lista de repuestos recomendados específica para cada máquina, "
        "distinguiendo las piezas de desgaste planificadas de los repuestos de alto riesgo "
        "recomendados para el stock del Cliente. Las listas se revisarán conforme a la antigüedad, "
        "especificación y mantenibilidad del equipamiento."
    ),
    "annex4.parts_list.p2": (
        "Cuando la filial local aplique la clasificación de estilo Benelux, A/B designan las "
        "piezas de desgaste/críticas recomendadas y C/D/E pueden identificar stock local, otro "
        "stock de Weber o fabricación bajo pedido; una misma pieza puede tener a la vez una "
        "recomendación y un estado de disponibilidad."
    ),
    "annex4.parts_list.categories": [
        "A - Piezas de desgaste recomendadas.",
        "B - Repuestos críticos / de mayor riesgo de avería propuestos para stock en sitio.",
        "C - Disponibles en el stock local de Weber (sujeto a confirmación).",
        "D - Disponibles en otra ubicación de Weber (sujeto a confirmación).",
        "E - Fabricados bajo pedido / sin stock actual.",
    ],
    "annex4.parts_list.p3": (
        "La lista es orientativa, no constituye una garantía de disponibilidad de stock, de "
        "idoneidad para todas las configuraciones ni un compromiso de suministrar automáticamente "
        "las cantidades recomendadas."
    ),
    "annex4.parts_list.p4": (
        "Weber suministra una lista de repuestos orientativa específica para cada máquina, sin "
        "suministro de materiales ni instalación salvo pedido separado."
    ),

    # Annex 5 - Blade Solutions
    "annex5.title": "ANEXO 5 - SOLUCIONES DE CUCHILLAS",
    "annex5.tagline": "Consultoría de aplicación de cuchillas, afilado y programa de cuchillas.",
    "annex5.intro": (
        "El módulo de Soluciones de Cuchillas favorece la selección, la disponibilidad, el uso y "
        "la gestión correctos de las cuchillas de Weber, incluido el principio «cuchilla correcta, "
        "aplicación correcta»."
    ),
    "annex5.discount.title": "S603 Programa de Suministro de Cuchillas",
    "annex5.discount.p1": (
        "Si el Cliente selecciona la opción de Programa de Cuchillas, las partes acuerdan un "
        "catálogo definido de referencias de cuchillas, cantidades, precios, calendario de pedidos "
        "y plazo comercial en el Programa de Cuchillas."
    ),
    "annex5.discount.p2": (
        "Cualquier presupuesto mensual fijo o plan de cuotas, previsión de consumo, compromiso "
        "mínimo, plazo de fijación de precios, bonificación, pedido de liberación, programa de "
        "devoluciones o acuerdo especial de entrega se aplicará únicamente si se especifica en "
        "dicho programa."
    ),
    "annex5.stock.title": "Acuerdo de Stock de Cuchillas",
    "annex5.stock.p1": (
        "Cuando se selecciona un Acuerdo de Stock de Cuchillas, las partes definen las referencias, "
        "cantidades, método de reposición, ubicación del stock y titularidad en el programa firmado."
    ),
    "annex5.stock.p2": (
        "Las cantidades compradas o entregadas deben contabilizarse de forma distinta del consumo "
        "estimado o del stock interno de cuchillas."
    ),
    "annex5.sharpening.title": "S602 Evaluación del Afilado",
    "annex5.sharpening.p1": (
        "Weber evalúa el enfoque de afilado actual del Cliente, sus procesos, parámetros de máquina "
        "y posibles mejoras de control de calidad o manipulación dentro del alcance acordado."
    ),
    "annex5.application.title": "S601 Consultoría de Aplicación de Cuchillas",
    "annex5.application.p1": (
        "Weber revisa con el Cliente la aplicación de corte seleccionada, las características del "
        "producto, la configuración de corte y la geometría o especificación de cuchilla pertinente."
    ),
    "annex5.application.p2": (
        "Entregable: un conjunto documentado de recomendaciones técnicas para una combinación "
        "adecuada de cuchilla y aplicación, sujeto a verificación en la aplicación real."
    ),

    # Annex 6 - Training & Optimization
    "annex6.title": "ANEXO 6 - FORMACIÓN Y OPTIMIZACIÓN",
    "annex6.tagline": (
        "Formación de operadores y de técnicos de mantenimiento, optimización de línea y "
        "auditorías EPIP."
    ),
    "annex6.intro": (
        "El módulo de Formación y Optimización ofrece actividades seleccionadas destinadas a "
        "mejorar la operación de las máquinas, la capacidad de mantenimiento y el rendimiento de "
        "la producción."
    ),
    "annex6.operator.title": "S501 Formación de Operadores",
    "annex6.operator.p1": (
        "Formación para operadores sobre el uso seguro y eficiente del Equipamiento definido, "
        "incluidos procedimientos de operación, ajustes, prácticas de limpieza y comprobaciones "
        "básicas de operación seleccionados, en la medida en que resulte apropiado."
    ),
    "annex6.maintenance.title": "S502 Formación de Técnicos de Mantenimiento",
    "annex6.maintenance.p1": (
        "Formación para el equipo de mantenimiento del Cliente sobre la arquitectura de la "
        "máquina, las comprobaciones preventivas, la identificación de averías, la resolución "
        "segura de problemas y los procedimientos de mantenimiento, dentro de los permisos de "
        "acceso acordados."
    ),
    "annex6.optimization.title": "S702 Optimización de Línea",
    "annex6.optimization.p1": (
        "Weber revisa las restricciones técnicas y de producción identificadas y podrá recomendar "
        "o realizar mejoras acordadas en la configuración de la máquina o en el proceso, dentro "
        "del alcance aceptado."
    ),
    "annex6.optimization.p2": (
        "Cualquier mejora de capital o partida de reparación permanece separada."
    ),
    "annex6.epip.title": "S701 Auditoría EPIP / Equipos",
    "annex6.epip.p1": (
        "Weber realiza la evaluación exhaustiva del equipamiento seleccionado / auditoría de tipo "
        "EPIP sobre las líneas de producción especificadas y proporciona un informe de evaluación."
    ),
    "annex6.epip.p2": (
        "El informe distinguirá la condición observada, las acciones prioritarias, las "
        "reparaciones recomendadas y las oportunidades de mejora."
    ),

    # Annex 7 - Digital Services
    "annex7.title": "ANEXO 7 - SERVICIOS DIGITALES",
    "annex7.tagline": (
        "Factory Cockpit, revisiones de rendimiento, revisiones MRO y gestión de cuenta dedicada."
    ),
    "annex7.intro": (
        "El módulo de Servicios Digitales ofrece servicios seleccionados de monitorización digital, "
        "revisión de rendimiento y gestión de cuenta."
    ),
    "annex7.cockpit.title": "S801 Factory Cockpit / Monitorización",
    "annex7.cockpit.p1": (
        "Cuando esté disponible y haya sido seleccionado, Weber proporcionará la conexión o el "
        "acceso acordados a la funcionalidad Factory Cockpit designada o a la funcionalidad de "
        "monitorización digital soportada para el Equipamiento elegible."
    ),
    "annex7.cockpit.p2": (
        "La arquitectura de conexión, la disponibilidad del servicio, la retención, los derechos de "
        "acceso y las responsabilidades en materia de ciberseguridad se definirán en las condiciones "
        "del servicio digital."
    ),
    "annex7.performance.title": "S802 Revisión de Rendimiento e Informes de Tendencias",
    "annex7.performance.p1": (
        "Weber podrá preparar o revisar la información acordada sobre el rendimiento del "
        "Equipamiento, las tendencias de operación y las áreas de seguimiento identificadas, sobre "
        "la base de los datos puestos a disposición."
    ),
    "annex7.performance.p2": (
        "Los valores podrán verse afectados por la calidad de los datos, las prácticas de "
        "operación, la combinación de productos y sistemas de terceros. Los informes son "
        "analíticos y no constituyen garantías de rendimiento de producción."
    ),
    "annex7.mro.title": "S803 Revisión MRO de Servicio / Repuestos",
    "annex7.mro.p1": (
        "Weber podrá revisar el gasto acordado en servicio y el uso de repuestos frente a una "
        "referencia MRO definida o a un objetivo de planificación acordado."
    ),
    "annex7.mro.p2": (
        "Las cuotas fijas de Guardian, las intervenciones de mantenimiento efectivas y los "
        "repuestos consumidos permanecerán como elementos de datos separados; sin duplicación de "
        "costes y sin inferir averías a partir de los importes de factura."
    ),
    "annex7.account.title": "S105 Revisiones de Cuenta Dedicada",
    "annex7.account.p1": (
        "Cuando se haya seleccionado, un contacto de cuenta o de Posventa asignado coordinará "
        "revisiones periódicas de la prestación de servicio acordada, las actividades completadas, "
        "las acciones abiertas y las necesidades próximas."
    ),

    # Configuration Summary and Signatures
    "summary.title": "RESUMEN DE CONFIGURACIÓN GUARDIAN",
    "summary.intro": (
        "El siguiente resumen confirma la configuración Guardian adquirida por el Cliente en virtud "
        "del presente Acuerdo."
    ),
    "summary.customer": "Cliente",
    "summary.site": "Centro",
    "summary.start": "Inicio del contrato",
    "summary.term": "Duración del contrato",
    "summary.equipment": "Equipamiento cubierto",
    "summary.equipment.value": "{{Number_Of_Machines}} máquinas / {{Number_Of_Lines}} líneas de producción",
    "summary.value": "Valor anual / del contrato",
    "summary.scope.title": "Su Guardian",
    "summary.scope.h_module": "Módulo Guardian",
    "summary.scope.h_scope": "Alcance seleccionado",
    "summary.signatures.title": "FIRMAS",
    "summary.signatures.intro": (
        "Al firmar el presente Acuerdo, las Partes confirman su aceptación del Acuerdo Marco y de "
        "todos los Anexos identificados en el Anexo 1 como aplicables."
    ),
    "summary.signatures.company": "Empresa",
    "summary.signatures.customer": "Por el Cliente",
    "summary.signatures.weber": "Por Weber",
    "summary.signatures.name": "Nombre",
    "summary.signatures.position": "Cargo",
    "summary.signatures.place": "Lugar",
    "summary.signatures.date": "Fecha",
    "summary.signatures.signature": "Firma",
}
