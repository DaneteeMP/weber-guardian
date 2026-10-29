"""Brazilian Portuguese overrides for the Guardian agreement content (full catalog).

Responsibility: translate every translatable node id to Brazilian Portuguese
(pt-BR). Any node id missing here falls back to the English source text, so a
parity test (test_content.py) requires this catalog to cover all translatable
ids. Overrides are strings for text nodes and lists of strings for list nodes
(ul, ol, dl, lines), mirroring the English source shape. Pure-token nodes
(address lines, special-conditions slot) are intentionally not translated:
{{Token}} placeholders must survive verbatim. Ids must exist in the English
section modules; the test suite rejects unknown ids and wrong override shapes.
"""

from __future__ import annotations

MESSAGES: dict[str, str | list[str]] = {
    # Module labels (labels.MODULE_LABELS)
    "module.maintenance_inspection": "Manutenção e inspeção",
    "module.service_support": "Suporte de serviço",
    "module.parts_availability": "Peças e disponibilidade",
    "module.blade_solutions": "Soluções de lâminas",
    "module.training_optimization": "Treinamento e otimização",
    "module.digital_services": "Serviços digitais",

    # Guardian contract types (labels.GUARDIAN_TYPE_LABELS)
    "guardian_type.audit": "Inspeção",
    "guardian_type.off_guardian": "Off-Guardian",
    "guardian_type.guardian": "Basic Kit",

    # Cover
    "cover.title": "CONTRATO DE MANUTENÇÃO",
    "cover.executor.label": "Entre a empresa:",
    "cover.executor.alias": "(doravante, o Executor)",
    "cover.customer.label": "E a empresa:",
    "cover.customer.alias": "(doravante, o Cliente)",
    "cover.preamble": (
        "celebra-se o seguinte contrato de inspeção e manutenção "
        '(doravante, o "Contrato"):'
    ),

    # Commercial breakdown (legacy Annex 1)
    "breakdown.title": "ANEXO 1, Relação de máquinas e módulos",
    "breakdown.date": "Data",
    "breakdown.offer_no": "N.º da oferta",
    "breakdown.frequency": "Frequência de Inspeção",
    "breakdown.type": "Tipo",
    "breakdown.col.line": "N.º DA LINHA",
    "breakdown.col.module": "MÓDULO",
    "breakdown.col.amount": "VALOR",
    "breakdown.total": "Total",
    "breakdown.kit": "Kit básico de peças de reposição",
    "breakdown.discount": "Desconto do contrato de manutenção",
    "breakdown.grand_total": "Valor total (sem IVA)",
    "breakdown.intro": (
        "Ambas as partes acordam o seguinte orçamento de inspeção da Weber nas "
        "condições abaixo estabelecidas:"
    ),
    "breakdown.notes": [
        "inclui deslocamento, mão de obra e documentação.",
        "verificação de sensores, componentes elétricos, transmissões, correias "
        "dentadas e lâminas (o kit básico inclui a substituição das correias "
        "principais da cabeça, do fuso e dos módulos auxiliares).",
        "ajuste das peças mecânicas dos diferentes módulos.",
        "revisão e otimização dos programas.",
        "registro de todas as reparações previstas.",
    ],
    "breakdown.notes_title": "NOTAS:",
    "breakdown.discount_notes": [
        "Desconto de 15% na assistência técnica das linhas contratadas.",
        "Desconto de 5% nas peças de reposição das linhas contratadas (não aplicável "
        "a descontos vigentes).",
        "Desconto de 5% nas lâminas para caixas completas de 3 lâminas (não aplicável "
        "a descontos vigentes).",
        "Inclui uma visita de acompanhamento gratuita após 6 meses.",
        "Todas as peças, consumíveis e peças de reposição fora do orçamento, bem como "
        "as horas fora do horário normal de trabalho, o tempo de espera e as reparações "
        "fora do orçamento, são faturados separadamente.",
    ],

    # Master Agreement (legacy 0 + I-IX)
    # 0. Definitions
    "master.clause0.title": "0. DEFINIÇÕES",
    "master.clause0.intro": "Os termos utilizados no presente contrato têm os seguintes significados:",
    "master.clause0.machine.term": "Máquina / Módulos",
    "master.clause0.machine.definition": (
        "Unidade funcional, item de equipamento ou sistema ao qual se referem os serviços prestados "
        "no âmbito do presente contrato."
    ),
    "master.clause0.inspection.term": "Inspeção",
    "master.clause0.inspection.definition": (
        "A determinação e a avaliação da condição real de uma máquina / módulo, incluindo a "
        "determinação das causas do desgaste e das consequências resultantes para a utilização futura."
    ),
    "master.clause0.maintenance.term": "Manutenção",
    "master.clause0.maintenance.definition": (
        'Medidas destinadas a retardar a deterioração dos elementos de desgaste existentes '
        '("manutenção preventiva"), em especial por meio de ajustes ou da substituição de filtros, '
        "vedações e lubrificantes, limpeza técnica, etc."
    ),
    "master.clause0.replacement.term": "Substituição",
    "master.clause0.replacement.definition": (
        "Qualquer medida destinada a restituir uma máquina / módulo à condição acordada, em especial "
        "mediante a substituição de peças, incluindo peças de desgaste. As medidas destinadas a "
        "manter a condição acordada fora dos serviços de manutenção também fazem parte da reparação."
    ),

    # I. Purpose of the contract
    "master.clause1.title": "I. OBJETIVO DO CONTRATO",
    "master.clause1.p1": (
        "(0) O objeto do contrato de inspeção é a inspeção das máquinas e dos módulos indicados no "
        "Anexo 1, sendo esses serviços faturados com base em um valor fixo (Anexo 1). A manutenção "
        "das máquinas e dos componentes será cobrada conforme a sua ocorrência e de acordo com as "
        "tarifas em vigor."
    ),
    "master.clause1.p2": (
        "O objeto do Contrato é prolongar a vida útil das máquinas e dos módulos, reduzir as paradas "
        "e manter os custos de manutenção sob controle por meio de inspeção e manutenção adequadas."
    ),
    "master.clause1.p3": (
        "(1) No âmbito do presente Contrato, o Executor assume os seguintes serviços para as máquinas "
        "e os módulos indicados:"
    ),
    "master.clause1.services": [
        "Serviço de linha de atendimento",
        "Fornecimento de peças de reposição",
        "Manutenção",
        "Visita de cortesia após a manutenção",
        "Programa de lâminas (manutenção de estoque)",
    ],
    "master.clause1.p4": "(2) O serviço do Executor compreende, nos seguintes casos:",
    "master.clause1.p5": "(2.1) Quando se recorre à linha de atendimento ou ao centro de serviço telefônico:",
    "master.clause1.hotline": [
        "Serviço de linha de atendimento de segunda a sexta-feira, das 07h30 às 17h30.",
        "Telefone: 938 23 32 33",
    ],
    "master.clause1.p6": (
        "(2.2) Distribuição de peças de reposição: fornecimento de peças de reposição disponíveis em "
        "estoque (na Península Ibérica e na Alemanha) no prazo de 24 a 48 horas. Caso a peça de "
        "reposição solicitada não esteja em estoque, será encomendada e entregue o mais breve possível."
    ),
    "master.clause1.p7": "(2.3) Inspeção: inspeção das máquinas de acordo com o Anexo 1.",
    "master.clause1.p8": "(2.4) Manutenção: realização de reparações de acordo com o ponto I.3 do Contrato.",
    "master.clause1.p9": (
        "(2.5) Programa de manutenção de estoque de lâminas: desconto de 5% a partir da primeira "
        "caixa de 3 unidades, de acordo com o Anexo 2."
    ),
    "master.clause1.p10": (
        "(3) Quaisquer trabalhos de manutenção ou outros serviços (por exemplo, alterações em "
        "máquinas e sistemas) decorrentes da inspeção exigirão uma ordem de compra separada e serão "
        "faturados mediante orçamento adicional."
    ),
    "master.clause1.p11": (
        "(4) O número de máquinas incluídas no Anexo 1, bem como o escopo dos serviços decorrentes do "
        "presente Contrato, será verificado pelas partes contratantes no último trimestre do Contrato."
    ),
    "master.clause1.p12": (
        "(5) As alterações no número de máquinas incluídas no acordo e as alterações no escopo do "
        "serviço efetuadas pelo Cliente serão registradas por escrito, com a correspondente alteração "
        "do Anexo 1. O presente acordo de serviço é válido pelos 12 meses do prazo do Contrato ou até "
        "o término do Contrato."
    ),
    "master.clause1.p13": (
        "(6) Visita de cortesia a ser realizada caso a manutenção subsequente seja executada pelo "
        "Executor."
    ),

    # II. Price and payment
    "master.clause2.title": "II. PREÇO E PAGAMENTO",
    "master.clause2.p1": (
        "(1) O preço dos trabalhos de inspeção é calculado de acordo com o Anexo 1. A relação decorre "
        "do modelo da máquina e dos módulos selecionados nos termos do ponto I do Contrato."
    ),
    "master.clause2.p2": (
        '(2) O preço dos módulos "Inspeção" e "Manutenção" inclui despesas de deslocamento, '
        "transporte, hospedagem e subsistência, salvo exceções acordadas com o Cliente."
    ),
    "master.clause2.p3": "(3) As peças substituídas serão apresentadas ao Cliente para o seu controle.",
    "master.clause2.p4": (
        "(4) O preço dos trabalhos do pessoal de inspeção será pago no prazo de 30 dias a contar da "
        "emissão da fatura. O faturamento ocorre após a realização da inspeção."
    ),
    "master.clause2.p5": (
        "(5) O Executor tem direito a revisar anualmente o preço dos trabalhos de acordo com o "
        "Anexo 1. O Executor notificará o Cliente dessa revisão com antecedência mínima de 3 meses "
        "antes da sua entrada em vigor. A alteração de preço aplicar-se-á no período de pagamento "
        "seguinte."
    ),
    "master.clause2.p6": (
        "(6) Não se admite a retenção de pagamentos nem a compensação com eventuais créditos "
        "alegados pelo Cliente."
    ),
    "master.clause2.p7": (
        "(7) O Executor concede um desconto de 15% nos serviços de assistência às máquinas e um "
        "desconto máximo de 5% nas peças de reposição, não cumulativos, conforme indicado no Anexo 1."
    ),

    # III. Client participation and technical contribution
    "master.clause3.title": "III. PARTICIPAÇÃO E CONTRIBUIÇÃO TÉCNICA DO CLIENTE",
    "master.clause3.p1": "(1) O Cliente garantirá que:",
    "master.clause3.obligations": [
        "Os trabalhos possam ser realizados pontualmente nos horários acordados e nas máquinas "
        "acordadas, devendo o Cliente garantir o livre acesso às máquinas e aos módulos.",
        "A máquina esteja em condições de funcionamento, disponível e limpa (sem resíduos de produto).",
        "Uma vez concluídos os trabalhos, possa ser realizada uma verificação funcional com os "
        "produtos originais do Cliente em quantidade suficiente.",
        "As falhas em curso estejam registradas nos desenhos da máquina.",
        "A produção esteja organizada de modo que possa ser interrompida durante a inspeção.",
    ],
    "master.clause3.p2": (
        "(2.a) O Cliente suportará os custos incorridos pelo pessoal de inspeção durante a inspeção "
        "e a manutenção."
    ),
    "master.clause3.p3": (
        "O Cliente adotará as medidas especiais necessárias à proteção pessoal e material no local "
        "de inspeção/manutenção. O Cliente informará também o pessoal da empresa executante sobre as "
        "medidas especiais de segurança, na medida em que estas sejam relevantes para o pessoal de "
        "inspeção e manutenção. O Cliente notificará o Executor de quaisquer infrações cometidas "
        "pelo pessoal que violem essas normas de segurança."
    ),
    "master.clause3.p4": (
        "(b) O Cliente compromete-se a suportar os custos da contribuição técnica, em especial a "
        "disponibilizar gratuitamente assistência, oficina e meios auxiliares, como água e "
        "eletricidade, incluindo as ligações necessárias."
    ),
    "master.clause3.p5": (
        "(c) A fim de decidir se os trabalhos podem ser realizados e/ou se as peças indicadas no "
        "ponto I.3 podem ser substituídas durante o intervalo de inspeção, o Cliente designará uma "
        "pessoa com autoridade para tomar decisões."
    ),

    # IV. Compliance with contract deadlines
    "master.clause4.title": "IV. CUMPRIMENTO DOS PRAZOS CONTRATUAIS",
    "master.clause4.p1": (
        "(1) O Executor compromete-se a realizar uma inspeção dentro do intervalo de tempo acordado "
        "no Anexo 1."
    ),
    "master.clause4.p2": (
        "(2) O Executor informará o Cliente da data exata da inspeção com antecedência mínima de 6 "
        "semanas, salvo se uma data específica tiver sido acordada entre as partes contratantes."
    ),
    "master.clause4.p3": "(3) O Executor prestará os serviços nos seguintes períodos:",
    "master.clause4.service_periods": [
        "Inspeção e manutenção de segunda a sexta-feira, das 08h00 às 18h00.",
        "Salvo acordo mútuo.",
    ],
    "master.clause4.p4": (
        "(4) Se o Cliente ou o Executor não puder realizar os trabalhos na data programada, ambas as "
        "partes deverão notificar-se mutuamente com antecedência mínima de 2 dias úteis. Se o "
        "Executor não comparecer na data acordada, o Executor não faturará os custos de deslocamento "
        "referentes à nova data; se a linha não estiver disponível na data acordada pelo Cliente, o "
        "Cliente pagará ao Executor os custos de deslocamento incorridos."
    ),
    "master.clause4.p5": (
        "(5) Se a inspeção/manutenção for atrasada por circunstâncias decorrentes de conflitos "
        "trabalhistas, em especial greves e paralisações, ou por eventos não imputáveis ao Executor, "
        "a inspeção/manutenção será prorrogada na medida adequada, desde que se comprove que tais "
        "impedimentos têm impacto significativo na conclusão da inspeção/manutenção. O mesmo se "
        "aplica quando tais circunstâncias ocorrerem depois de o Executor não ter cumprido o prazo de "
        "aviso previsto no parágrafo anterior."
    ),

    # V. Commencement and term
    "master.clause5.title": "V. INÍCIO E VIGÊNCIA DO CONTRATO",
    "master.clause5.p1": (
        "(1) O Contrato vigora a partir da assinatura de ambas as partes. O prazo do Contrato é de 12 "
        "meses e pode ser denunciado por qualquer das partes."
    ),
    "master.clause5.p2": (
        "(2) O Contrato será renovado automaticamente por mais 12 meses, salvo denúncia por escrito "
        "3 meses antes do seu término."
    ),

    # VI. Warranty and liability
    "master.clause6.title": "VI. GARANTIA E RESPONSABILIDADE",
    "master.clause6.p1": (
        "(1) Caso a inspeção/manutenção não tenha sido integralmente concluída, o Executor deverá "
        "revê-la ou corrigi-la sem qualquer custo."
    ),
    "master.clause6.p2": (
        "(2) O Executor reparará gratuitamente todos os danos causados por si ou pelos seus agentes "
        "às máquinas e instalações que deviam ser mantidas. O montante da obrigação de reparação está "
        "limitado ao valor anual estipulado no contrato."
    ),
    "master.clause6.p3": (
        "(3) Se o Executor não cumprir o seu dever de reparação, correção ou reparação de danos, o "
        "Cliente poderá fixar uma prorrogação adequada. Se, por culpa do Executor, esse prazo "
        "transcorrer sem resultado, o Cliente poderá, à sua escolha, exigir uma redução das taxas de "
        "manutenção e inspeção ou rescindir imediatamente o Contrato. O Executor e o Cliente acordam "
        "expressamente que o Executor só será responsável por danos quando se comprove dolo ou culpa "
        "grave da sua parte ou dos seus agentes. Em especial, as partes excluem expressamente a "
        "responsabilidade por danos ou prejuízos indiretos."
    ),
    "master.clause6.p4": (
        "(4) Qualquer outro direito de reclamação do Cliente aplicar-se-á apenas em caso de dolo ou "
        "culpa grave. Além disso, o Cliente não poderá opor ao Executor qualquer outro direito de "
        "compensação, em especial nenhum direito a indenização por danos ou outros direitos "
        "relativos a quaisquer transtornos relacionados com o Contrato de inspeção, "
        "independentemente dos motivos."
    ),
    "master.clause6.p5": (
        "(5) O Executor não será responsável por quaisquer danos ou defeitos causados por peças não "
        "originais."
    ),

    # VII. Limitation period
    "master.clause7.title": "VII. PRAZO DE PRESCRIÇÃO",
    "master.clause7.p1": (
        "Os direitos de garantia do Cliente prescreverão doze meses após a aceitação do "
        "correspondente serviço de inspeção/manutenção. O prazo de garantia será prorrogado pela "
        "duração dos trabalhos de correção."
    ),

    # VIII. Other provisions
    "master.clause8.title": "VIII. OUTRAS DISPOSIÇÕES",
    "master.clause8.p1": (
        "(1) Será concedido ao pessoal de inspeção/manutenção acesso às máquinas e instalações "
        "durante o horário normal de trabalho/horário de serviço, para que possa realizar os "
        "trabalhos de inspeção e manutenção anunciados. O Cliente fornecerá todas as informações "
        "necessárias sobre as máquinas e os módulos indicados no Anexo 1 e disponibilizará a "
        "documentação correspondente."
    ),
    "master.clause8.p2": (
        "(2) Se o Cliente transferir máquinas e instalações a terceiros, continuará responsável pelo "
        "pagamento das taxas, salvo se o terceiro aderir ao contrato com a autorização prévia do "
        "Executor. O Executor só poderá recusar o consentimento por motivos justificados."
    ),
    "master.clause8.p3": (
        "(3) O Executor tem direito de transferir a terceiros os direitos e deveres assumidos no "
        "âmbito do presente contrato."
    ),
    "master.clause8.p4": "(4) Os acordos adicionais e as alterações ao contrato devem ser formalizados por escrito.",
    "master.clause8.p5": (
        "(5) Se qualquer disposição do presente contrato se tornar inválida, todas as demais "
        "disposições ou acordos permanecerão válidos."
    ),

    # IX. Place of jurisdiction
    "master.clause9.title": "IX. FORO COMPETENTE",
    "master.clause9.p1": (
        "Na medida permitida por lei, o local de cumprimento e o foro competente serão a sede do "
        "Executor. Aplicar-se-á exclusivamente a legislação de Espanha."
    ),

    # Annex 1 - Equipment & Commercial Schedule
    "annex1.title": "ANEXO 1 - EQUIPAMENTO E CONDIÇÕES COMERCIAIS",
    "annex1.info.title": "1. Informações do contrato",
    "annex1.info.customer": "Cliente",
    "annex1.info.customer_no": "N.º do cliente",
    "annex1.info.site": "Unidade",
    "annex1.info.agreement_no": "N.º do acordo",
    "annex1.info.start_date": "Data de início do contrato",
    "annex1.info.term": "Prazo inicial",
    "annex1.info.billing": "Frequência de faturamento",
    "annex1.info.currency": "Moeda",
    "annex1.equipment.title": "2. Equipamento abrangido",
    "annex1.equipment.intro": "Somente o Equipamento e os módulos de máquina listados a seguir são abrangidos pelos Serviços Guardian.",
    "annex1.equipment.h_line": "Linha de produção",
    "annex1.equipment.h_machine": "Máquina",
    "annex1.equipment.h_serial": "N.º de série",
    "annex1.equipment.h_type": "Tipo",
    "annex1.equipment.h_modules": "Módulos / componentes incluídos",
    "annex1.equipment.h_frequency": "Frequência de serviço",
    "annex1.modules.title": "3. Módulos Guardian selecionados",
    "annex1.modules.intro": "Os seguintes módulos Guardian fazem parte deste Acuerdo:",
    "annex1.modules.outro": (
        "Somente os Anexos correspondentes aos módulos selecionados acima são anexados e passam a "
        "fazer parte do Acuerdo."
    ),
    "annex1.summary.title": "4. Resumo comercial",
    "annex1.summary.h_item": "Item comercial",
    "annex1.summary.h_amount": "Valor",
    "annex1.summary.travel": "Deslocamento / despesas",
    "annex1.summary.kit": "Peças de reposição / kit de manutenção",
    "annex1.summary.discount": "Desconto Guardian",
    "annex1.summary.total": "VALOR TOTAL DO CONTRATO",
    "annex1.summary.vat_note": "Todos os valores não incluem o IVA aplicável, salvo indicação em contrário.",
    "annex1.billing.title": "5. Faturamento",
    "annex1.billing.frequency": "Frequência de faturamento",
    "annex1.billing.terms": "Condições de pagamento",
    "annex1.billing.adjustment": "Ajuste de preço",
    "annex1.billing.travel": "Condições de deslocamento",
    "annex1.billing.freight": "Condições de frete",
    "annex1.special.title": "6. Condições comerciais especiais",

    # Annex 2 - Maintenance & Inspection
    "annex2.title": "ANEXO 2 - MANUTENÇÃO E INSPEÇÃO",
    "annex2.tagline": "Inspeção, manutenção preventiva e serviços de condição da máquina.",
    "annex2.purpose.title": "1. Objetivo",
    "annex2.purpose.p1": (
        "O módulo Manutenção e Inspeção destina-se a avaliar e manter a condição do Equipamento "
        "identificado no Anexo 1, identificar as ações técnicas necessárias e apoiar a operação "
        "confiável e o planejamento da manutenção."
    ),
    "annex2.purpose.p2": "As atividades exatas incluídas dependem das opções selecionadas na configuração Guardian.",
    "annex2.inspection.title": "S301 Inspeção Técnica Programada",
    "annex2.inspection.p1": (
        "Uma inspeção avalia a condição do equipamento selecionado no intervalo acordado, "
        "utilizando o checklist aplicável baseado na linha/módulo. O escopo técnico deve ser "
        "adaptado ao tipo e à configuração do equipamento."
    ),
    "annex2.inspection.p2": (
        "Antes da inspeção, a Weber e o Cliente revisarão os problemas operacionais conhecidos, o "
        "histórico do equipamento e a disponibilidade de produção planejada. Após a inspeção, os "
        "achados serão discutidos com o representante designado do Cliente e registrados em um "
        "relatório de inspeção."
    ),
    "annex2.checklist.title": "Checklist da Máquina",
    "annex2.checklist.p1": (
        "Para linhas de fatiamento, o checklist padrão pode incluir o seguinte, quando técnica e "
        "seguramente aplicável e acessível com segurança:"
    ),
    "annex2.checklist.items": [
        "teste de funcionamento com produto original, quando disponível; observações sobre a "
        "condição do equipamento e aspectos relacionados à segurança;",
        "sensores, eletrônica, ajustes da máquina, funções elétricas e pneumáticas; acionamentos, "
        "correias dentadas e trens de acionamento selecionados;",
        "ajustes mecânicos, carcaças e vedações, transportadores e elementos móveis; módulos de "
        "linha e componentes auxiliares da Weber;",
        "identificação de desgaste, reparos pendentes, anomalias da máquina e recomendações para "
        "ações futuras;",
        "acesso às carcaças da balança ou do cabeçote de corte somente conforme expressamente "
        "acordado e autorizado com segurança;",
        "preparação de um checklist de inspeção baseado em módulos, relatório e orçamento opcional "
        "de peças de acompanhamento.",
    ],
    "annex2.checklist.p2": (
        "Para máquinas de embalagem Weber, o checklist de inspeção também pode incluir verificações "
        "de condição específicas de embalagem definidas. Etiquetadoras de terceiros, bombas e "
        "dispositivos de fim de linha estão excluídos, salvo se expressamente listados."
    ),
    "annex2.report.title": "S305 Visita de Acompanhamento e Relatório",
    "annex2.report.p1": (
        "Quando acordado, a Weber realizará um acompanhamento definido após uma inspeção ou evento "
        "de manutenção, que poderá ser presencial ou remoto, dependendo do serviço acordado."
    ),
    "annex2.report.p2": (
        "Uma visita de acompanhamento não está automaticamente incluída em uma inspeção e pode "
        "estar condicionada à realização pela Weber de trabalhos de manutenção especificados, "
        "conforme indicado na programação do Cliente."
    ),
    "annex2.preventive.title": "S303 Manutenção Preventiva",
    "annex2.preventive.p1": (
        "A manutenção preventiva consiste em ajustes planejados, lubrificação, limpeza de "
        "componentes técnicos definidos e substituição de peças de desgaste especificadas, de "
        "acordo com a lista de atividades acordada e as restrições do equipamento."
    ),
    "annex2.preventive.p2": (
        "O escopo das peças fornecidas, das peças instaladas, da margem de mão de obra, da "
        "frequência e da parada necessária deve ser especificado por máquina no Anexo 1."
    ),
    "annex2.preventive.p3": (
        "A manutenção preventiva é distinta de um reparo corretivo; os serviços fora da lista de "
        "tarefas planejadas são autorizados e faturados separadamente, salvo se expressamente "
        "incluídos."
    ),
    "annex2.kit.title": "S402 Kit Básico de Peças de Reposição - Somente Fornecimento",
    "annex2.kit.p1": (
        "O Kit Básico de Peças de Reposição consiste nos artigos e quantidades exatos listados no "
        "Cronograma do Kit assinado. Ele apoia a substituição planejada ou o estoque mantido pelo "
        "Cliente, mas não constitui um direito ilimitado a consumíveis."
    ),
    "annex2.kit.p2": (
        "A Weber fornece os itens listados nas condições de pedido, entrega e preço especificadas. "
        "A instalação não está incluída em um kit somente de fornecimento."
    ),
    "annex2.repairs.title": "S304 Manutenção Corretiva / Reparo",
    "annex2.repairs.p1": (
        "O trabalho de reparo segue uma falha, defeito ou avaria identificada e busca restaurar uma "
        "condição acordada, sujeito ao acesso, à viabilidade técnica e à disponibilidade de peças."
    ),
    "annex2.repairs.p2": (
        "Salvo se uma alocação de reparo for expressamente precificada e selecionada, a mão de obra "
        "corretiva, as peças de reposição, o deslocamento e outros custos são orçados ou cobrados de "
        "acordo com as taxas de serviço selecionadas e a autorização do Cliente."
    ),
    "annex2.repairs.p3": (
        "Um atendimento, diagnóstico de falha ou tarefa de reparo não deve ser representado como "
        "restauração garantida da produção dentro de um período específico, salvo se expressamente "
        "acordado por escrito."
    ),
    "annex2.frequency.title": "Frequência de Inspeção",
    "annex2.frequency.value": "Frequência",
    "annex2.frequency.p1": "A programação efetiva deve ser coordenada entre a Weber e o Cliente.",

    # Annex 3 - Service Support
    "annex3.title": "ANEXO 3 - SUPORTE DE SERVIÇO",
    "annex3.tagline": "Atendimento ao cliente e suporte técnico.",
    "annex3.purpose.title": "1. Objetivo",
    "annex3.purpose.p1": (
        "O módulo Suporte de Serviço proporciona ao Cliente acesso ao suporte técnico da Weber para "
        "o Equipamento abrangido por este Contrato."
    ),
    "annex3.purpose.p2": "O nível exato de serviço depende das opções selecionadas abaixo.",
    "annex3.rates.title": "2. Taxas de Serviço",
    "annex3.rates.hours": "Horário",
    "annex3.rates.weekdays": "Segunda - Sexta",
    "annex3.rates.saturday": "Sábado",
    "annex3.rates.sunday": "Domingo / feriado",
    "annex3.rates.band": "Banda",
    "annex3.rates.without": "Sem contrato",
    "annex3.rates.with": "Com contrato",
    "annex3.hotline.title": "S101 Linha Direta Padrão",
    "annex3.hotline.p1": (
        "A Weber disponibilizará acesso ao canal de contato técnico padrão selecionado durante a "
        "janela de disponibilidade acordada. Trata-se de um serviço de comunicação; não está "
        "implícito qualquer tempo de resposta no local."
    ),
    "annex3.hotline.phone": "Ponto de contato",
    "annex3.hotline.email": "E-mail",
    "annex3.hotline.hours": "Segunda - Sexta",
    "annex3.hotline.p2": (
        "A disponibilidade para recebimento de chamadas não constitui, por si só, garantia de "
        "resolução diagnóstica, comparecimento no local ou envio de peças de reposição."
    ),
    "annex3.remote.title": "S103 Suporte Técnico Remoto",
    "annex3.remote.p1": (
        "A Weber poderá realizar a análise inicial de falhas por telefone, e-mail, conexão remota "
        "suportada ou comunicação por vídeo, mediante acordo quanto ao acesso seguro e à "
        "assistência do Cliente."
    ),
    "annex3.remote.p2": (
        "As condições de conexão, rede e segurança cibernética deverão ser acordadas antes da "
        "ativação. O suporte remoto não substitui um serviço no local que seja necessário."
    ),
    "annex3.priority.title": "S104 Serviço no Local e Resposta Prioritária",
    "annex3.priority.p1": (
        "A assistência técnica no local está disponível no território acordado, sujeita à "
        "disponibilidade de técnicos e às condições aplicáveis de despacho e agendamento. Qualquer "
        "classificação de prioridade deverá ser expressamente acordada."
    ),
    "annex3.priority.p2": (
        "As taxas de atendimento, mão de obra, deslocamento, tempo de espera, horas extras, "
        "hospedagem e materiais são calculadas conforme a tabela de preços aprovada."
    ),

    # Annex 4 - Parts & Availability
    "annex4.title": "ANEXO 4 - PEÇAS E DISPONIBILIDADE",
    "annex4.tagline": "Condições comerciais de peças de reposição, tratamento prioritário e estoque recomendado.",
    "annex4.purpose.title": "1. Objetivo",
    "annex4.purpose.p1": (
        "O módulo Peças e Disponibilidade apoia o planejamento estruturado de peças de reposição e "
        "o acesso às peças de reposição originais da Weber para o Equipamento abrangido por este "
        "Acordo."
    ),
    "annex4.discount.title": "S201 Condições Comerciais de Peças de Reposição",
    "annex4.discount.p1": (
        "As categorias selecionadas de peças de reposição são fornecidas aos preços e descontos "
        "acordados, com exclusões e tratamento de peças de troca, lâminas, pedidos especiais e "
        "equipamentos atualizados expressamente indicados."
    ),
    "annex4.discount.p2": "Os descontos não são acumulativos, salvo acordo expresso.",
    "annex4.handling.title": "S203 Tratamento Prioritário de Peças",
    "annex4.handling.p1": (
        "Sujeitos à disponibilidade e ao prazo acordado para a colocação de pedidos, os pedidos "
        "elegíveis poderão receber processamento ou despacho prioritários, conforme o arranjo local."
    ),
    "annex4.parts_list.title": "S202 Lista de Peças de Reposição Recomendadas",
    "annex4.parts_list.p1": (
        "A Weber poderá preparar uma lista de peças de reposição recomendadas específica para a "
        "máquina, distinguindo peças de desgaste programado de peças de reposição de alto risco "
        "recomendadas para estoque do Cliente. As listas deverão ser revisadas de acordo com a "
        "idade, a especificação e a capacidade de suporte do equipamento."
    ),
    "annex4.parts_list.p2": (
        "Quando a filial local aplicar a classificação de estilo Benelux, A/B designam peças de "
        "desgaste/críticas recomendadas e C/D/E poderão identificar estoque local, outro estoque da "
        "Weber ou fabricação sob encomenda; uma determinada peça pode possuir tanto uma "
        "recomendação quanto um status de disponibilidade."
    ),
    "annex4.parts_list.categories": [
        "A - Peças de desgaste recomendadas.",
        "B - Peças de reposição críticas / de maior risco de falha propostas para estoque no local.",
        "C - Disponíveis no estoque local da Weber (sujeito a confirmação).",
        "D - Disponíveis em outra localidade da Weber (sujeito a confirmação).",
        "E - Fabricadas sob encomenda / sem estoque atual.",
    ],
    "annex4.parts_list.p3": (
        "A lista é meramente indicativa, não constituindo garantia de disponibilidade de estoque, "
        "de adequação a todas as configurações ou de compromisso de fornecimento automático das "
        "quantidades recomendadas."
    ),
    "annex4.parts_list.p4": (
        "A Weber fornece uma lista de peças específica para a máquina, de caráter indicativo, sem "
        "fornecimento de material ou instalação, salvo pedido em separado."
    ),

    # Annex 5 - Blade Solutions
    "annex5.title": "ANEXO 5 - SOLUÇÕES DE LÂMINAS",
    "annex5.tagline": "Consultoria de aplicação de lâminas, afiação e o programa de lâminas.",
    "annex5.intro": (
        "O módulo Soluções de Lâminas apoia a seleção, a disponibilidade, o uso e a gestão corretos "
        "das lâminas da Weber, incluindo o princípio \"lâmina certa, aplicação correta\"."
    ),
    "annex5.discount.title": "S603 Parceria de Fornecimento de Lâminas",
    "annex5.discount.p1": (
        "Caso o Cliente selecione a opção Parceria de Lâminas, as partes acordam, no Anexo do "
        "Programa de Lâminas, um catálogo definido de referências de lâminas, quantidades, preços, "
        "cronograma de pedidos e prazo comercial."
    ),
    "annex5.discount.p2": (
        "Qualquer orçamento mensal fixo ou plano de parcelamento, previsão de consumo, compromisso "
        "mínimo, prazo de fixação de preços, bonificação, pedido de liberação, programa de devolução "
        "ou condição especial de entrega aplica-se somente se especificado no referido anexo."
    ),
    "annex5.stock.title": "Acordo de Estoque de Lâminas",
    "annex5.stock.p1": (
        "Quando for selecionado um acordo de estoque de lâminas, as partes definem, no anexo "
        "assinado, as referências, as quantidades, o método de reposição, a localização e a "
        "propriedade do estoque."
    ),
    "annex5.stock.p2": (
        "As quantidades compradas ou entregues devem ser contabilizadas de forma distinta do uso "
        "estimado ou do estoque interno de lâminas."
    ),
    "annex5.sharpening.title": "S602 Avaliação de Afiação",
    "annex5.sharpening.p1": (
        "A Weber avalia a abordagem de afiação atual do Cliente, seus processos, os parâmetros das "
        "máquinas e eventuais melhorias de controle de qualidade ou de manuseio, dentro do escopo "
        "acordado."
    ),
    "annex5.application.title": "S601 Consultoria de Aplicação de Lâminas",
    "annex5.application.p1": (
        "A Weber analisa, juntamente com o Cliente, a aplicação de corte selecionada, as "
        "características do produto, a configuração de corte e a geometria ou especificação "
        "relevante da lâmina."
    ),
    "annex5.application.p2": (
        "Entregável: um conjunto documentado de recomendações técnicas para uma combinação adequada "
        "de lâmina e aplicação, sujeito a verificação na aplicação real."
    ),

    # Annex 6 - Training & Optimization
    "annex6.title": "ANEXO 6 - TREINAMENTO E OTIMIZAÇÃO",
    "annex6.tagline": (
        "Treinamento de operadores e de técnicos de manutenção, otimização de linha e auditorias EPIP."
    ),
    "annex6.intro": (
        "O módulo Treinamento e Otimização oferece atividades selecionadas destinadas a melhorar a "
        "operação das máquinas, a capacidade de manutenção e o desempenho da produção."
    ),
    "annex6.operator.title": "S501 Treinamento de Operadores",
    "annex6.operator.p1": (
        "Treinamento para operadores sobre o uso seguro e eficiente do Equipamento definido, "
        "incluindo procedimentos operacionais selecionados, ajustes, práticas de limpeza e "
        "verificações operacionais básicas, na medida adequada."
    ),
    "annex6.maintenance.title": "S502 Treinamento de Técnicos de Manutenção",
    "annex6.maintenance.p1": (
        "Treinamento para a equipe de manutenção do Cliente sobre a arquitetura da máquina, "
        "verificações preventivas, reconhecimento de falhas, solução segura de problemas e "
        "procedimentos de manutenção, dentro das permissões de acesso acordadas."
    ),
    "annex6.optimization.title": "S702 Otimização de Linha",
    "annex6.optimization.p1": (
        "A Weber analisa as restrições técnicas e de produção identificadas e pode recomendar ou "
        "executar melhorias acordadas de ajuste da máquina ou de processo, dentro do escopo aceito."
    ),
    "annex6.optimization.p2": "Quaisquer atualizações de capital ou itens de reparo permanecem separados.",
    "annex6.epip.title": "S701 Auditoria EPIP / Equipamentos",
    "annex6.epip.p1": (
        "A Weber realiza a avaliação aprofundada do equipamento ou auditoria no estilo EPIP "
        "selecionada nas linhas de produção especificadas e fornece um relatório de avaliação."
    ),
    "annex6.epip.p2": (
        "O relatório deve distinguir a condição observada, as ações prioritárias, os reparos "
        "recomendados e as oportunidades de melhoria."
    ),

    # Annex 7 - Digital Services
    "annex7.title": "ANEXO 7 - SERVIÇOS DIGITAIS",
    "annex7.tagline": (
        "Factory Cockpit, revisões de desempenho, revisões MRO e gestão de contas dedicada."
    ),
    "annex7.intro": (
        "O módulo Serviços Digitais oferece serviços selecionados de monitoramento digital, revisão "
        "de desempenho e gestão de contas."
    ),
    "annex7.cockpit.title": "S801 Factory Cockpit / Monitoramento",
    "annex7.cockpit.p1": (
        "Quando disponível e selecionada, a Weber fornece a conexão ou o acesso acordado à "
        "funcionalidade designada do Factory Cockpit ou de monitoramento digital suportada para "
        "Equipamentos elegíveis."
    ),
    "annex7.cockpit.p2": (
        "A arquitetura de conexão, a disponibilidade do serviço, a retenção, os direitos de acesso "
        "e as responsabilidades de cibersegurança serão definidos nos termos do serviço digital."
    ),
    "annex7.performance.title": "S802 Revisão de Desempenho e Relatórios de Tendências",
    "annex7.performance.p1": (
        "A Weber poderá preparar ou revisar as informações acordadas de desempenho do Equipamento, "
        "as tendências operacionais e as áreas identificadas para acompanhamento, com base nos "
        "dados disponibilizados."
    ),
    "annex7.performance.p2": (
        "Os valores poderão ser afetados pela qualidade dos dados, pelas práticas operacionais, "
        "pelo mix de produtos e por sistemas de terceiros. Os relatórios têm caráter analítico e "
        "não constituem garantias de desempenho de produção."
    ),
    "annex7.mro.title": "S803 Revisão MRO de Serviço / Peças",
    "annex7.mro.p1": (
        "A Weber poderá revisar as despesas de serviço acordadas e o uso de peças de reposição em "
        "relação a uma referência MRO definida ou a uma meta de planejamento acordada."
    ),
    "annex7.mro.p2": (
        "As taxas fixas Guardian, as intervenções de manutenção efetivas e as peças de reposição "
        "consumidas permanecerão como elementos de dados separados; não haverá duplicação de custos "
        "nem inferência de falhas a partir dos totais das faturas."
    ),
    "annex7.account.title": "S105 Revisões de Conta Dedicada",
    "annex7.account.p1": (
        "Quando selecionado, um contato designado de conta ou de Pós-Vendas coordenará revisões "
        "periódicas da prestação acordada de serviços, das atividades concluídas, dos itens de ação "
        "em aberto e dos requisitos futuros."
    ),

    # Configuration Summary and Signatures
    "summary.title": "RESUMO DE CONFIGURAÇÃO GUARDIAN",
    "summary.intro": (
        "O resumo a seguir confirma a configuração Guardian adquirida pelo Cliente nos termos "
        "deste Acuerdo."
    ),
    "summary.customer": "Cliente",
    "summary.site": "Unidade",
    "summary.start": "Início do contrato",
    "summary.term": "Prazo do contrato",
    "summary.equipment": "Equipamento abrangido",
    "summary.equipment.value": "{{Number_Of_Machines}} máquinas / {{Number_Of_Lines}} linhas de produção",
    "summary.value": "Valor anual / do contrato",
    "summary.scope.title": "Seu Guardian",
    "summary.scope.h_module": "Módulo Guardian",
    "summary.scope.h_scope": "Escopo selecionado",
    "summary.signatures.title": "ASSINATURAS",
    "summary.signatures.intro": (
        "Ao assinar este Acuerdo, as Partes confirmam sua aceitação do Acordo-Mestre e de todos "
        "os Anexos identificados no Anexo 1 como aplicáveis."
    ),
    "summary.signatures.company": "Empresa",
    "summary.signatures.customer": "Pelo Cliente",
    "summary.signatures.weber": "Pela Weber",
    "summary.signatures.name": "Nome",
    "summary.signatures.position": "Cargo",
    "summary.signatures.place": "Local",
    "summary.signatures.date": "Data",
    "summary.signatures.signature": "Assinatura",
}
