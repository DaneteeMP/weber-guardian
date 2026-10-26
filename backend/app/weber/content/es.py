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
    "module.maintenance_inspection": "Mantenimiento e inspección",
    "module.service_support": "Soporte de servicio",
    "module.parts_availability": "Repuestos y disponibilidad",
    "module.blade_solutions": "Soluciones de cuchillas",
    "module.training_optimization": "Formación y optimización",
    "module.digital_services": "Servicios digitales",

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

    # Master Agreement
    "master.title": "ACUERDO MARCO WEBER GUARDIAN",
    "master.kv.agreement_no": "N.º de acuerdo",
    "master.kv.offer_no": "N.º de oferta",
    "master.kv.offer_date": "Fecha de la oferta",
    "master.kv.start_date": "Fecha de inicio del contrato",
    "master.kv.term": "Duración inicial del contrato",
    "master.kv.billing": "Frecuencia de facturación",
    "master.between": "ENTRE",
    "master.weber_definition": "en adelante, «Weber».",
    "master.customer_definition": "en adelante, el «Cliente».",
    "master.parties": "Weber y el Cliente se denominan individualmente «Parte» y conjuntamente «las Partes».",

    # 1. PURPOSE OF THE AGREEMENT
    "master.clause1.title": "1. OBJETIVO DEL ACUERDO",
    "master.clause1.p1": (
        "El presente Acuerdo Guardian tiene por objeto favorecer la operación fiable, eficiente y "
        "económicamente sostenible del equipamiento Weber del Cliente durante todo su ciclo de vida."
    ),
    "master.clause1.p2": (
        "Guardian es un programa posventa modular. En función de los módulos seleccionados por el "
        "Cliente, el Acuerdo puede incluir servicios de inspección y mantenimiento preventivo, "
        "asistencia técnica, servicios de repuestos, soluciones de cuchillas, servicios de formación "
        "y optimización y servicios digitales."
    ),
    "master.clause1.p3": "Solo se incluyen los servicios expresamente identificados en los Anexos aplicables del presente Acuerdo.",
    "master.clause1.goals_intro": "El objetivo del programa Guardian es:",
    "master.clause1.goals": [
        "mejorar la fiabilidad y la disponibilidad del equipamiento;",
        "apoyar el mantenimiento preventivo y la identificación temprana de incidencias técnicas;",
        "reducir las paradas no planificadas evitables;",
        "favorecer una planificación y un gasto de mantenimiento previsibles;",
        "garantizar el acceso a la experiencia técnica de Weber;",
        "optimizar la gestión de repuestos y cuchillas;",
        "mejorar las prácticas de operación y mantenimiento; y",
        "apoyar la optimización continua del equipamiento instalado del Cliente.",
    ],
    "master.clause1.exclusion": (
        "Ningún servicio, descuento, compromiso de respuesta u otro beneficio se considerará incluido "
        "salvo que se establezca expresamente en el presente Acuerdo o en un Anexo que forme parte del mismo."
    ),

    # 2. CONTRACT DOCUMENTS AND MODULAR STRUCTURE
    "master.clause2.title": "2. DOCUMENTOS CONTRACTUALES Y ESTRUCTURA MODULAR",
    "master.clause2.p1": (
        "El presente Acuerdo consta del presente Acuerdo Marco y de los Anexos indicados a "
        "continuación que han sido seleccionados para el Cliente."
    ),
    "master.clause2.annexes": [
        "Anexo 1 - Equipos y condiciones comerciales: siempre aplicable.",
        "Anexo 2 - Mantenimiento e inspección: aplicable solo si se selecciona el módulo de Mantenimiento e inspección.",
        "Anexo 3 - Soporte de servicio: aplicable solo si se selecciona el módulo de Soporte de servicio.",
        "Anexo 4 - Repuestos y disponibilidad: aplicable solo si se selecciona el módulo de Repuestos y disponibilidad.",
        "Anexo 5 - Soluciones de cuchillas: aplicable solo si se selecciona el módulo de Soluciones de cuchillas.",
        "Anexo 6 - Formación y optimización: aplicable solo si se selecciona el módulo de Formación y optimización.",
        "Anexo 7 - Servicios digitales: aplicable solo si se selecciona el módulo de Servicios digitales.",
    ],
    "master.clause2.p2": "Los Anexos aplicables forman parte integrante del presente Acuerdo.",
    "master.clause2.p3": (
        "Los servicios se aplican únicamente a las máquinas, líneas de producción, módulos y "
        "emplazamientos identificados en el Anexo 1, salvo acuerdo en contrario por escrito."
    ),
    "master.clause2.p4": (
        "En caso de conflicto entre los documentos que forman el presente Acuerdo, se aplicará el "
        "siguiente orden de prelación:"
    ),
    "master.clause2.precedence": [
        "Anexo 1 - Equipos y condiciones comerciales;",
        "el Anexo específico del servicio correspondiente;",
        "el presente Acuerdo Marco; y",
        "las Condiciones Generales de Venta aplicables de Weber.",
    ],
    "master.clause2.p5": (
        "Las desviaciones específicas del Cliente expresamente establecidas en el Anexo 1 prevalecerán "
        "sobre las disposiciones estándar relativas a la misma materia."
    ),

    # 3. DEFINITIONS
    "master.clause3.title": "3. DEFINICIONES",
    "master.clause3.definitions": [
        "Equipamiento: las máquinas, módulos, sistemas u otros equipos expresamente listados en el Anexo 1.",
        "Inspección: la evaluación del estado real del Equipamiento con el fin de identificar desgastes, anomalías, el mantenimiento requerido y las acciones necesarias para favorecer su futura operación.",
        "Mantenimiento preventivo: medidas programadas destinadas a reducir la deterioración y el riesgo de avería, incluidos ajuste, lubricación, limpieza, sustitución de piezas de desgaste definidas y otras actividades expresamente incluidas en el ámbito de servicio aplicable.",
        "Mantenimiento correctivo / Reparación: trabajos destinados a restablecer el estado operativo requerido del Equipamiento tras una falla, avería o defecto identificado.",
        "Piezas de desgaste: componentes que, por su función prevista y en función de las condiciones de uso, requieren sustitución periódica.",
        "Repuestos: componentes de sustitución suministrados para el Equipamiento.",
        "Servicios: los servicios Guardian expresamente seleccionados y descritos en los Anexos aplicables.",
        "Visita de servicio: una visita física acordada del personal de Weber o de un servicio autorizado de Weber al emplazamiento del Cliente.",
        "Soporte remoto: asistencia técnica prestada sin visita física, incluidos teléfono, correo electrónico, comunicación digital y, cuando esté disponible y autorizado, conexión remota al Equipamiento.",
        "Año contractual: cada periodo consecutivo de doce meses comenzando en la Fecha de inicio del contrato.",
    ],

    # 4. EQUIPMENT COVERED
    "master.clause4.title": "4. EQUIPAMIENTO CUBIERTO",
    "master.clause4.p1": "El Acuerdo Guardian se aplica exclusivamente al Equipamiento listado en el Anexo 1.",
    "master.clause4.p2": "El Anexo 1 identificará, cuando corresponda:",
    "master.clause4.identify": [
        "la línea de producción del Cliente;",
        "la referencia de la máquina Weber;",
        "el número de serie;",
        "el tipo de equipamiento;",
        "los módulos incluidos;",
        "la frecuencia de servicio;",
        "el tiempo de inspección o servicio planificado;",
        "los módulos Guardian seleccionados;",
        "el precio de servicio aplicable; y",
        "cualquier condición comercial específica de la máquina.",
    ],
    "master.clause4.p3": (
        "El Cliente notificará por escrito a Weber cualquier traslado, modificación material, "
        "enajenación o venta del Equipamiento cubierto por el presente Acuerdo."
    ),
    "master.clause4.p4": (
        "Cuando el Equipamiento se venda o se traslade de forma permanente a otra persona jurídica "
        "o emplazamiento, la continuación del Acuerdo Guardian quedará sujeta a la confirmación "
        "por escrito de Weber."
    ),
    "master.clause4.p5": "Las Partes podrán añadir o retirar Equipamiento durante la vigencia del contrato mediante enmienda por escrito al Anexo 1.",

    # 5. GENERAL SERVICE PRINCIPLES
    "master.clause5.title": "5. PRINCIPIOS GENERALES DE SERVICIO",
    "master.clause5.p1": (
        "Weber prestará los Servicios seleccionados con personal adecuadamente cualificado y de "
        "conformidad con los estándares técnicos generalmente aceptados y los procedimientos de "
        "servicio de Weber aplicables al Equipamiento correspondiente."
    ),
    "master.clause5.p2": "Weber podrá emplear empresas afiliadas cualificadas o servicios autorizados de Weber para la prestación de los Servicios.",
    "master.clause5.p3": (
        "Weber determinará el número y la cualificación de los técnicos razonablemente necesarios "
        "para la actividad de servicio aplicable, teniendo en cuenta la configuración del "
        "Equipamiento y el alcance del trabajo."
    ),
    "master.clause5.p4": "El Acuerdo Guardian no constituye una garantía de que el Equipamiento operará sin interrupciones ni averías.",
    "master.clause5.excluded_intro": (
        "Salvo que se incluya expresamente en un Anexo aplicable, no se incluyen en la tarifa "
        "Guardian fija los siguientes conceptos:"
    ),
    "master.clause5.excluded": [
        "reparaciones correctivas;",
        "piezas de sustitución;",
        "piezas de desgaste y consumibles;",
        "mejoras o modificaciones;",
        "equipamiento de terceros;",
        "trabajos fuera de las horas de servicio acordadas;",
        "intervenciones de urgencia;",
        "desplazamientos adicionales;",
        "equipos de acceso especiales;",
        "materiales de producción;",
        "herramientas especiales no requeridas habitualmente para el Equipamiento Weber correspondiente; y",
        "trabajos derivados de un uso indebido, daños, causas externas o modificaciones no aprobadas por Weber.",
    ],
    "master.clause5.p5": "Dichos servicios podrán presupuestarse y pedirse por separado.",

    # 6. CUSTOMER COOPERATION
    "master.clause6.title": "6. COLABORACIÓN DEL CLIENTE",
    "master.clause6.p1": "El Cliente prestará la colaboración razonablemente requerida para que Weber pueda prestar los Servicios.",
    "master.clause6.p2": "En particular, el Cliente se asegurará de que:",
    "master.clause6.obligations": [
        "el personal de Weber tenga acceso seguro y puntual al Equipamiento correspondiente;",
        "el Equipamiento esté disponible en la hora acordada;",
        "el Equipamiento se encuentre en un estado razonablemente limpio y accesible;",
        "la producción pueda interrumpirse cuando sea necesario para el trabajo acordado;",
        "estén disponibles los servicios auxiliares y las conexiones técnicas requeridas para el trabajo, incluidos electricidad, aire comprimido, agua, acceso a red o acceso VPN cuando corresponda;",
        "haya personal del Cliente adecuado disponible cuando se requiera asistencia;",
        "haya suficiente producto original disponible cuando se requiera una prueba de producción o funcionalidad;",
        "se informe a Weber por adelantado de las fallas conocidas, condiciones de operación anormales o requisitos de seguridad;",
        "se comuniquen a Weber todos los requisitos de seguridad y salud específicos del emplazamiento antes de comenzar los trabajos; y",
        "haya disponible un representante del Cliente con autoridad suficiente para aprobar trabajos adicionales o la sustitución de componentes cuando sea necesario.",
    ],
    "master.clause6.p3": (
        "Cualquier retraso, tiempo de espera o gasto adicional derivado del incumplimiento por el "
        "Cliente de estas obligaciones podrá facturarse por separado de conformidad con las tarifas "
        "aplicables de Weber."
    ),

    # 7. SCHEDULING
    "master.clause7.title": "7. PLANIFICACIÓN",
    "master.clause7.p1": (
        "Las inspecciones planificadas, visitas de mantenimiento, formación y otros Servicios "
        "planificados se coordinarán entre Weber y el Cliente."
    ),
    "master.clause7.p2": "Weber hará esfuerzos razonables para comunicar al Cliente con antelación la fecha prevista.",
    "master.clause7.p3": "El plazo de preaviso aplicable, cuando se acuerde específicamente, se indicará en el Anexo correspondiente o en el Anexo 1.",
    "master.clause7.p4": "Si alguna de las Partes no puede realizar una actividad acordada en la fecha planificada, informará a la otra Parte lo antes razonablemente posible.",
    "master.clause7.p5": (
        "Cuando una visita planificada no pueda realizarse por motivos atribuibles al Cliente, "
        "Weber podrá facturar los costes razonablemente incurridos, incluidos desplazamiento, "
        "alojamiento, tiempo de espera y capacidad de personal reservada."
    ),

    # 8. ADDITIONAL WORK IDENTIFIED DURING A SERVICE ACTIVITY
    "master.clause8.title": "8. TRABAJOS ADICIONALES IDENTIFICADOS DURANTE UNA ACTIVIDAD DE SERVICIO",
    "master.clause8.p1": "Cuando una inspección, actividad de mantenimiento, auditoría u otro servicio Guardian identifique trabajos adicionales, Weber informará al Cliente.",
    "master.clause8.p2": "Salvo que el Anexo 1 disponga expresamente lo contrario, dichos trabajos adicionales no formarán automáticamente parte de la tarifa fija Guardian.",
    "master.clause8.p3": (
        "El mantenimiento correctivo, las reparaciones, las modificaciones, las mejoras y la "
        "sustitución de piezas identificadas durante una inspección requerirán la autorización del Cliente."
    ),
    "master.clause8.p4": "Cuando proceda, Weber podrá emitir un presupuesto por separado o una recomendación de repuestos tras la actividad de servicio.",
    "master.clause8.p5": (
        "No se realizará intencionadamente ningún trabajo adicional facturable sin la autorización "
        "del Cliente, salvo cuando sea razonablemente necesario actuar de inmediato para prevenir "
        "un riesgo de seguridad inminente y dicha acción esté permitida por la legislación aplicable "
        "y las normas del emplazamiento."
    ),

    # 9. PRICES AND PAYMENT
    "master.clause9.title": "9. PRECIOS Y PAGO",
    "master.clause9.p1": "Los precios aplicables al Acuerdo Guardian se indican en el Anexo 1.",
    "master.clause9.p2": "Salvo que se establezca expresamente lo contrario, todos los precios no incluyen el IVA ni otros impuestos aplicables.",
    "master.clause9.p3": (
        "La moneda aplicable, la frecuencia de facturación, las condiciones de pago, las condiciones "
        "de desplazamiento, las condiciones de porte, los descuentos y las tarifas de servicio "
        "adicionales serán las especificadas en el Anexo 1 o en el Anexo del servicio correspondiente."
    ),
    "master.clause9.p4": "Las tarifas recurrentes de Guardian se facturarán según la frecuencia de facturación indicada en el Anexo 1.",
    "master.clause9.p5": (
        "Los servicios, materiales y gastos no incluidos en la tarifa Guardian acordada se "
        "facturarán por separado a las tarifas acordadas aplicables."
    ),
    "master.clause9.p6": "Weber podrá ajustar los precios recurrentes de conformidad con el mecanismo de ajuste anual de precios indicado en el Anexo 1.",
    "master.clause9.p7": (
        "Cualquier descuento acordado se aplicará únicamente a las categorías expresamente "
        "identificadas en el Anexo correspondiente y no se acumulará con otros descuentos salvo "
        "acuerdo expreso."
    ),

    # 10. PARTS AND MATERIALS
    "master.clause10.title": "10. PIEZAS Y MATERIALES",
    "master.clause10.p1": (
        "Salvo que se incluyan específicamente en el Anexo 1 o en un Anexo de servicio aplicable, "
        "los repuestos, piezas de desgaste, cuchillas, lubricantes y otros materiales no están "
        "incluidos en la tarifa de servicio Guardian."
    ),
    "master.clause10.p2": (
        "Las piezas suministradas por Weber se facturarán al precio aplicable en la fecha de "
        "suministro, menos cualquier descuento Guardian expresamente acordado en virtud del Anexo 4 "
        "o del Anexo 5."
    ),
    "master.clause10.p3": (
        "Cuando los componentes sustituidos se pongan a disposición del Cliente para su inspección, "
        "el Cliente será responsable de su posterior eliminación, salvo acuerdo en contrario."
    ),
    "master.clause10.p4": (
        "Weber no responderá de los defectos, daños, rendimiento reducido o efectos consecuentes "
        "causados por componentes no originales, modificaciones no autorizadas o trabajos realizados "
        "por terceros, en la medida permitida por la legislación aplicable."
    ),
    "master.clause10.p5": (
        "La propiedad de los bienes suministrados permanecerá en Weber hasta el pago íntegro, "
        "cuando esté permitido por las condiciones locales y la legislación aplicable."
    ),

    # 11. ACCEPTANCE AND SERVICE REPORTING
    "master.clause11.title": "11. ACEPTACIÓN E INFORMES DE SERVICIO",
    "master.clause11.p1": (
        "Cuando la naturaleza de un Servicio permita la verificación funcional, el Cliente "
        "facilitará a Weber una oportunidad razonable de probar el Equipamiento tras la "
        "finalización de la actividad."
    ),
    "master.clause11.p2": (
        "Cuando el Cliente identifique una deficiencia material en la prestación de un Servicio, "
        "notificará a Weber sin dilación indebida y facilitará información suficiente para que "
        "Weber pueda evaluar el asunto."
    ),
    "master.clause11.p3": (
        "Si un Servicio ha quedado demostrablemente realizado al margen del alcance acordado y "
        "Weber es responsable de la deficiencia, Weber deberá, como remedio principal, represtar o "
        "corregir el Servicio afectado dentro de un plazo razonable."
    ),
    "master.clause11.p4": (
        "Los informes de servicio, informes de inspección, informes de auditoría y recomendaciones "
        "documentan el estado observado en el momento de la actividad y no constituyen una garantía "
        "del rendimiento futuro de la máquina."
    ),

    # 12. WARRANTY AND LIABILITY
    "master.clause12.title": "12. GARANTÍA Y RESPONSABILIDAD",
    "master.clause12.p1": "Weber prestará los Servicios con el cuidado y la competencia profesional razonables.",
    "master.clause12.p2": (
        "La responsabilidad de Weber se regirá por las disposiciones imperantes de la legislación "
        "aplicable y por las Condiciones Generales aplicables de Weber."
    ),
    "master.clause12.p3": (
        "En la máxima medida permitida por la ley, Weber no responderá de los daños indirectos o "
        "consecuentes, incluidas la pérdida de producción, la pérdida de beneficios, la pérdida de "
        "negocios u otros perjuicios comerciales indirectos, salvo que dicha limitación esté "
        "prohibida por la legislación aplicable."
    ),
    "master.clause12.p4": "Nada en el presente Acuerdo excluirá la responsabilidad que legalmente no pueda excluirse ni limitarse.",
    "master.clause12.p5": (
        "Cuando un incumplimiento o retraso resulte de circunstancias fuera del control razonable "
        "de Weber, incluido el incumplimiento o retraso de proveedores, alteraciones del transporte, "
        "conflictos laborales, acontecimientos naturales, medidas gubernamentales, incidentes "
        "cibernéticos, epidemias u otros acontecimientos de fuerza mayor, el periodo de prestación "
        "afectado se ampliará en la medida razonablemente necesaria."
    ),

    # 13. CONTRACT TERM AND RENEWAL
    "master.clause13.title": "13. VIGENCIA Y RENOVACIÓN DEL CONTRATO",
    "master.clause13.p1": "El presente Acuerdo entra en vigor en la Fecha de inicio del contrato indicada en el Anexo 1.",
    "master.clause13.term": "Duración inicial",
    "master.clause13.renewal": "Duración de renovación",
    "master.clause13.notice": "Plazo de preaviso",
    "master.clause13.p2": (
        "Salvo que se indique lo contrario en el Anexo 1, el Acuerdo se renovará automáticamente "
        "por sucesivos periodos de renovación, salvo denuncia por escrito dentro del plazo de "
        "preaviso aplicable."
    ),
    "master.clause13.p3": (
        "La terminación o expiración del Acuerdo Marco dará por terminados todos los Anexos de "
        "servicio, salvo acuerdo expreso en contrario."
    ),
    "master.clause13.p4": "Los servicios opcionales individuales pueden tener fechas de inicio o expiración diferentes cuando se establezca expresamente en el Anexo correspondiente.",

    # 14. CHANGES TO THE AGREEMENT
    "master.clause14.title": "14. MODIFICACIONES DEL ACUERDO",
    "master.clause14.p1": (
        "Las modificaciones del Equipamiento cubierto, la frecuencia de servicio, los módulos "
        "Guardian, los descuentos, los niveles de servicio, los precios u otras condiciones "
        "contractuales materiales deberán documentarse por escrito."
    ),
    "master.clause14.p2": "Un Anexo actualizado generado y aceptado por ambas Partes podrá constituir dicha enmienda por escrito.",

    # 15. CONFIDENTIALITY
    "master.clause15.title": "15. CONFIDENCIALIDAD",
    "master.clause15.p1": (
        "Cada Parte mantendrá confidencial toda la información comercial, técnica y operativa no "
        "pública recibida de la otra Parte en relación con el presente Acuerdo."
    ),
    "master.clause15.p2": "Dicha información se utilizará únicamente para la prestación y administración de la relación Guardian.",
    "master.clause15.p3": "Esta obligación no se aplicará a la información que:",
    "master.clause15.exceptions": [
        "ya forme lícitamente parte del dominio público;",
        "fuera lícitamente conocida por la Parte receptora antes de su divulgación;",
        "se reciba lícitamente de un tercero sin restricciones de confidencialidad; o",
        "deba divulgarse por mandato legal o de una autoridad competente.",
    ],

    # 16. INTELLECTUAL PROPERTY
    "master.clause16.title": "16. PROPIEDAD INTELECTUAL",
    "master.clause16.p1": (
        "Todos los derechos de propiedad intelectual sobre la documentación de Weber, los "
        "métodos de servicio, las listas de verificación, el software, la información técnica, "
        "los materiales de formación, los análisis y otros contenidos propietarios de Weber "
        "permanecerán propiedad de Weber o del titular de los derechos correspondientes."
    ),
    "master.clause16.p2": "El Cliente podrá utilizar internamente la documentación facilitada en virtud del presente Acuerdo para la operación y el mantenimiento de su Equipamiento.",
    "master.clause16.p3": "No se transfiere al Cliente ningún derecho de propiedad intelectual salvo acuerdo expreso por escrito.",

    # 17. ASSIGNMENT AND SERVICE PARTNERS
    "master.clause17.title": "17. CESIÓN Y SOCIOS DE SERVICIO",
    "master.clause17.p1": "Weber podrá cumplir sus obligaciones a través de empresas del grupo Weber o de socios de servicio cualificados y autorizados de Weber.",
    "master.clause17.p2": "Weber podrá ceder los derechos y obligaciones derivados del presente Acuerdo a otra empresa del grupo Weber, sujeto a la legislación aplicable.",
    "master.clause17.p3": (
        "El Cliente no podrá ceder el presente Acuerdo a un tercero sin el consentimiento previo "
        "por escrito de Weber, el cual no se denegará injustificadamente cuando la continuación de "
        "la relación contractual sea comercial y técnicamente viable."
    ),

    # 18. GOVERNING LAW AND JURISDICTION
    "master.clause18.title": "18. LEY APLICABLE Y JURISDICCIÓN",
    "master.clause18.law": "Ley aplicable",
    "master.clause18.jurisdiction": "Jurisdicción",
    "master.clause18.p1": "Las disposiciones anteriores quedan sujetas en cada caso a la legislación imperante aplicable.",

    # 19. GENERAL PROVISIONS
    "master.clause19.title": "19. DISPOSICIONES GENERALES",
    "master.clause19.p1": (
        "Si alguna disposición del presente Acuerdo se declarase inválida o inaplicable, las "
        "disposiciones restantes seguirán vigentes."
    ),
    "master.clause19.p2": "El hecho de que una de las Partes no ejerza un derecho contractual no constituirá la renuncia a dicho derecho.",
    "master.clause19.p3": (
        "El presente Acuerdo y sus Anexos aplicables constituyen el acuerdo entre las Partes "
        "respecto a los Servicios Guardian aquí descritos y sustituyen las propuestas o "
        "entendimientos previos relativos específicamente al mismo alcance de servicio, salvo que "
        "se incorporen expresamente."
    ),
    "master.clause19.p4": "Las enmiendas se formalizarán por escrito.",
    "master.clause19.p5": (
        "Podrán utilizarse firmas electrónicas cuando legalmente esté permitido y tendrán los "
        "mismos efectos que las firmas manuscritas."
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
    "annex2.tagline": "Inspección, mantenimiento preventivo y servicios de estado de la máquina.",
    "annex2.purpose.title": "1. Objeto",
    "annex2.purpose.p1": (
        "El módulo de Mantenimiento e Inspección tiene por objeto evaluar y mantener el estado del "
        "Equipamiento identificado en el Anexo 1, identificar las acciones técnicas requeridas y "
        "favorecer la operación fiable y la planificación del mantenimiento."
    ),
    "annex2.purpose.p2": "Las actividades exactas incluidas dependen de las opciones seleccionadas en la configuración Guardian.",
    "annex2.inspection.title": "2. Inspección",
    "annex2.inspection.p1": "Weber realizará inspecciones del Equipamiento seleccionado con la frecuencia indicada en el Anexo 1.",
    "annex2.inspection.p2": "Una inspección podrá incluir, cuando sea aplicable al Equipamiento seleccionado:",
    "annex2.inspection.includes": [
        "revisión del estado general de la máquina;",
        "inspección basada en la lista de verificación específica de Weber para la máquina o el módulo;",
        "revisión de los sensores y componentes eléctricos relevantes;",
        "inspección de transmisiones, correas y componentes mecánicos;",
        "inspección de componentes neumáticos;",
        "inspección de juntas y carcasas de la máquina;",
        "verificación y ajuste de componentes mecánicamente móviles cuando sea razonablemente necesario;",
        "revisión de los ajustes relevantes de la máquina;",
        "identificación de desgastes o anomalías visibles;",
        "identificación de reparaciones o necesidades de mantenimiento pendientes;",
        "exposición de las incidencias conocidas con el personal responsable del Cliente; y",
        "verificación funcional tras la inspección cuando proceda.",
    ],
    "annex2.inspection.p3": (
        "Cuando sea útil y operativamente posible, Weber podrá revisar el proceso de producción "
        "utilizando el producto original del Cliente."
    ),
    "annex2.inspection.p4": (
        "La apertura de zonas específicas protegidas de la máquina, como carcasas de báscula o de "
        "cabezas de corte, se realizará cuando sea técnicamente apropiado y esté acordado."
    ),
    "annex2.checklist.title": "3. Lista de verificación de la máquina",
    "annex2.checklist.p1": "Weber documentará la inspección mediante la lista de verificación de inspección aplicable de Weber.",
    "annex2.checklist.p2": "La lista de verificación registra los elementos inspeccionados y su estado observado en el momento de la inspección.",
    "annex2.checklist.p3": (
        "La lista de verificación tiene carácter de registro técnico de servicio y no constituye "
        "una certificación de que el Equipamiento esté libre de defectos ni de que no pueda ocurrir "
        "ninguna avería futura."
    ),
    "annex2.report.title": "4. Informe de inspección",
    "annex2.report.p1": "Tras la inspección, Weber facilitará un informe de inspección que resuma los hallazgos principales.",
    "annex2.report.p2": "El informe podrá incluir:",
    "annex2.report.includes": [
        "hallazgos sobre el estado;",
        "desgastes identificados;",
        "mantenimiento o reparaciones recomendados;",
        "repuestos recomendados;",
        "observaciones técnicas;",
        "riesgos identificados que requieren atención adicional; y",
        "prioridades o acciones siguientes recomendadas.",
    ],
    "annex2.report.p3": (
        "Cuando proceda, Weber podrá preparar un presupuesto por separado para las piezas, "
        "reparaciones, mejoras u otras actividades derivadas de la inspección."
    ),
    "annex2.preventive.title": "5. Mantenimiento preventivo",
    "annex2.preventive.p1": "Weber realizará las actividades de mantenimiento preventivo expresamente definidas para el Equipamiento en el Anexo 1.",
    "annex2.preventive.p2": "El mantenimiento preventivo podrá incluir:",
    "annex2.preventive.includes": [
        "ajuste mecánico;",
        "lubricación;",
        "limpieza de componentes técnicamente relevantes;",
        "sustitución de filtros, juntas o componentes de desgaste definidos;",
        "comprobación y ajuste de transmisiones y correas;",
        "comprobación de elementos neumáticos;",
        "comprobación de componentes eléctricos y sensores; y",
        "otras tareas de mantenimiento preventivo específicas de la máquina identificadas en el plan de mantenimiento aplicable de Weber.",
    ],
    "annex2.preventive.p3": (
        "Las piezas de sustitución, las piezas de desgaste y los consumibles no están incluidos "
        "salvo que se establezca expresamente en el Anexo 1 o en un kit de mantenimiento acordado."
    ),
    "annex2.kit.title": "6. Repuestos / kit de mantenimiento",
    "annex2.kit.p1": (
        "El kit de mantenimiento contendrá únicamente las piezas expresamente identificadas en el "
        "presupuesto aplicable o en el programa de equipamiento."
    ),
    "annex2.kit.p2": "El precio del kit se mostrará por separado en el Anexo 1.",
    "annex2.kit.p3": "Las piezas no utilizadas quedan sujetas a las condiciones comerciales indicadas en el Anexo 1.",
    "annex2.repairs.title": "7. Mantenimiento adicional y reparaciones",
    "annex2.repairs.p1": (
        "Las reparaciones y el mantenimiento correctivo identificados durante una inspección no "
        "están incluidos en el precio estándar de inspección, salvo que se establezca específicamente lo contrario."
    ),
    "annex2.repairs.p2": "Cuando se recomienden trabajos adicionales, Weber obtendrá la aprobación del Cliente o emitirá un presupuesto por separado.",
    "annex2.frequency.title": "8. Frecuencia de inspección",
    "annex2.frequency.value": "Frecuencia",
    "annex2.frequency.planned": "Inspecciones planificadas por año contractual",
    "annex2.frequency.p1": "El calendario real se coordinará entre Weber y el Cliente.",
    "annex2.hours.title": "9. Horas de servicio",
    "annex2.hours.p1": "Los servicios se realizarán normalmente durante: {{Standard_Service_Hours}}",
    "annex2.hours.p2": "Los trabajos solicitados fuera de estas horas podrán conllevar cargos adicionales.",

    # Annex 3 - Service Support
    "annex3.title": "ANEXO 3 - SOPORTE DE SERVICIO",
    "annex3.tagline": "Línea directa, soporte remoto y respuesta técnica prioritaria.",
    "annex3.purpose.title": "1. Objeto",
    "annex3.purpose.p1": (
        "El módulo de Soporte de servicio facilita al Cliente acceso a la asistencia técnica de "
        "Weber para el Equipamiento cubierto por el presente Acuerdo."
    ),
    "annex3.purpose.p2": "El nivel de servicio exacto depende de las opciones seleccionadas a continuación.",
    "annex3.hotline.title": "2. Línea directa estándar",
    "annex3.hotline.p1": "El Cliente tendrá acceso a la línea directa de servicio de Weber durante las horas de soporte aplicables.",
    "annex3.hotline.hours": "Horas de soporte",
    "annex3.hotline.phone": "Teléfono",
    "annex3.hotline.email": "Correo electrónico",
    "annex3.hotline.p2": "La línea directa proporciona soporte técnico de primer nivel y coordinación.",
    "annex3.hotline.p3": (
        "Cuando la incidencia no pueda resolverse a través de la línea directa, Weber podrá "
        "recomendar Soporte remoto, una visita de servicio en sitio, repuestos u otra acción técnica."
    ),
    "annex3.hotline.p4": (
        "El servicio en sitio no queda incluido por el solo hecho de contar con soporte de Línea "
        "directa estándar, salvo que se establezca expresamente en el Anexo 1."
    ),
    "annex3.remote.title": "3. Soporte remoto",
    "annex3.remote.p1": (
        "Cuando esté técnicamente disponible y autorizado por el Cliente, Weber podrá prestar "
        "diagnóstico y asistencia técnica remotos."
    ),
    "annex3.remote.p2": (
        "El Cliente facilitará las conexiones de red, el acceso VPN, la autorización de usuarios y "
        "las demás condiciones técnicas razonablemente necesarias para el acceso remoto."
    ),
    "annex3.remote.p3": "El soporte remoto podrá incluir:",
    "annex3.remote.includes": [
        "análisis remoto de fallos;",
        "revisión del estado de la máquina o de la información de diagnóstico;",
        "asistencia en comprobaciones de parámetros o configuración;",
        "apoyo al personal de mantenimiento del Cliente; y",
        "recomendaciones de acciones siguientes.",
    ],
    "annex3.remote.p4": "El Soporte remoto no garantiza que un fallo pueda corregirse sin una intervención en sitio.",
    "annex3.priority.title": "4. Respuesta prioritaria",
    "annex3.priority.p1": (
        "Las solicitudes relativas al Equipamiento cubierto por el presente Acuerdo recibirán un "
        "trato prioritario dentro de la organización de servicio de Weber en comparación con las "
        "solicitudes estándar sin contrato, sujeto a la disponibilidad de técnicos y al nivel de "
        "servicio aplicable."
    ),
    "annex3.priority.target": "Respuesta inicial objetivo",
    "annex3.priority.p2": (
        "La Respuesta prioritaria se refiere a la priorización de la solicitud de soporte. No "
        "constituye un tiempo de reparación garantizado, una disponibilidad de la máquina garantizada "
        "ni un tiempo de llegada en sitio garantizado, salvo que se establezca expresamente lo "
        "contrario en el Anexo 1."
    ),

    # Annex 4 - Parts & Availability
    "annex4.title": "ANEXO 4 - REPUESTOS Y DISPONIBILIDAD",
    "annex4.tagline": "Condiciones comerciales de repuestos, trato prioritario y stock recomendado.",
    "annex4.purpose.title": "1. Objeto",
    "annex4.purpose.p1": (
        "El módulo de Repuestos y disponibilidad respalda la planificación estructurada de "
        "repuestos y el acceso a los repuestos originales de Weber para el Equipamiento cubierto "
        "por el presente Acuerdo."
    ),
    "annex4.discount.title": "2. Descuento sobre repuestos",
    "annex4.discount.p1": (
        "El Cliente recibirá el siguiente descuento sobre los repuestos originales elegibles de "
        "Weber para el Equipamiento cubierto por el Acuerdo Guardian:"
    ),
    "annex4.discount.amount": "Descuento Guardian sobre repuestos {{Parts_Discount}} %",
    "annex4.discount.p2": "El descuento se aplica a los repuestos originales de Weber, salvo que se indique lo contrario.",
    "annex4.discount.p3": "Los siguientes conceptos pueden quedar excluidos:",
    "annex4.discount.excluded": [
        "piezas de recambio (exchange);",
        "cuchillas;",
        "artículos de precio especial;",
        "productos de terceros;",
        "gastos de porte y urgencia;",
        "servicios y mano de obra; y",
        "artículos ya sujetos a otro precio especial o descuento.",
    ],
    "annex4.discount.p4": "Los descuentos no son acumulables salvo acuerdo expreso.",
    "annex4.handling.title": "3. Trato prioritario",
    "annex4.handling.p1": (
        "Las consultas y pedidos de piezas relativos al Equipamiento cubierto por el presente "
        "Acuerdo recibirán trato prioritario dentro de la organización de repuestos aplicable de Weber."
    ),
    "annex4.handling.p2": "El trato prioritario incluye una aceleración del procesamiento interno cuando sea razonablemente posible.",
    "annex4.handling.p3": (
        "No constituye un tiempo de entrega garantizado cuando la pieza solicitada no esté "
        "disponible en stock o cuando la entrega dependa de proveedores externos, la producción o "
        "el transporte."
    ),
    "annex4.parts_list.title": "4. Lista de repuestos recomendados",
    "annex4.parts_list.p1": (
        "Weber facilitará, cuando esté disponible técnica y comercialmente, una lista de repuestos "
        "recomendados para el Equipamiento seleccionado."
    ),
    "annex4.parts_list.categories": [
        "A - Artículos locales / de disponibilidad inmediata: Piezas normalmente disponibles en la organización responsable de Weber.",
        "B - Artículos de stock central: Piezas normalmente disponibles en el stock central de Weber.",
        "C - Artículos recomendados en stock del Cliente: repuestos críticos o de mayor riesgo que Weber recomienda mantener localmente al Cliente.",
        "D - Piezas de desgaste: Piezas que requieren sustitución en función del uso.",
        "E - Piezas a medida / de largo plazo: Piezas que normalmente no se mantienen en stock y pueden requerir fabricación o plazos de suministro prolongados.",
    ],
    "annex4.parts_list.p2": (
        "La lista de repuestos recomendados constituye una recomendación basada en la "
        "configuración de la máquina y la información de servicio disponibles. No es una garantía "
        "de que esté cubierto cada posible escenario de avería."
    ),
    "annex4.delivery.title": "5. Condiciones de entrega",
    "annex4.delivery.p1": "La disponibilidad de stock y las condiciones de entrega quedan sujetas al Anexo 1.",
    "annex4.delivery.condition": "Condición de entrega estándar",
    "annex4.delivery.threshold": "Umbral de porte gratuito",
    "annex4.delivery.courier": "Costes de urgencia / mensajería",
    "annex4.delivery.courier.value": "Se facturan por separado, salvo acuerdo en contrario.",

    # Annex 5 - Blade Solutions
    "annex5.title": "ANEXO 5 - SOLUCIONES DE CUCHILLAS",
    "annex5.tagline": "Condiciones comerciales, disponibilidad y asistencia técnica de los programas de cuchillas de Weber.",
    "annex5.intro": (
        "El módulo de Soluciones de cuchillas tiene por objeto favorecer la selección correcta, la "
        "disponibilidad, el uso y la gestión de las cuchillas de Weber, incluido el principio "
        "«Cuchilla correcta, aplicación correcta»."
    ),
    "annex5.discount.title": "1. Descuento sobre cuchillas",
    "annex5.discount.p1": "El Cliente recibirá el siguiente descuento Guardian sobre las cuchillas elegibles de Weber:",
    "annex5.discount.amount": "Descuento sobre cuchillas {{Blade_Discount}} %",
    "annex5.discount.p2": (
        "Las cuchillas aplicables, los emplazamientos del Cliente, las máquinas, las cantidades "
        "comprometidas y cualquier precio especial se listarán en el programa comercial cuando sea necesario."
    ),
    "annex5.discount.p3": (
        "Los descuentos sobre cuchillas no se acumulan con otras promociones de cuchillas o "
        "precios especiales salvo acuerdo expreso."
    ),
    "annex5.discount.p4": (
        "Cuando se acuerden precios de cuchillas a plazo fijo, el plazo aplicable y las condiciones "
        "de precio se indicarán en el Anexo 1."
    ),
    "annex5.stock.title": "2. Acuerdo de stock",
    "annex5.stock.p1": "Weber y el Cliente podrán establecer un concepto de stock de cuchillas acordado en función del consumo previsto.",
    "annex5.stock.p2": "El acuerdo de stock definirá, cuando corresponda:",
    "annex5.stock.defines": [
        "las referencias de cuchillas;",
        "la cantidad de stock acordada;",
        "el stock mínimo;",
        "el stock máximo;",
        "el consumo anual previsto;",
        "el método de reposición;",
        "la ubicación del stock;",
        "la titularidad del stock;",
        "las condiciones de entrega; y",
        "el tratamiento del stock obsoleto o no utilizado.",
    ],
    "annex5.stock.p3": (
        "El Cliente facilitará información de consumo razonablemente precisa y notificará a Weber "
        "los cambios materiales en la producción o la demanda de cuchillas."
    ),
    "annex5.stock.p4": (
        "El acuerdo de stock tiene por objeto mejorar la disponibilidad pero no constituye una "
        "garantía incondicional de suministro ininterrumpido en circunstancias fuera del control "
        "razonable de Weber."
    ),
    "annex5.sharpening.title": "3. Evaluación del afilado",
    "annex5.sharpening.p1": "Weber evaluará el proceso y la capacidad de afilado de cuchillas del Cliente según lo acordado.",
    "annex5.sharpening.p2": "La evaluación podrá incluir:",
    "annex5.sharpening.includes": [
        "el equipo de afilado;",
        "el proceso de afilado;",
        "el manejo de cuchillas;",
        "el estado de las cuchillas;",
        "los parámetros de rectificado;",
        "las prácticas de mantenimiento;",
        "el almacenamiento de cuchillas;",
        "la consistencia del proceso; y",
        "oportunidades de mejora.",
    ],
    "annex5.sharpening.p3": "Weber podrá emitir recomendaciones tras la evaluación.",
    "annex5.sharpening.p4": (
        "Salvo inclusión específica, no se incluyen la implantación de esas recomendaciones, las "
        "reparaciones o modificaciones del equipo de afilado ni la formación adicional."
    ),
    "annex5.application.title": "4. Revisión de la aplicación de cuchillas",
    "annex5.application.p1": (
        "Cuando esté incluido en el programa de cuchillas seleccionado, Weber podrá revisar la "
        "combinación cuchilla-producto con el objetivo de favorecer el principio «Cuchilla "
        "correcta, aplicación correcta»."
    ),
    "annex5.application.p2": (
        "Las recomendaciones podrán tener en cuenta el tipo de producto, las condiciones de "
        "corte, la configuración de la máquina, la geometría de la cuchilla y los requisitos operativos."
    ),

    # Annex 6 - Training & Optimization
    "annex6.title": "ANEXO 6 - FORMACIÓN Y OPTIMIZACIÓN",
    "annex6.tagline": "Formación de operadores, formación de mantenimiento, optimización de línea y auditorías EPIP.",
    "annex6.intro": (
        "El módulo de Formación y optimización ofrece actividades seleccionadas destinadas a "
        "mejorar la operación de las máquinas, la capacidad de mantenimiento y el rendimiento de "
        "la producción."
    ),
    "annex6.operator.title": "1. Formación de operadores",
    "annex6.operator.p1": "Weber impartirá formación dirigida a los operadores para el Equipamiento seleccionado.",
    "annex6.operator.p2": "El contenido de la formación podrá incluir, en función de la máquina y de los objetivos acordados:",
    "annex6.operator.includes": [
        "la operación correcta de la máquina;",
        "los ajustes básicos de la máquina;",
        "las rutinas de operación;",
        "el cambio de producto;",
        "las comprobaciones a nivel de operador;",
        "las consideraciones de limpieza e inspección;",
        "la identificación de comportamientos anormales de la máquina; y",
        "las buenas prácticas de operación.",
    ],
    "annex6.operator.quantity": "Número de sesiones / días",
    "annex6.operator.p3": "La formación se impartirá al personal designado por el Cliente.",
    "annex6.operator.p4": (
        "Salvo que se establezca expresamente lo contrario, la formación no constituye una "
        "certificación formal del personal del Cliente."
    ),
    "annex6.maintenance.title": "2. Formación de mantenimiento",
    "annex6.maintenance.p1": "Weber impartirá formación técnica al personal de mantenimiento del Cliente.",
    "annex6.maintenance.p2": "La formación podrá incluir:",
    "annex6.maintenance.includes": [
        "la construcción de la máquina y sus principios funcionales;",
        "el mantenimiento preventivo;",
        "los puntos de inspección;",
        "la identificación de piezas de desgaste;",
        "la metodología de resolución de problemas;",
        "el ajuste mecánico;",
        "los componentes eléctricos o neumáticos relevantes;",
        "la documentación de mantenimiento; y",
        "las prácticas de mantenimiento recomendadas.",
    ],
    "annex6.maintenance.quantity": "Número de sesiones / días",
    "annex6.optimization.title": "3. Optimización de línea",
    "annex6.optimization.p1": (
        "Weber realizará una revisión acordada de la línea de producción seleccionada con el "
        "objetivo de identificar oportunidades de mejora del rendimiento."
    ),
    "annex6.optimization.p2": "La actividad podrá incluir:",
    "annex6.optimization.includes": [
        "la revisión de los parámetros de la máquina;",
        "la observación de la producción;",
        "el análisis de las condiciones de operación;",
        "la revisión de la interacción entre líneas;",
        "la identificación de restricciones de rendimiento;",
        "el ajuste de parámetros seleccionados cuando proceda; y",
        "recomendaciones de mejora adicional.",
    ],
    "annex6.optimization.quantity": "Número de actividades de optimización",
    "annex6.optimization.p3": (
        "La Optimización de línea no constituye una garantía de una producción, rendimiento, OEE, "
        "reducción de giveaway u otra mejora del rendimiento determinados, salvo que se acuerde "
        "expresamente por escrito un compromiso de rendimiento específico."
    ),
    "annex6.epip.title": "4. Auditoría EPIP",
    "annex6.epip.p1": "Weber realizará una auditoría EPIP en el Equipamiento o las líneas especificadas en el Anexo 1.",
    "annex6.epip.p2": (
        "La auditoría incluirá una evaluación de la línea seleccionada y un informe que identifique "
        "los hallazgos, oportunidades y acciones prioritarias relevantes."
    ),
    "annex6.epip.p3": (
        "Cuando corresponda, los resultados se revisarán con el Cliente y se integrarán en el plan "
        "de acción Guardian en curso."
    ),
    "annex6.epip.quantity": "Número de auditorías EPIP",
    "annex6.epip.lines": "Líneas cubiertas",
    "annex6.epip.p4": (
        "Las acciones correctivas, reparaciones, mejoras o piezas derivadas de la auditoría no "
        "están incluidos salvo que se establezca expresamente."
    ),
    "annex6.followup.title": "5. Seguimiento",
    "annex6.followup.p1": (
        "Cuando esté incluido en el paquete seleccionado, Weber podrá realizar reuniones o "
        "llamadas de seguimiento antes y después de las actividades seleccionadas para revisar:"
    ),
    "annex6.followup.items": [
        "los objetivos acordados;",
        "las actividades realizadas;",
        "el impacto observado;",
        "las acciones pendientes;",
        "las prioridades técnicas; y",
        "las acciones siguientes.",
    ],

    # Annex 7 - Digital Services
    "annex7.title": "ANEXO 7 - SERVICIOS DIGITALES",
    "annex7.tagline": "Factory Cockpit, revisión de rendimiento, revisión MRO y gestión dedicada de cuenta.",
    "annex7.intro": (
        "El módulo de Servicios digitales ofrece servicios seleccionados de monitorización digital, "
        "revisión de rendimiento y gestión de cuenta."
    ),
    "annex7.cockpit.title": "1. Factory Cockpit",
    "annex7.cockpit.p1": (
        "Cuando el Equipamiento seleccionado sea técnicamente compatible, Weber facilitará la "
        "conexión del Equipamiento acordado a Factory Cockpit de conformidad con las condiciones "
        "del servicio digital aplicable."
    ),
    "annex7.cockpit.lines": "Línea(s) conectada(s)",
    "annex7.cockpit.p2": (
        "Factory Cockpit podrá utilizarse para recopilar y visualizar los datos de rendimiento "
        "disponibles de las máquinas con el fin de la revisión y la optimización del rendimiento."
    ),
    "annex7.cockpit.p3": (
        "El Cliente facilitará la infraestructura de red, los permisos y el acceso técnico "
        "razonablemente requeridos para la conexión."
    ),
    "annex7.cockpit.p4": (
        "La disponibilidad de datos específicos depende de la generación de la máquina, el "
        "software instalado y la conectividad del Equipamiento correspondiente."
    ),
    "annex7.cockpit.p5": (
        "Cualquier licencia de software por separado o condiciones del servicio digital aplicables "
        "a Factory Cockpit seguirán siendo aplicables."
    ),
    "annex7.performance.title": "2. Revisión de rendimiento",
    "annex7.performance.p1": "Weber y el Cliente realizarán revisiones periódicas de los datos de rendimiento disponibles del Equipamiento.",
    "annex7.performance.frequency": "Frecuencia de revisión",
    "annex7.performance.p2": "La revisión podrá incluir:",
    "annex7.performance.includes": [
        "los KPI seleccionados de la máquina;",
        "tendencias de rendimiento;",
        "observaciones técnicas recurrentes;",
        "oportunidades de mejora identificadas;",
        "actividades realizadas;",
        "acciones pendientes; y",
        "prioridades del siguiente periodo de revisión.",
    ],
    "annex7.performance.p3": "Las Partes podrán acordar KPI y valores objetivo específicos del Cliente.",
    "annex7.performance.p4": (
        "Salvo acuerdo expreso en contrario, dichos valores objetivo son objetivos de gestión y no "
        "garantías contractuales de rendimiento."
    ),
    "annex7.mro.title": "3. Revisión MRO",
    "annex7.mro.p1": (
        "Weber revisará periódicamente la información disponible sobre el gasto de Mantenimiento, "
        "Reparación y Operaciones (MRO) del Equipamiento cubierto."
    ),
    "annex7.mro.p2": "La revisión podrá incluir:",
    "annex7.mro.includes": [
        "el gasto en repuestos;",
        "el gasto en servicio;",
        "el gasto en cuchillas cuando sea relevante;",
        "el histórico de actividad de mantenimiento;",
        "la información de la base instalada;",
        "tendencias de mantenimiento;",
        "los impulsores de coste identificados; y",
        "la comparación con un objetivo de planificación MRO acordado.",
    ],
    "annex7.mro.frequency": "Frecuencia de revisión MRO",
    "annex7.mro.target": "Objetivo MRO acordado, si aplica",
    "annex7.mro.p3": (
        "El propósito de la revisión es respaldar la planificación del mantenimiento e identificar "
        "oportunidades de mejora. No constituye una garantía de que se alcance un nivel "
        "determinado de gasto MRO."
    ),
    "annex7.account.title": "4. Equipo de cuenta dedicado",
    "annex7.account.p1": "Weber asignará una estructura de gestión de cuenta Guardian para el Cliente.",
    "annex7.account.p2": (
        "El equipo coordinará las actividades Guardian seleccionadas y actuará como punto central "
        "para la revisión periódica del programa."
    ),
    "annex7.account.p3": "El proceso de gestión de cuenta podrá incluir:",
    "annex7.account.includes": [
        "revisiones periódicas del Cliente;",
        "la coordinación entre las funciones relevantes de Weber;",
        "la revisión de acciones abiertas;",
        "la revisión de las próximas actividades de servicio;",
        "la revisión de las necesidades de repuestos y cuchillas;",
        "discusiones de rendimiento;",
        "oportunidades de optimización; y",
        "el seguimiento de las acciones acordadas.",
    ],
    "annex7.account.cadence": "Cadencia de revisión",
    "annex7.account.p4": (
        "El equipo de cuenta dedicado complementa, pero no sustituye, los canales operativos "
        "normales de Weber para solicitudes urgentes de servicio, pedidos de repuestos o asistencia "
        "de emergencia."
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
