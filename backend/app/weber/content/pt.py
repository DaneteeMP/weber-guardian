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

    # Master Agreement
    "master.title": "ACORDO-MESTRE WEBER GUARDIAN",
    "master.kv.agreement_no": "N.º do acordo",
    "master.kv.offer_no": "N.º da oferta",
    "master.kv.offer_date": "Data da oferta",
    "master.kv.start_date": "Data de início do contrato",
    "master.kv.term": "Prazo inicial do contrato",
    "master.kv.billing": "Frequência de faturamento",
    "master.between": "ENTRE",
    "master.weber_definition": "doravante, \"Weber\".",
    "master.customer_definition": "doravante, o \"Cliente\".",
    "master.parties": "Weber e o Cliente são denominados individualmente \"Parte\" e coletivamente \"as Partes\".",

    # 1. PURPOSE OF THE AGREEMENT
    "master.clause1.title": "1. OBJETIVO DO ACORDO",
    "master.clause1.p1": (
        "O presente Acordo Weber Guardian tem por objetivo apoiar a operação confiável, eficiente e "
        "economicamente sustentável do equipamento Weber do Cliente durante todo o seu ciclo de vida."
    ),
    "master.clause1.p2": (
        "Guardian é um programa pós-venda modular. Dependendo dos módulos selecionados pelo Cliente, "
        "o Acordo pode incluir serviços de inspeção e manutenção preventiva, suporte técnico, "
        "serviços de peças de reposição, soluções de lâminas, serviços de treinamento e otimização "
        "e serviços digitais."
    ),
    "master.clause1.p3": "Somente os serviços expressamente identificados nos Anexos aplicáveis deste Acordo estão incluídos.",
    "master.clause1.goals_intro": "O objetivo do programa Guardian é:",
    "master.clause1.goals": [
        "melhorar a confiabilidade e a disponibilidade do equipamento;",
        "apoiar a manutenção preventiva e a identificação precoce de problemas técnicos;",
        "reduzir as paradas não planejadas evitáveis;",
        "apoiar um planejamento de manutenção e um gasto previsíveis;",
        "garantir o acesso à especialização técnica da Weber;",
        "otimizar a gestão de peças de reposição e lâminas;",
        "melhorar as práticas de operação e manutenção; e",
        "apoiar a otimização contínua do equipamento instalado do Cliente.",
    ],
    "master.clause1.exclusion": (
        "Nenhum serviço, desconto, compromisso de resposta ou outro benefício será considerado "
        "incluído, salvo quando expressamente previsto neste Acordo ou em um Anexo que faça parte dele."
    ),

    # 2. CONTRACT DOCUMENTS AND MODULAR STRUCTURE
    "master.clause2.title": "2. DOCUMENTOS CONTRATUAIS E ESTRUTURA MODULAR",
    "master.clause2.p1": (
        "Este Acuerdo é composto por este Acordo-Mestre e pelos Anexos abaixo listados que foram "
        "selecionados para o Cliente."
    ),
    "master.clause2.annexes": [
        "Anexo 1 - Equipamento e condições comerciais: sempre aplicável.",
        "Anexo 2 - Manutenção e inspeção: aplicável somente quando o módulo Manutenção e inspeção for selecionado.",
        "Anexo 3 - Suporte de serviço: aplicável somente quando o módulo Suporte de serviço for selecionado.",
        "Anexo 4 - Peças e disponibilidade: aplicável somente quando o módulo Peças e disponibilidade for selecionado.",
        "Anexo 5 - Soluções de lâminas: aplicável somente quando o módulo Soluções de lâminas for selecionado.",
        "Anexo 6 - Treinamento e otimização: aplicável somente quando o módulo Treinamento e otimização for selecionado.",
        "Anexo 7 - Serviços digitais: aplicável somente quando o módulo Serviços digitais for selecionado.",
    ],
    "master.clause2.p2": "Os Anexos aplicáveis fazem parte integrante deste Acordo.",
    "master.clause2.p3": (
        "Os serviços aplicam-se somente às máquinas, linhas de produção, módulos e locais "
        "identificados no Anexo 1, salvo acordo em contrário por escrito."
    ),
    "master.clause2.p4": (
        "Em caso de conflito entre os documentos que compõem este Acordo, aplicar-se-á a seguinte "
        "ordem de precedência:"
    ),
    "master.clause2.precedence": [
        "Anexo 1 - Equipamento e condições comerciais;",
        "o Anexo específico do serviço correspondente;",
        "este Acordo-Mestre; e",
        "os Termos e Condições Gerais aplicáveis da Weber.",
    ],
    "master.clause2.p5": (
        "Os desvios específicos do Cliente expressamente previstos no Anexo 1 prevalecerão sobre "
        "as disposições padrão relativas ao mesmo tema."
    ),

    # 3. DEFINITIONS
    "master.clause3.title": "3. DEFINIÇÕES",
    "master.clause3.definitions": [
        "Equipamento: as máquinas, módulos, sistemas ou outros equipamentos expressamente listados no Anexo 1.",
        "Inspeção: a avaliação da condição real do Equipamento com o objetivo de identificar desgastes, irregularidades, a manutenção necessária e as ações potenciais necessárias para sustentar a sua futura operação.",
        "Manutenção preventiva: medidas programadas destinadas a reduzir a deterioração e o risco de falha, incluindo ajuste, lubrificação, limpeza, substituição de peças de desgaste definidas e outras atividades expressamente incluídas no escopo de serviço aplicável.",
        "Manutenção corretiva / Reparo: trabalhos destinados a restaurar o Equipamento à condição operacional necessária após uma falha, avaria ou defeito identificado.",
        "Peças de desgaste: componentes que, pela sua função prevista e em função das condições de operação e do uso, exigem substituição periódica.",
        "Peças de reposição: componentes de substituição fornecidos para o Equipamento.",
        "Serviços: os serviços Guardian expressamente selecionados e descritos nos Anexos aplicáveis.",
        "Visita de serviço: uma visita física acordada de pessoal da Weber ou de um parceiro de serviço autorizado da Weber ao local do Cliente.",
        "Suporte remoto: assistência técnica prestada sem visita física, incluindo telefone, e-mail, comunicação digital e, quando disponível e autorizado, conexão remota ao Equipamento.",
        "Ano contratual: cada período consecutivo de doze meses iniciado na Data de início do contrato.",
    ],

    # 4. EQUIPMENT COVERED
    "master.clause4.title": "4. EQUIPAMENTO ABRANGIDO",
    "master.clause4.p1": "O Acordo Weber Guardian aplica-se exclusivamente ao Equipamento listado no Anexo 1.",
    "master.clause4.p2": "O Anexo 1 identificará, quando aplicável:",
    "master.clause4.identify": [
        "a linha de produção do Cliente;",
        "a referência da máquina Weber;",
        "o número de série;",
        "o tipo de equipamento;",
        "os módulos incluídos;",
        "a frequência de serviço;",
        "o tempo planejado de inspeção ou serviço;",
        "os módulos Guardian selecionados;",
        "o preço de serviço aplicável; e",
        "quaisquer condições comerciais específicas da máquina.",
    ],
    "master.clause4.p3": (
        "O Cliente notificará por escrito a Weber qualquer mudança de local, modificação material, "
        "alienação ou venda do Equipamento abrangido por este Acuerdo."
    ),
    "master.clause4.p4": (
        "Quando o Equipamento for vendido ou transferido permanentemente para outra pessoa jurídica "
        "ou local, a continuidade do Acordo Weber Guardian ficará sujeita à confirmação por escrito da Weber."
    ),
    "master.clause4.p5": "As Partes poderão adicionar ou remover Equipamento durante a vigência do contrato por meio de emenda escrita ao Anexo 1.",

    # 5. GENERAL SERVICE PRINCIPLES
    "master.clause5.title": "5. PRINCÍPIOS GERAIS DE SERVIÇO",
    "master.clause5.p1": (
        "A Weber prestará os Serviços selecionados com pessoal devidamente qualificado e de acordo "
        "com os padrões tecnicamente aceitos e os procedimentos de serviço da Weber aplicáveis ao "
        "Equipamento correspondente."
    ),
    "master.clause5.p2": "A Weber poderá utilizar empresas afiliadas qualificadas ou parceiros de serviço autorizados da Weber para a prestação dos Serviços.",
    "master.clause5.p3": (
        "A Weber determinará o número e a qualificação dos técnicos razoavelmente necessários para "
        "a atividade de serviço aplicável, levando em consideração a configuração do Equipamento e "
        "o escopo do trabalho."
    ),
    "master.clause5.p4": "O Acordo Weber Guardian não constitui garantia de que o Equipamento operará sem interrupções ou falhas.",
    "master.clause5.excluded_intro": (
        "Salvo expressa inclusão em um Anexo aplicável, os seguintes itens não estão incluídos na "
        "taxa fixa Guardian:"
    ),
    "master.clause5.excluded": [
        "reparações corretivas;",
        "peças de reposição;",
        "peças de desgaste e consumíveis;",
        "melhorias ou modificações;",
        "equipamentos de terceiros;",
        "trabalhos fora das horas de serviço acordadas;",
        "intervenções de emergência;",
        "despesas adicionais de deslocamento;",
        "equipamentos especiais de acesso;",
        "materiais de produção;",
        "ferramentas especiais normalmente não exigidas para o Equipamento Weber correspondente; e",
        "trabalhos decorrentes de uso indevido, danos, causas externas ou modificações não aprovadas pela Weber.",
    ],
    "master.clause5.p5": "Tais serviços poderão ser orçados e solicitados separadamente.",

    # 6. CUSTOMER COOPERATION
    "master.clause6.title": "6. COLABORAÇÃO DO CLIENTE",
    "master.clause6.p1": "O Cliente prestará a colaboração razoavelmente necessária para que a Weber possa prestar os Serviços.",
    "master.clause6.p2": "Em particular, o Cliente deverá garantir que:",
    "master.clause6.obligations": [
        "o pessoal da Weber tenha acesso seguro e pontual ao Equipamento correspondente;",
        "o Equipamento esteja disponível no horário acordado;",
        "o Equipamento esteja em condições razoavelmente limpas e acessíveis;",
        "a produção possa ser interrompida quando necessário para o trabalho acordado;",
        "os serviços auxiliares e as conexões técnicas necessárias para o trabalho, incluindo energia elétrica, ar comprimido, água, acesso à rede ou acesso VPN quando aplicável, estejam disponíveis;",
        "haja pessoal do Cliente adequado disponível quando for necessária assistência;",
        "haja produto original suficiente disponível quando for necessário um teste de produção ou funcionalidade;",
        "a Weber seja informada antecipadamente sobre falhas conhecidas, condições operacionais incomuns ou requisitos de segurança;",
        "todos os requisitos específicos de saúde e segurança do local sejam comunicados à Weber antes do início dos trabalhos; e",
        "haja um representante do Cliente com autoridade suficiente para aprovar trabalhos adicionais ou a substituição de componentes quando necessário.",
    ],
    "master.clause6.p3": (
        "Qualquer atraso, tempo de espera ou despesa adicional decorrente do descumprimento dessas "
        "obrigações pelo Cliente poderá ser cobrado separadamente de acordo com as tarifas "
        "aplicáveis da Weber."
    ),

    # 7. SCHEDULING
    "master.clause7.title": "7. PROGRAMAÇÃO",
    "master.clause7.p1": (
        "As inspeções planejadas, visitas de manutenção, treinamentos e outros Serviços programados "
        "serão coordenados entre a Weber e o Cliente."
    ),
    "master.clause7.p2": "A Weber utilizará esforços razoáveis para informar ao Cliente, com antecedência, a data planejada.",
    "master.clause7.p3": "O prazo de aviso aplicável, quando especificamente acordado, será indicado no Anexo correspondente ou no Anexo 1.",
    "master.clause7.p4": "Se alguma das Partes não puder realizar uma atividade acordada na data programada, informará a outra Parte assim que razoavelmente possível.",
    "master.clause7.p5": (
        "Quando uma visita programada não puder ser realizada por motivos atribuíveis ao Cliente, "
        "a Weber poderá cobrar os custos razoavelmente incorridos, incluindo deslocamento, "
        "hospedagem, tempo de espera e capacidade de pessoal reservada."
    ),

    # 8. ADDITIONAL WORK IDENTIFIED DURING A SERVICE ACTIVITY
    "master.clause8.title": "8. TRABALHOS ADICIONAIS IDENTIFICADOS DURANTE UMA ATIVIDADE DE SERVIÇO",
    "master.clause8.p1": "Quando uma inspeção, atividade de manutenção, auditoria ou outro serviço Guardian identificar trabalhos adicionais, a Weber informará o Cliente.",
    "master.clause8.p2": "Salvo disposição expressa em contrário no Anexo 1, tais trabalhos adicionais não farão automaticamente parte da taxa fixa Guardian.",
    "master.clause8.p3": (
        "A manutenção corretiva, as reparações, as modificações, as melhorias e a substituição de "
        "peças identificadas durante uma inspeção exigirão autorização do Cliente."
    ),
    "master.clause8.p4": "Quando aplicável, a Weber poderá emitir um orçamento separado ou uma recomendação de peças de reposição após a atividade de serviço.",
    "master.clause8.p5": (
        "Nenhum trabalho adicional cobrável será realizado intencionalmente sem a autorização do "
        "Cliente, exceto quando a ação imediata for razoavelmente necessária para prevenir um risco "
        "iminente de segurança e tal ação for permitida pelas leis aplicáveis e pelas regras do local."
    ),

    # 9. PRICES AND PAYMENT
    "master.clause9.title": "9. PREÇOS E PAGAMENTO",
    "master.clause9.p1": "Os preços aplicáveis ao Acordo Weber Guardian estão indicados no Anexo 1.",
    "master.clause9.p2": "Salvo expressa disposição em contrário, todos os preços não incluem o IVA e outros tributos aplicáveis.",
    "master.clause9.p3": (
        "A moeda aplicável, a frequência de faturamento, as condições de pagamento, as condições de "
        "deslocamento, as condições de frete, os descontos e as tarifas de serviço adicionais serão "
        "os especificados no Anexo 1 ou no Anexo do serviço correspondente."
    ),
    "master.clause9.p4": "As taxas recorrentes do Guardian serão faturadas conforme a frequência de faturamento indicada no Anexo 1.",
    "master.clause9.p5": (
        "Serviços, materiais e despesas não incluídos na taxa Guardian acordada serão faturados "
        "separadamente às tarifas acordadas aplicáveis."
    ),
    "master.clause9.p6": "A Weber poderá ajustar os preços recorrentes de acordo com o mecanismo anual de ajuste de preço indicado no Anexo 1.",
    "master.clause9.p7": (
        "Qualquer desconto acordado aplicar-se-á somente às categorias expressamente identificadas "
        "no Anexo correspondente e não será acumulado com outros descontos, salvo acordo expresso."
    ),

    # 10. PARTS AND MATERIALS
    "master.clause10.title": "10. PEÇAS E MATERIAIS",
    "master.clause10.p1": (
        "Salvo quando especificamente incluídos no Anexo 1 ou em um Anexo de serviço aplicável, as "
        "peças de reposição, as peças de desgaste, as lâminas, os lubrificantes e outros materiais "
        "não estão incluídos na taxa de serviço Guardian."
    ),
    "master.clause10.p2": (
        "As peças fornecidas pela Weber serão faturadas pelo preço aplicável na data de "
        "fornecimento, menos qualquer desconto Guardian expressamente acordado nos termos do Anexo 4 "
        "ou do Anexo 5."
    ),
    "master.clause10.p3": (
        "Quando os componentes substituídos forem disponibilizados ao Cliente para inspeção, o "
        "Cliente será responsável pelo seu posterior descarte, salvo acordo em contrário."
    ),
    "master.clause10.p4": (
        "A Weber não se responsabilizará por defeitos, danos, desempenho reduzido ou efeitos "
        "consequenciais causados por componentes não originais, modificações não autorizadas ou "
        "trabalhos realizados por terceiros, na medida permitida pela legislação aplicável."
    ),
    "master.clause10.p5": (
        "A propriedade dos bens fornecidos permanecerá com a Weber até o pagamento integral, quando "
        "permitido pelas condições locais e pela legislação aplicável."
    ),

    # 11. ACCEPTANCE AND SERVICE REPORTING
    "master.clause11.title": "11. ACEITAÇÃO E RELATÓRIOS DE SERVIÇO",
    "master.clause11.p1": (
        "Quando a natureza de um Serviço permitir a verificação funcional, o Cliente proporcionará "
        "à Weber uma oportunidade razoável de testar o Equipamento após a conclusão da atividade."
    ),
    "master.clause11.p2": (
        "Quando o Cliente identificar uma deficiência material na prestação de um Serviço, "
        "notificará a Weber sem demora indevida e fornecerá informações suficientes para que a "
        "Weber possa avaliar a questão."
    ),
    "master.clause11.p3": (
        "Se um Serviço comprovadamente não tiver sido executado de acordo com o escopo acordado e a "
        "Weber for responsável pela deficiência, a Weber deverá, como remédio principal, reexecutar "
        "ou corrigir o Serviço afetado dentro de um prazo razoável."
    ),
    "master.clause11.p4": (
        "Relatórios de serviço, relatórios de inspeção, relatórios de auditoria e recomendações "
        "documentam o estado observado no momento da atividade e não constituem garantia do "
        "desempenho futuro da máquina."
    ),

    # 12. WARRANTY AND LIABILITY
    "master.clause12.title": "12. GARANTIA E RESPONSABILIDADE",
    "master.clause12.p1": "A Weber executará os Serviços com o cuidado e a competência profissionais razoáveis.",
    "master.clause12.p2": (
        "A responsabilidade da Weber será regida pelas disposições imperativas da legislação "
        "aplicável e pelos Termos e Condições Gerais aplicáveis da Weber."
    ),
    "master.clause12.p3": (
        "Na máxima medida permitida por lei, a Weber não se responsabilizará por danos indiretos "
        "ou consequenciais, incluindo perda de produção, perda de lucros, perda de negócios ou "
        "outros prejuízos comerciais indiretos, salvo quando tal limitação for proibida pela "
        "legislação aplicável."
    ),
    "master.clause12.p4": "Nada neste Acuerdo excluirá a responsabilidade que legalmente não possa ser excluída nem limitada.",
    "master.clause12.p5": (
        "Quando um descumprimento ou atraso resultar de circunstâncias fora do controle razoável "
        "da Weber, incluindo descumprimento ou atraso de fornecedores, perturbações no transporte, "
        "conflitos trabalhistas, eventos naturais, medidas governamentais, incidentes cibernéticos, "
        "epidemias ou outros eventos de força maior, o período de prestação afetado será prorrogado "
        "na medida razoavelmente necessária."
    ),

    # 13. CONTRACT TERM AND RENEWAL
    "master.clause13.title": "13. VIGÊNCIA E RENOVAÇÃO DO CONTRATO",
    "master.clause13.p1": "Este Acordo entra em vigor na Data de início do contrato indicada no Anexo 1.",
    "master.clause13.term": "Prazo inicial",
    "master.clause13.renewal": "Prazo de renovação",
    "master.clause13.notice": "Prazo de aviso",
    "master.clause13.p2": (
        "Salvo indicação em contrário no Anexo 1, o Acordo se renovará automaticamente por "
        "períodos de renovação sucessivos, salvo denúncia por escrito dentro do prazo de aviso "
        "aplicável."
    ),
    "master.clause13.p3": (
        "A rescisão ou o vencimento do Acordo-Mestre encerrará todos os Anexos de serviço, salvo "
        "acordo expresso em contrário."
    ),
    "master.clause13.p4": "Serviços opcionais individuais podem ter datas de início ou de vencimento diferentes quando expressamente indicado no Anexo correspondente.",

    # 14. CHANGES TO THE AGREEMENT
    "master.clause14.title": "14. ALTERAÇÕES NO ACORDO",
    "master.clause14.p1": (
        "Alterações no Equipamento abrangido, na frequência de serviço, nos módulos Guardian, nos "
        "descontos, nos níveis de serviço, nos preços ou em outras condições contratuais materiais "
        "deverão ser documentadas por escrito."
    ),
    "master.clause14.p2": "Um Anexo atualizado gerado e aceito por ambas as Partes poderá constituir tal emenda escrita.",

    # 15. CONFIDENTIALITY
    "master.clause15.title": "15. CONFIDENCIALIDADE",
    "master.clause15.p1": (
        "Cada Parte manterá como confidencial toda a informação comercial, técnica e operacional "
        "não pública recebida da outra Parte em relação a este Acuerdo."
    ),
    "master.clause15.p2": "Tal informação será utilizada somente para a execução e a administração da relação Guardian.",
    "master.clause15.p3": "Esta obrigação não se aplicará à informação que:",
    "master.clause15.exceptions": [
        "já esteja legitimamente no domínio público;",
        "tenha sido legitimamente conhecida pela Parte receptora antes da divulgação;",
        "seja legitimamente recebida de terceiro sem restrições de confidencialidade; ou",
        "deva ser divulgada por força de lei ou de autoridade competente.",
    ],

    # 16. INTELLECTUAL PROPERTY
    "master.clause16.title": "16. PROPRIEDADE INTELECTUAL",
    "master.clause16.p1": (
        "Todos os direitos de propriedade intelectual sobre a documentação da Weber, os métodos de "
        "serviço, as listas de verificação, o software, as informações técnicas, os materiais de "
        "treinamento, as análises e outros conteúdos proprietários da Weber permanecerão propriedade "
        "da Weber ou do titular dos direitos correspondentes."
    ),
    "master.clause16.p2": "O Cliente poderá utilizar internamente a documentação fornecida nos termos deste Acordo para a operação e a manutenção do seu Equipamento.",
    "master.clause16.p3": "Nenhum direito de propriedade intelectual é transferido ao Cliente, salvo acordo expresso por escrito.",

    # 17. ASSIGNMENT AND SERVICE PARTNERS
    "master.clause17.title": "17. CESSÃO E PARCEIROS DE SERVIÇO",
    "master.clause17.p1": "A Weber poderá cumprir suas obrigações por meio de empresas do grupo Weber ou de parceiros de serviço qualificados e autorizados da Weber.",
    "master.clause17.p2": "A Weber poderá ceder os direitos e obrigações decorrentes deste Acuerdo a outra empresa do grupo Weber, sujeito à legislação aplicável.",
    "master.clause17.p3": (
        "O Cliente não poderá ceder este Acuerdo a terceiro sem o consentimento prévio por escrito "
        "da Weber, o qual não será injustificadamente negado quando a continuidade da relação "
        "contratual for comercial e tecnicamente viável."
    ),

    # 18. GOVERNING LAW AND JURISDICTION
    "master.clause18.title": "18. LEI APLICÁVEL E JURISDIÇÃO",
    "master.clause18.law": "Lei aplicável",
    "master.clause18.jurisdiction": "Jurisdição",
    "master.clause18.p1": "As disposições acima ficam sujeitas, em cada caso, à legislação imperativa aplicável.",

    # 19. GENERAL PROVISIONS
    "master.clause19.title": "19. DISPOSIÇÕES GERAIS",
    "master.clause19.p1": (
        "Se qualquer disposição deste Acuerdo for considerada inválida ou inaplicável, as "
        "disposições restantes permanecerão inalteradas."
    ),
    "master.clause19.p2": "O fato de uma das Partes não exercer um direito contratual não constituirá renúncia a esse direito.",
    "master.clause19.p3": (
        "Este Acuerdo e seus Anexos aplicáveis constituem o acordo entre as Partes relativo aos "
        "Serviços Guardian aqui descritos e substituem propostas ou entendimentos anteriores "
        "relativos especificamente ao mesmo escopo de serviço, salvo quando expressamente incorporados."
    ),
    "master.clause19.p4": "As emendas serão formalizadas por escrito.",
    "master.clause19.p5": (
        "Assinaturas eletrônicas poderão ser utilizadas quando legalmente permitido e terão os "
        "mesmos efeitos que as assinaturas manuscritas."
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
        "O módulo Manutenção e Inspeção tem por objetivo avaliar e manter a condição do Equipamento "
        "identificado no Anexo 1, identificar as ações técnicas necessárias e apoiar a operação "
        "confiável e o planejamento da manutenção."
    ),
    "annex2.purpose.p2": "As atividades exatas incluídas dependem das opções selecionadas na configuração Guardian.",
    "annex2.inspection.title": "2. Inspeção",
    "annex2.inspection.p1": "A Weber realizará inspeções do Equipamento selecionado com a frequência indicada no Anexo 1.",
    "annex2.inspection.p2": "Uma inspeção pode incluir, quando aplicável ao Equipamento selecionado:",
    "annex2.inspection.includes": [
        "revisão do estado geral da máquina;",
        "inspeção baseada na lista de verificação específica da máquina ou do módulo da Weber;",
        "revisão dos sensores e componentes elétricos relevantes;",
        "inspeção de acionamentos, correias e componentes mecânicos;",
        "inspeção de componentes pneumáticos;",
        "inspeção de vedações e carcaças da máquina;",
        "verificação e ajuste de componentes mecanicamente móveis quando razoavelmente necessário;",
        "revisão das configurações relevantes da máquina;",
        "identificação de desgastes ou anormalidades visíveis;",
        "identificação de necessidades pendentes de reparo ou manutenção;",
        "discussão dos problemas conhecidos com o pessoal responsável do Cliente; e",
        "verificação funcional após a inspeção quando aplicável.",
    ],
    "annex2.inspection.p3": (
        "Quando útil e operacionalmente viável, a Weber poderá revisar o processo de produção "
        "utilizando o produto original do Cliente."
    ),
    "annex2.inspection.p4": (
        "A abertura de áreas específicas protegidas da máquina, como carcaças de pesagem ou de "
        "cabeças de corte, será realizada quando tecnicamente apropriado e acordado."
    ),
    "annex2.checklist.title": "3. Lista de verificação da máquina",
    "annex2.checklist.p1": "A Weber documentará a inspeção utilizando a lista de verificação de inspeção aplicável da Weber.",
    "annex2.checklist.p2": "A lista de verificação registra os elementos inspecionados e o seu estado observado no momento da inspeção.",
    "annex2.checklist.p3": (
        "A lista de verificação tem caráter de registro técnico de serviço e não constitui "
        "certificação de que o Equipamento está livre de defeitos nem de que nenhuma falha futura "
        "possa ocorrer."
    ),
    "annex2.report.title": "4. Relatório de inspeção",
    "annex2.report.p1": "Após a inspeção, a Weber fornecerá um relatório de inspeção resumindo os principais achados.",
    "annex2.report.p2": "O relatório pode incluir:",
    "annex2.report.includes": [
        "achados sobre a condição;",
        "desgastes identificados;",
        "manutenção ou reparações recomendadas;",
        "peças de reposição recomendadas;",
        "observações técnicas;",
        "riscos identificados que exigem atenção adicional; e",
        "prioridades ou próximas ações recomendadas.",
    ],
    "annex2.report.p3": (
        "Quando aplicável, a Weber poderá preparar um orçamento separado para as peças, "
        "reparações, melhorias ou outras atividades decorrentes da inspeção."
    ),
    "annex2.preventive.title": "5. Manutenção preventiva",
    "annex2.preventive.p1": "A Weber realizará as atividades de manutenção preventiva expressamente definidas para o Equipamento no Anexo 1.",
    "annex2.preventive.p2": "A manutenção preventiva pode incluir:",
    "annex2.preventive.includes": [
        "ajuste mecânico;",
        "lubrificação;",
        "limpeza de componentes tecnicamente relevantes;",
        "substituição de filtros, vedações ou componentes de desgaste definidos;",
        "verificação e ajuste de acionamentos e correias;",
        "verificação de elementos pneumáticos;",
        "verificação de componentes elétricos e sensores; e",
        "outras tarefas de manutenção preventiva específicas da máquina identificadas no plano de manutenção aplicável da Weber.",
    ],
    "annex2.preventive.p3": (
        "Peças de reposição, peças de desgaste e consumíveis não estão incluídos, salvo expressa "
        "disposição no Anexo 1 ou em um kit de manutenção acordado."
    ),
    "annex2.kit.title": "6. Peças de reposição / kit de manutenção",
    "annex2.kit.p1": (
        "O kit de manutenção conterá somente as peças expressamente identificadas no orçamento "
        "aplicável ou na programação de equipamento."
    ),
    "annex2.kit.p2": "O preço do kit será apresentado separadamente no Anexo 1.",
    "annex2.kit.p3": "As peças não utilizadas permanecem sujeitas às condições comerciais indicadas no Anexo 1.",
    "annex2.repairs.title": "7. Manutenção adicional e reparações",
    "annex2.repairs.p1": (
        "As reparações e a manutenção corretiva identificadas durante uma inspeção não estão "
        "incluídas no preço padrão da inspeção, salvo disposição específica em contrário."
    ),
    "annex2.repairs.p2": "Quando trabalhos adicionais forem recomendados, a Weber obterá a aprovação do Cliente ou emitirá um orçamento separado.",
    "annex2.frequency.title": "8. Frequência de inspeção",
    "annex2.frequency.value": "Frequência",
    "annex2.frequency.planned": "Inspeções planejadas por ano contratual",
    "annex2.frequency.p1": "A programação efetiva será coordenada entre a Weber e o Cliente.",
    "annex2.hours.title": "9. Horas de serviço",
    "annex2.hours.p1": "Os serviços serão normalmente realizados durante: {{Standard_Service_Hours}}",
    "annex2.hours.p2": "Trabalhos solicitados fora dessas horas poderão estar sujeitos a cobranças adicionais.",

    # Annex 3 - Service Support
    "annex3.title": "ANEXO 3 - SUPORTE DE SERVIÇO",
    "annex3.tagline": "Linha de atendimento, suporte remoto e resposta técnica prioritária.",
    "annex3.purpose.title": "1. Objetivo",
    "annex3.purpose.p1": (
        "O módulo Suporte de Serviço oferece ao Cliente acesso ao suporte técnico da Weber para o "
        "Equipamento abrangido por este Acuerdo."
    ),
    "annex3.purpose.p2": "O nível de serviço exato depende das opções selecionadas abaixo.",
    "annex3.hotline.title": "2. Linha de atendimento padrão",
    "annex3.hotline.p1": "O Cliente terá acesso à linha de atendimento de serviços da Weber durante as horas de suporte aplicáveis.",
    "annex3.hotline.hours": "Horas de suporte",
    "annex3.hotline.phone": "Telefone",
    "annex3.hotline.email": "E-mail",
    "annex3.hotline.p2": "A linha de atendimento oferece suporte técnico de primeiro nível e coordenação.",
    "annex3.hotline.p3": (
        "Quando o problema não puder ser resolvido por meio da linha de atendimento, a Weber poderá "
        "recomendar o Suporte Remoto, uma visita de serviço no local, peças de reposição ou outra "
        "ação técnica."
    ),
    "annex3.hotline.p4": (
        "O serviço no local não está incluído simplesmente por contar com o suporte da Linha de "
        "Atendimento padrão, salvo expressa disposição no Anexo 1."
    ),
    "annex3.remote.title": "3. Suporte remoto",
    "annex3.remote.p1": (
        "Quando tecnicamente disponível e autorizado pelo Cliente, a Weber poderá prestar "
        "diagnóstico e suporte técnico remotos."
    ),
    "annex3.remote.p2": (
        "O Cliente fornecerá as conexões de rede, o acesso VPN, a autorização de usuários e as "
        "demais condições técnicas razoavelmente necessárias para o acesso remoto."
    ),
    "annex3.remote.p3": "O Suporte remoto pode incluir:",
    "annex3.remote.includes": [
        "análise remota de falhas;",
        "revisão do estado da máquina ou das informações de diagnóstico;",
        "auxílio em verificações de parâmetros ou configuração;",
        "apoio ao pessoal de manutenção do Cliente; e",
        "recomendações de ações adicionais.",
    ],
    "annex3.remote.p4": "O Suporte remoto não garante que uma falha possa ser corrigida sem uma intervenção no local.",
    "annex3.priority.title": "4. Resposta prioritária",
    "annex3.priority.p1": (
        "Solicitações relativas ao Equipamento abrangido por este Acordo receberão tratamento "
        "prioritário dentro da organização de serviços da Weber em comparação com solicitações "
        "padrão sem contrato, sujeito à disponibilidade de técnicos e ao nível de serviço aplicável."
    ),
    "annex3.priority.target": "Tempo-alvo de primeira resposta",
    "annex3.priority.p2": (
        "A Resposta prioritária refere-se à priorização da solicitação de suporte. Não constitui "
        "tempo de reparo garantido, disponibilidade da máquina garantida nem tempo de chegada ao "
        "local garantido, salvo expressa disposição em contrário no Anexo 1."
    ),

    # Annex 4 - Parts & Availability
    "annex4.title": "ANEXO 4 - PEÇAS E DISPONIBILIDADE",
    "annex4.tagline": "Condições comerciais de peças de reposição, tratamento prioritário e estoque recomendado.",
    "annex4.purpose.title": "1. Objetivo",
    "annex4.purpose.p1": (
        "O módulo Peças e Disponibilidade apoia o planejamento estruturado de peças de reposição e "
        "o acesso às peças de reposição originais da Weber para o Equipamento abrangido por este "
        "Acuerdo."
    ),
    "annex4.discount.title": "2. Desconto sobre peças",
    "annex4.discount.p1": (
        "O Cliente receberá o seguinte desconto sobre as peças de reposição elegíveis da Weber para "
        "o Equipamento abrangido pelo Acordo Weber Guardian:"
    ),
    "annex4.discount.amount": "Desconto Guardian sobre peças {{Parts_Discount}} %",
    "annex4.discount.p2": "O desconto aplica-se às peças de reposição originais da Weber, salvo indicação em contrário.",
    "annex4.discount.p3": "Os seguintes conceitos podem ficar excluídos:",
    "annex4.discount.excluded": [
        "peças de troca (exchange);",
        "lâminas;",
        "itens com preço especial;",
        "produtos de terceiros;",
        "custos de frete e de envio expresso;",
        "serviços e mão de obra; e",
        "itens já sujeitos a outro preço especial ou desconto.",
    ],
    "annex4.discount.p4": "Os descontos não são acumulativos, salvo acordo expresso.",
    "annex4.handling.title": "3. Tratamento prioritário",
    "annex4.handling.p1": (
        "Consultas e pedidos de peças relativos ao Equipamento abrangido por este Acordo receberão "
        "tratamento prioritário dentro da organização de peças aplicável da Weber."
    ),
    "annex4.handling.p2": "O tratamento prioritário inclui a aceleração do processamento interno quando razoavelmente possível.",
    "annex4.handling.p3": (
        "Não constitui tempo de entrega garantido quando a peça solicitada não estiver disponível "
        "em estoque ou quando a entrega depender de fornecedores externos, produção ou transporte."
    ),
    "annex4.parts_list.title": "4. Lista de peças recomendadas",
    "annex4.parts_list.p1": (
        "A Weber fornecerá, quando técnica e comercialmente disponível, uma lista de peças de "
        "reposição recomendadas para o Equipamento selecionado."
    ),
    "annex4.parts_list.categories": [
        "A - Itens locais / de disponibilidade imediata: Peças normalmente disponíveis na organização responsável da Weber.",
        "B - Itens de estoque central: Peças normalmente disponíveis no estoque central da Weber.",
        "C - Itens recomendados em estoque do Cliente: Peças de reposição críticas ou de maior risco que a Weber recomenda que o Cliente mantenha localmente.",
        "D - Peças de desgaste: Peças que exigem substituição conforme o uso.",
        "E - Peças sob encomenda / de longo prazo: Peças que normalmente não são mantidas em estoque e podem exigir fabricação ou prazos prolongados de suprimento.",
    ],
    "annex4.parts_list.p2": (
        "A lista de peças de reposição recomendadas constitui uma recomendação baseada na "
        "configuração da máquina e nas informações de serviço disponíveis. Não é garantia de que "
        "todos os possíveis cenários de falha estejam cobertos."
    ),
    "annex4.delivery.title": "5. Condições de entrega",
    "annex4.delivery.p1": "A disponibilidade de estoque e as condições de entrega ficam sujeitas ao Anexo 1.",
    "annex4.delivery.condition": "Condição padrão de entrega",
    "annex4.delivery.threshold": "Limite de frete grátis",
    "annex4.delivery.courier": "Custos de entrega expressa / mensageria",
    "annex4.delivery.courier.value": "Cobrados separadamente, salvo acordo em contrário.",

    # Annex 5 - Blade Solutions
    "annex5.title": "ANEXO 5 - SOLUÇÕES DE LÂMINAS",
    "annex5.tagline": "Condições comerciais, disponibilidade e suporte técnico dos programas de lâminas da Weber.",
    "annex5.intro": (
        "O módulo Soluções de Lâminas tem por objetivo apoiar a seleção correta, a disponibilidade, "
        "o uso e a gestão das lâminas da Weber, incluindo o princípio \"Lâmina certa, aplicação "
        "correta\"."
    ),
    "annex5.discount.title": "1. Desconto sobre lâminas",
    "annex5.discount.p1": "O Cliente receberá o seguinte Desconto Guardian sobre as lâminas elegíveis da Weber:",
    "annex5.discount.amount": "Desconto sobre lâminas {{Blade_Discount}} %",
    "annex5.discount.p2": (
        "As lâminas aplicáveis, os locais do Cliente, as máquinas, as quantidades comprometidas e "
        "qualquer preço especial serão listados na programação comercial quando necessário."
    ),
    "annex5.discount.p3": (
        "Os descontos sobre lâminas não se acumulam com outras promoções de lâminas ou preços "
        "especiais, salvo acordo expresso."
    ),
    "annex5.discount.p4": (
        "Quando forem acordados preços de lâminas por prazo fixo, o prazo aplicável e as condições "
        "de preço serão indicados no Anexo 1."
    ),
    "annex5.stock.title": "2. Acordo de estoque",
    "annex5.stock.p1": "A Weber e o Cliente poderão estabelecer um conceito de estoque de lâminas acordado com base no consumo previsto.",
    "annex5.stock.p2": "O acordo de estoque definirá, quando aplicável:",
    "annex5.stock.defines": [
        "as referências de lâminas;",
        "a quantidade de estoque acordada;",
        "o estoque mínimo;",
        "o estoque máximo;",
        "o consumo anual previsto;",
        "o método de reposição;",
        "a localização do estoque;",
        "a propriedade do estoque;",
        "as condições de entrega; e",
        "o tratamento do estoque obsoleto ou não utilizado.",
    ],
    "annex5.stock.p3": (
        "O Cliente fornecerá informações de consumo razoavelmente precisas e notificará a Weber "
        "sobre mudanças materiais na produção ou na demanda por lâminas."
    ),
    "annex5.stock.p4": (
        "O acordo de estoque tem por objetivo melhorar a disponibilidade, mas não constitui "
        "garantia incondicional de fornecimento ininterrupto em circunstâncias fora do controle "
        "razoável da Weber."
    ),
    "annex5.sharpening.title": "3. Avaliação do afiamento",
    "annex5.sharpening.p1": "A Weber avaliará o processo e a capacidade de afiamento de lâminas do Cliente conforme acordado.",
    "annex5.sharpening.p2": "A avaliação pode incluir:",
    "annex5.sharpening.includes": [
        "o equipamento de afiamento;",
        "o processo de afiamento;",
        "o manuseio de lâminas;",
        "a condição das lâminas;",
        "os parâmetros de amolação;",
        "as práticas de manutenção;",
        "o armazenamento de lâminas;",
        "a consistência do processo; e",
        "oportunidades de melhoria.",
    ],
    "annex5.sharpening.p3": "A Weber poderá emitir recomendações após a avaliação.",
    "annex5.sharpening.p4": (
        "Salvo inclusão específica, a implementação dessas recomendações, as reparações ou "
        "modificações no equipamento de afiamento e o treinamento adicional não estão incluídos."
    ),
    "annex5.application.title": "4. Revisão da aplicação de lâminas",
    "annex5.application.p1": (
        "Quando incluído no programa de lâminas selecionado, a Weber poderá revisar a combinação "
        "lâmina-produto com o objetivo de apoiar o princípio \"Lâmina certa, aplicação correta\"."
    ),
    "annex5.application.p2": (
        "As recomendações poderão considerar o tipo de produto, as condições de corte, a "
        "configuração da máquina, a geometria da lâmina e os requisitos operacionais."
    ),

    # Annex 6 - Training & Optimization
    "annex6.title": "ANEXO 6 - TREINAMENTO E OTIMIZAÇÃO",
    "annex6.tagline": "Treinamento de operadores, treinamento de manutenção, otimização de linha e auditorias EPIP.",
    "annex6.intro": (
        "O módulo Treinamento e Otimização oferece atividades selecionadas destinadas a melhorar a "
        "operação das máquinas, a capacidade de manutenção e o desempenho da produção."
    ),
    "annex6.operator.title": "1. Treinamento de operadores",
    "annex6.operator.p1": "A Weber fornecerá treinamento voltado aos operadores para o Equipamento selecionado.",
    "annex6.operator.p2": "O conteúdo do treinamento pode incluir, dependendo da máquina e dos objetivos acordados:",
    "annex6.operator.includes": [
        "a operação correta da máquina;",
        "as configurações básicas da máquina;",
        "as rotinas de operação;",
        "a troca de produto;",
        "as verificações realizadas pelo operador;",
        "as considerações de limpeza e inspeção;",
        "a identificação de comportamentos anormais da máquina; e",
        "as boas práticas de operação.",
    ],
    "annex6.operator.quantity": "Número de sessões / dias",
    "annex6.operator.p3": "O treinamento será ministrado ao pessoal designado pelo Cliente.",
    "annex6.operator.p4": (
        "Salvo expressa disposição em contrário, o treinamento não constitui certificação formal "
        "do pessoal do Cliente."
    ),
    "annex6.maintenance.title": "2. Treinamento de manutenção",
    "annex6.maintenance.p1": "A Weber fornecerá treinamento técnico ao pessoal de manutenção do Cliente.",
    "annex6.maintenance.p2": "O treinamento pode incluir:",
    "annex6.maintenance.includes": [
        "a construção da máquina e seus princípios de funcionamento;",
        "a manutenção preventiva;",
        "os pontos de inspeção;",
        "a identificação de peças de desgaste;",
        "a metodologia de resolução de problemas;",
        "o ajuste mecânico;",
        "os componentes elétricos ou pneumáticos relevantes;",
        "a documentação de manutenção; e",
        "as práticas de manutenção recomendadas.",
    ],
    "annex6.maintenance.quantity": "Número de sessões / dias",
    "annex6.optimization.title": "3. Otimização de linha",
    "annex6.optimization.p1": (
        "A Weber realizará uma revisão acordada da linha de produção selecionada com o objetivo de "
        "identificar oportunidades de melhoria de desempenho."
    ),
    "annex6.optimization.p2": "A atividade pode incluir:",
    "annex6.optimization.includes": [
        "a revisão dos parâmetros da máquina;",
        "a observação da produção;",
        "a análise das condições de operação;",
        "a revisão da interação entre linhas;",
        "a identificação de restrições de desempenho;",
        "o ajuste de parâmetros selecionados quando aplicável; e",
        "recomendações de melhoria adicional.",
    ],
    "annex6.optimization.quantity": "Número de atividades de otimização",
    "annex6.optimization.p3": (
        "A Otimização de Linha não constitui garantia de produção, desempenho, OEE, redução de "
        "giveaway ou outra melhoria de desempenho específicos, salvo quando um compromisso de "
        "desempenho específico seja expressamente acordado por escrito."
    ),
    "annex6.epip.title": "4. Auditoria EPIP",
    "annex6.epip.p1": "A Weber realizará uma auditoria EPIP no Equipamento ou nas linhas especificadas no Anexo 1.",
    "annex6.epip.p2": (
        "A auditoria incluirá uma avaliação da linha selecionada e um relatório identificando os "
        "achados, oportunidades e ações prioritárias relevantes."
    ),
    "annex6.epip.p3": (
        "Quando aplicável, os resultados serão revisados com o Cliente e incorporados ao plano de "
        "ação Guardian em andamento."
    ),
    "annex6.epip.quantity": "Número de auditorias EPIP",
    "annex6.epip.lines": "Linhas abrangidas",
    "annex6.epip.p4": (
        "Ações corretivas, reparações, melhorias ou peças decorrentes da auditoria não estão "
        "incluídas, salvo expressa disposição."
    ),
    "annex6.followup.title": "5. Acompanhamento",
    "annex6.followup.p1": (
        "Quando incluído no pacote selecionado, a Weber poderá realizar reuniões ou chamadas de "
        "acompanhamento antes e depois das atividades selecionadas para revisar:"
    ),
    "annex6.followup.items": [
        "os objetivos acordados;",
        "as atividades realizadas;",
        "o impacto observado;",
        "os itens de ação pendentes;",
        "as prioridades técnicas; e",
        "as próximas ações.",
    ],

    # Annex 7 - Digital Services
    "annex7.title": "ANEXO 7 - SERVIÇOS DIGITAIS",
    "annex7.tagline": "Factory Cockpit, revisão de desempenho, revisão MRO e gestão dedicada de contas.",
    "annex7.intro": (
        "O módulo Serviços Digitais oferece serviços selecionados de monitoramento digital, revisão "
        "de desempenho e gestão de contas."
    ),
    "annex7.cockpit.title": "1. Factory Cockpit",
    "annex7.cockpit.p1": (
        "Quando o Equipamento selecionado for tecnicamente compatível, a Weber dará suporte à "
        "conexão do Equipamento acordado ao Factory Cockpit de acordo com as condições do serviço "
        "digital aplicáveis."
    ),
    "annex7.cockpit.lines": "Linha(s) conectada(s)",
    "annex7.cockpit.p2": (
        "O Factory Cockpit pode ser utilizado para coletar e visualizar os dados de desempenho "
        "disponíveis das máquinas com o objetivo da revisão e da otimização do desempenho."
    ),
    "annex7.cockpit.p3": (
        "O Cliente fornecerá a infraestrutura de rede, as permissões e o acesso técnico "
        "razoavelmente necessários para a conexão."
    ),
    "annex7.cockpit.p4": (
        "A disponibilidade de dados específicos depende da geração da máquina, do software "
        "instalado e da conectividade do Equipamento correspondente."
    ),
    "annex7.cockpit.p5": (
        "Quaisquer licenças de software separadas ou condições do serviço digital aplicáveis ao "
        "Factory Cockpit permanecerão aplicáveis."
    ),
    "annex7.performance.title": "2. Revisão de desempenho",
    "annex7.performance.p1": "A Weber e o Cliente realizarão revisões periódicas dos dados de desempenho disponíveis do Equipamento.",
    "annex7.performance.frequency": "Frequência de revisão",
    "annex7.performance.p2": "A revisão pode incluir:",
    "annex7.performance.includes": [
        "os KPIs selecionados da máquina;",
        "tendências de desempenho;",
        "observações técnicas recorrentes;",
        "oportunidades de melhoria identificadas;",
        "atividades realizadas;",
        "ações pendentes; e",
        "prioridades do próximo período de revisão.",
    ],
    "annex7.performance.p3": "As Partes poderão acordar KPIs e valores-alvo específicos do Cliente.",
    "annex7.performance.p4": (
        "Salvo acordo expresso em contrário, tais valores-alvo são objetivos de gestão e não "
        "garantias contratuais de desempenho."
    ),
    "annex7.mro.title": "3. Revisão MRO",
    "annex7.mro.p1": (
        "A Weber revisará periodicamente as informações disponíveis sobre as despesas de Manutenção, "
        "Reparo e Operações (MRO) do Equipamento abrangido."
    ),
    "annex7.mro.p2": "A revisão pode incluir:",
    "annex7.mro.includes": [
        "as despesas com peças de reposição;",
        "as despesas com serviços;",
        "as despesas com lâminas quando relevante;",
        "o histórico de atividades de manutenção;",
        "as informações da base instalada;",
        "tendências de manutenção;",
        "os fatores de custo identificados; e",
        "a comparação com uma meta de planejamento MRO acordada.",
    ],
    "annex7.mro.frequency": "Frequência de revisão MRO",
    "annex7.mro.target": "Meta MRO acordada, se aplicável",
    "annex7.mro.p3": (
        "O objetivo da revisão é apoiar o planejamento da manutenção e identificar oportunidades "
        "de melhoria. Não constitui garantia de que um determinado nível de despesa MRO será "
        "alcançado."
    ),
    "annex7.account.title": "4. Equipe dedicada de conta",
    "annex7.account.p1": "A Weber designará uma estrutura de gestão de conta Guardian para o Cliente.",
    "annex7.account.p2": (
        "A equipe coordenará as atividades Guardian selecionadas e atuará como ponto central para "
        "a revisão periódica do programa."
    ),
    "annex7.account.p3": "O processo de gestão de contas pode incluir:",
    "annex7.account.includes": [
        "revisões programadas do Cliente;",
        "a coordenação entre as funções relevantes da Weber;",
        "a revisão de ações em aberto;",
        "a revisão das próximas atividades de serviço;",
        "a revisão das necessidades de peças e lâminas;",
        "discussões de desempenho;",
        "oportunidades de otimização; e",
        "o acompanhamento das ações acordadas.",
    ],
    "annex7.account.cadence": "Cadência de revisão",
    "annex7.account.p4": (
        "A equipe dedicada de conta complementa, mas não substitui, os canais operacionais normais "
        "da Weber para solicitações urgentes de serviço, pedidos de peças de reposição ou suporte "
        "de emergência."
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
