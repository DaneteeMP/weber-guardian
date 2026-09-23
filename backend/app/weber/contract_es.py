"""Spanish Guardian maintenance-contract content (Weber legacy).

Ported from WeberAssistant generateOfferPdf (clauses + executor block).
Data only, no PDF code: the renderer in this package consumes it.
Executor blocks are keyed by subsidiary_id; subsidiaries without their
own block fall back to None so the caller fails explicitly instead of
printing another filial's address.
"""

EXECUTORS: dict[str, dict[str, str]] = {
    "ES": {
        "name": "WEBER FOOD TECHNOLOGY IBÉRICA, S.L.",
        "street": "c/ La Coma, 29",
        "city": "(08272) Sant Fruitós de Bages (Barcelona)",
        "country": "España",
        "place_date": "Sant Fruitós de Bages",
    },
}

TITLE = "CONTRATO DE MANTENIMIENTO"
EXECUTOR_LABEL = "Entre la empresa:"
EXECUTOR_ALIAS = "(en adelante, el Ejecutor)"
CLIENT_LABEL = "Y la empresa:"
CLIENT_ALIAS = "(en adelante, el Ordenante)"
PREAMBLE = 'se celebra el siguiente contrato de inspección y mantenimiento (en adelante, el "Contrato"):'
ANNEX_TITLE = "ANEXO 1, Relación de máquinas y módulos"

# (kind, text): kind is heading/subheading/text, indent in mm for text.
CLAUSES: list[tuple[str, str, int]] = [
    ("heading", "0. DEFINICIONES", 0),
    ("text", "Los términos utilizados en este acuerdo tienen los siguientes significados:", 0),
    ("subheading", "Máquina/ Módulos", 0),
    ("text", "Unidad funcional, equipo o sistema al que se refieren los servicios que se prestarán en virtud del presente contrato.", 0),
    ("subheading", "Inspección", 0),
    ("text", "La determinación y evaluación del estado real de una máquina / módulo, incluida la determinación de las causas del desgaste y la derivación de las consecuencias necesarias para el uso futuro.", 0),
    ("subheading", "Mantenimiento", 0),
    ("text", 'Las medidas para retrasar el desmantelamiento de las existencias de desgaste existentes ("mantenimiento preventivo"), en particular mediante ajustes o mediante la sustitución de filtros, sellos y lubricantes, limpieza técnica, etc.', 0),
    ("subheading", "Reposición", 0),
    ("text", "Cualquier medida para devolver una máquina / módulo a la condición acordada, en particular mediante la sustitución de piezas, incluidas las piezas de desgaste. Las medidas para mantener la condición acordada fuera de los servicios de mantenimiento también son parte de la reparación.", 0),
    ("heading", "I. OBJETO DEL CONTRATO", 0),
    ("text", "(0) El Contrato de inspección tiene por objeto la inspección de las máquinas y módulos enumerados en el (Anexo 1), facturación de estos servicios sobre la base de una tarifa fija (Anexo1). El mantenimiento de las máquinas y componentes, a computar según se incurra en el mismo y segun tarifas vigentes.", 0),
    ("text", "El objetivo del Contrato es extender la vida útil de las máquinas y los módulos, reducir los tiempos de inactividad y mantener los costos de mantenimiento bajo control mediante una inspección y un mantenimiento adecuados.", 0),
    ("text", "(1) En el marco de este Contrato, el Ejecutor asume los siguientes servicios para las máquinas y módulos enumerados:", 0),
    ("text", "- Servicio de atención telefónica", 15),
    ("text", "- Suministro de piezas de repuesto", 15),
    ("text", "- Mantenimiento", 15),
    ("text", "- Visita de cortesía posterior al mantenimiento", 15),
    ("text", "- Programa de Cuchillas (resguardo de stock)", 15),
    ("text", "(2) El servicio del Ejecutor comprende, en los casos", 0),
    ("text", "(2.1) En los que se acceda a la línea o centro de atención telefónica :", 0),
    ("text", "- El servicio de atención telefónica de lunes a viernes de 07:30 h a 17:30 h.", 15),
    ("text", "- Teléfono: 938 23 32 33", 15),
    ("text", "(2.2) La distribución de piezas de repuesto : El suministro de piezas de repuesto existentes (en stock) en almacén (en la Península Ibérica y Alemania) en un plazo de 24-48 horas. En el caso de no disponer de la pieza de repuesto solicitada en stock, se solicitará y se entregará con la mayor brevedad posible.", 0),
    ("text", "(2.3) La inspección : Inspección de las máquinas en conformidad con el ANEXO 1", 0),
    ("text", "(2.4) El mantenimiento: Ejecución de reparaciones de conformidad con el punto I.3 del Contrato.", 0),
    ("text", "(2.5) Programa de resguardo de stock de Cuchillas: descuento del 5% a partir de la 1ª caja de 3 unidades, en conformidad con el ANEXO 2.", 0),
    ("text", "(3) Cualquier trabajo de mantenimiento u otros servicios (por ejemplo, cambios en las máquinas y sistemas) que resulten de la inspección requerirán de una orden de compra separada; y se facturará en función de una oferta adicional.", 0),
    ("text", "(4) El número de las máquinas incluidas en el ANEXO 1, así como el alcance de los servicios derivados del presente Contrato se verificarán, por parte de las partes contratantes, en el último trimestre del Contrato", 0),
    ("text", "(5) Las modificaciones en referencia al número de máquinas incluidas en el acuerdo y las modificaciones del alcance del servicio por parte del Ordenante se harán constar por escrito, modificando el Anexo 1. Este acuerdo de servicios es válido por los 12 meses de validez de Contrato o hasta la finalización del Contrato", 0),
    ("text", "(6) Visita de cortesía a realizar si el mantenimiento posterior es realizado por el Ejecutor.", 0),
    ("heading", "II. PRECIO Y PAGO", 0),
    ("text", "(1) El precio del trabajo de inspección se calcula según el ANEXO 1. La relación se deduce del modelo de máquina y de los módulos seleccionados conforme al punto I del Contrato.", 0),
    ("text", '(2) El precio para los módulos "Inspección" y "Mantenimiento" incluye gastos de desplazamiento, transporte, alojamiento y dietas. Salvo excepciones acordadas con el Ordenante.', 0),
    ("text", "(3) Las piezas sustituidas se le presentarán al Ordenante para su control.", 0),
    ("text", "(4) El precio del trabajo del personal de inspección se abonará una vez emitida la factura, en el plazo de 30 días . La facturación tiene lugar después de haber realizado la inspección.", 0),
    ("text", "(5) El Ejecutor tiene derecho a revisar el precio del trabajo conforme a lo establecido en el Anexo 1 anualmente. Le notificará dicha revisión al Ordenante al menos 3 meses antes de la entrada en vigor. La modificación del precio se aplicará en el siguiente periodo de pago.", 0),
    ("text", "(6) No se acepta la retención de pagos ni la compensación por eventuales contraprestaciones alegadas por parte del Ordenante.", 0),
    ("text", "(7) El Ejecutor ofrece un descuento del 15 % para los servicios de asistencia de máquinas y un 5% de descuento máximo en recambios no acumulable como indica el ANEXO 1.", 0),
    ("heading", "III. PARTICIPACIÓN Y CONTRIBUCIÓN TÉCNICA DEL ORDENANTE", 0),
    ("text", "(1) El Ordenante velará por qué:", 0),
    ("text", "• Los trabajos puedan llevarse a cabo puntualmente a las horas y en las máquinas acordadas y garantizará el libre acceso a las máquinas y módulos.", 15),
    ("text", "• La máquina se encuentre en estado operativo, esté disponible y limpia (sin restos de producto).", 15),
    ("text", "• Una vez finalizados los trabajos, pueda llevarse a cabo una comprobación funcional con los productos originales del cliente en una cantidad suficiente.", 15),
    ("text", "• Se registren las averías en curso en los planos de máquinas.", 15),
    ("text", "(2.a) El Ordenante correrá con los gastos originados por el personal de inspección durante la ejecución de la inspección y del mantenimiento.", 0),
    ("text", "(b) El Ordenante se compromete a correr con los gastos de la contribución técnica, en particular, a ofrecer gratuitamente asistencia, taller, medios auxiliares como el agua y la electricidad, incluyendo las conexiones necesarias.", 0),
    ("heading", "IV. CUMPLIMIENTO DE LOS PLAZOS DEL CONTRATO", 0),
    ("text", "(1) El Ejecutor se compromete a efectuar una inspección en el marco del intervalo de tiempo acordado en el Anexo 1.", 0),
    ("text", "(2) El Ejecutor notifica al Ordenante la fecha exacta de la inspección con al menos con 6 semanas de antelación, en caso de que entre las partes del contrato no se haya acordado una determinada fecha.", 0),
    ("text", "(3) El Ejecutor prestará los servicios en los siguientes periodos:", 0),
    ("text", "- Inspección y mantenimiento de lunes a viernes de 08:00 h a 18:00 h.", 15),
    ("text", "- Salvo excepciones de mutuo acuerdo.", 15),
    ("text", "(4) En caso de que al Ordenante o al Ejecutor no le fuese posible llevar a cabo los trabajos en la fecha prevista, ambas partes se lo notificarán recíprocamente con al menos 2 días laborables de antelación.", 0),
    ("text", "(5) Si la inspección/mantenimiento se retrasa por circunstancias originadas por conflictos laborales, en particular, huelgas y paros, así como por hechos acaecidos no imputables al Ejecutor, tendrá lugar una adecuada prolongación de la inspección/mantenimiento.", 0),
    ("heading", "V. INICIO Y DURACIÓN DEL CONTRATO", 0),
    ("text", "(1) El Contrato adquiere validez desde la firma de ambas partes. La duración del Contrato es de 12 meses, y será revocable por ambas partes.", 0),
    ("text", "(2) El Contrato se prorrogará automáticamente por otros 12 meses, en el caso de que no se haya rescindido por escrito 3 meses anteriores a la finalización del mismo .", 0),
    ("heading", "VI. GARANTÍA Y RESPONSABILIDAD", 0),
    ("text", "(1) En caso de que la inspección /el mantenimiento no se haya completado en su totalidad, Ejecutor la revisará o rectificará sin coste alguno.", 0),
    ("text", "(2) El Ejecutor subsanará gratuitamente todos los daños que él o sus agentes hayan provocado en las máquinas e instalaciones a las que debía efectuarse el mantenimiento. La cuantía de la obligación de reparación se limita a la cuota anual estipulada por contrato.", 0),
    ("text", "(3) En el caso de que el Ejecutor incumpla su deber de reparación, mejora o reparación del daño, el Ordenante podrá establecer una prórroga adecuada. Si por la culpa del Ejecutor, este plazo transcurre sin obtnerse resultado, el Ordenante podrá, a su elección, exigir una reducción de las cuotas de mantenimiento e inspección o bien rescindir de inmediato el Contrato.", 0),
    ("text", "(4) Cualquier otro derecho a reclamación del Ordenante se aplicará únicamente en caso de dolo o negligencia grave.", 0),
    ("text", "(5) Cualquier daño o desperfecto causado por piezas no originales, el Ejecutor no se hará responsable.", 0),
    ("heading", "VII. PERÍODO DE PRESCRIPCIÓN", 0),
    ("text", "Los derechos de garantía del Ordenante pierden su validez a los doce meses, a contar desde la aceptación del correspondiente servicio de inspección/mantenimiento. El plazo de garantía se prolongará mientras duren los trabajos de subsanación.", 0),
    ("heading", "VIII. OTRAS DISPOSICIONES", 0),
    ("text", "(1) Al personal de inspección/mantenimiento se le facilitará el acceso a las máquinas e instalaciones durante las horas habituales de trabajo/tiempo de servicio con la finalidad de que pueda efectuar los trabajos de inspección y mantenimiento anunciados.", 0),
    ("text", "(2) Si el Ordenante cede máquinas e instalaciones a terceros, sigue permaneciendo obligado al pago de las cuotas, a menos que el tercero se adhiera al contrato, previa autorización del ejecutor.", 0),
    ("text", "(3) El Ejecutor tiene derecho a transferir a terceros los derechos y deberes contraídos con el presente contrato.", 0),
    ("text", "(4) Los acuerdos adicionales y las modificaciones del contrato deben efectuarse por escrito.", 0),
    ("text", "(5) En el caso de que una de las disposiciones del presente contrato deje de ser válida, todas las demás disposiciones o acuerdos seguirán manteniendo su validez.", 0),
    ("heading", "IX. LUGAR DE JURISDICCIÓN", 0),
    ("text", "En la medida en que lo permita la ley, el lugar de cumplimiento y jurisdicción será el domicilio social del Ejecutor. Se aplicará exclusivamente la legislación de España.", 0),
]

NOTES = [
    "- incluye desplazamientos, mano de obra y documentación.",
    "- comprobación de sensores, componentes eléctricos, transmisiones, correas dentadas y cuchillas",
    "  (en el kit básico se incluye la sustitución de las correas principales del cabezal, husillo y módulos",
    "  auxiliares).",
    "- ajuste de las piezas mecánicas de los diferentes módulos",
    "- revisión y optimización de programas.",
    "- registro de todas las reparaciones previstas.",
]

DISCOUNT_NOTES = [
    "- Descuento del 15% en la asistencia técnica de las líneas contratadas.",
    "- Descuento del 5% en los recambios de las líneas contratadas (no aplicable a descuentos vigentes).",
    "- Descuento del 5% en cuchillas para cajas completas 3 cuchillas, no aplicable a descuentos vigentes).",
    "- Incluye una visita gratuita de seguimiento a los 6 meses.",
    "- Todas las piezas, consumibles y recambios fuera de presupuesto, así como horas fuera de horario normal,",
    "  espera y reparación fuera de presupuesto, se facturarán aparte.",
]
