"""
Dados de exemplo do ambiente local (usados por `seed_mock_data`).

Tudo aqui é fictício, exceto os nomes e as descrições dos quatro programas do ICC,
que são os reais. Pessoas, empresas, e-mails e links são inventados e usam
example.com, para nunca apontar para alguém de verdade. Cada caso de borda que o
admin ou o site tratam (campo vazio, item oculto, rascunho, texto muito longo) tem
pelo menos um exemplo, marcado em comentário.
"""
from datetime import date

POSICOES = [
    ("Presidente", 0),
    ("Vice-presidente", 1),
    ("Diretor de Projetos", 2),
    ("Diretor de Capacitação", 2),
    ("Diretor de Relacionamento", 2),
    ("Coordenador", 3),
    ("Mentor", 4),
    ("Membro", 4),
    ("Trainee", 5),
]

DIRETORIAS = [
    ("Presidência", 1),
    ("Projetos", 2),
    ("Capacitação", 3),
    ("Relacionamento", 4),
    ("Escola de Mentores", 5),
]

# foto: gera uma foto de exemplo. contato: False deixa o LinkedIn vazio.
# ativo: False marca um ex-membro (some da página Equipe). vinculos: (diretoria, cargo nela).
MEMBROS = [
    {
        "nome": "Helena Prado", "cargo": "Presidente",
        "foto": True, "contato": True,
        "vinculos": [("Presidência", "Presidente")],
        "trajetoria": [("2024.1", "Trainee"), ("2024.2", "Membro"), ("2025.2", "Diretora de Projetos"), ("2026.1", "Presidente")],
    },
    {
        "nome": "Rafael Moura", "cargo": "Vice-presidente",
        "foto": True, "contato": True,
        "vinculos": [("Presidência", "Vice-presidente")],
        "trajetoria": [("2023.2", "Trainee"), ("2024.1", "Membro"), ("2025.1", "Coordenador"), ("2026.1", "Vice-presidente")],
    },
    {
        "nome": "Camila Duarte", "cargo": "Diretor de Projetos",
        "foto": True, "contato": True,
        "vinculos": [("Projetos", "Diretora de Projetos")],
        "trajetoria": [("2024.2", "Trainee"), ("2025.1", "Membro"), ("2026.1", "Diretora de Projetos")],
    },
    {
        "nome": "Lucas Tavares", "cargo": "Diretor de Capacitação",
        "foto": True, "contato": True,
        "vinculos": [("Capacitação", "Diretor de Capacitação")],
        "trajetoria": [("2024.2", "Trainee"), ("2025.1", "Membro"), ("2026.1", "Diretor de Capacitação")],
    },
    {
        "nome": "Beatriz Salgado", "cargo": "Diretor de Relacionamento",
        "foto": False, "contato": True,
        "vinculos": [("Relacionamento", "Diretora de Relacionamento")],
        "trajetoria": [("2024.1", "Trainee"), ("2024.2", "Membro"), ("2026.1", "Diretora de Relacionamento")],
    },
    {
        "nome": "Thiago Marques", "cargo": "Coordenador",
        "foto": True, "contato": True,
        "vinculos": [("Projetos", "Coordenador de Projetos")],
        "trajetoria": [("2024.2", "Trainee"), ("2025.1", "Membro"), ("2026.1", "Coordenador")],
    },
    {
        # Em duas diretorias ao mesmo tempo, para testar o agrupamento da página Equipe.
        "nome": "Isabela Fontes", "cargo": "Mentor",
        "foto": True, "contato": True,
        "vinculos": [("Escola de Mentores", "Mentora"), ("Capacitação", "Instrutora de Case")],
        "trajetoria": [("2023.1", "Trainee"), ("2023.2", "Membro"), ("2024.2", "Presidente"), ("2025.2", "Mentora")],
    },
    {
        "nome": "Gabriel Ferraz", "cargo": "Membro",
        "foto": False, "contato": True,
        "vinculos": [("Projetos", "Analista de Projetos")],
        "trajetoria": [("2025.1", "Trainee"), ("2025.2", "Membro")],
    },
    {
        "nome": "Larissa Quintela", "cargo": "Membro",
        "foto": True, "contato": True,
        "vinculos": [("Relacionamento", "Analista de Relacionamento")],
        "trajetoria": [("2025.1", "Trainee"), ("2025.2", "Membro")],
    },
    {
        # Nome muito longo, para testar quebra de linha nos cards, no perfil e no admin.
        "nome": "Pedro Henrique Cavalcanti Albuquerque de Vasconcelos Neto", "cargo": "Membro",
        "foto": True, "contato": True,
        "vinculos": [("Capacitação", "Analista de Capacitação")],
        "trajetoria": [("2025.2", "Trainee"), ("2026.1", "Membro")],
    },
    {
        "nome": "Júlia Nogueira", "cargo": "Trainee",
        "foto": False, "contato": True,
        "vinculos": [],
        "trajetoria": [("2026.2", "Trainee")],
    },
    {
        # Sem foto, sem LinkedIn e sem trajetória: campos vazios.
        "nome": "Mateus Ribeiro", "cargo": "Trainee", "foto": False, "contato": False,
        "vinculos": [],
        "trajetoria": [],
    },
    {
        "nome": "Sofia Brandão", "cargo": "Trainee",
        "foto": True, "contato": True,
        "vinculos": [],
        "trajetoria": [("2026.2", "Trainee")],
    },
    {
        "nome": "Davi Lacerda", "cargo": "Membro",
        "foto": False, "contato": True,
        "vinculos": [("Projetos", "Analista de Projetos")],
        "trajetoria": [("2025.1", "Trainee"), ("2025.2", "Membro"), ("2026.1", "Membro")],
    },
    # Ex-membros: somem da página Equipe, mas o perfil e os cases antigos continuam.
    {
        "nome": "Carolina Mendonça", "cargo": "Mentor",
        "ativo": False, "foto": False, "contato": True,
        "vinculos": [],
        "trajetoria": [("2022.2", "Trainee"), ("2023.1", "Membro"), ("2024.1", "Presidente"), ("2024.2", "Mentora")],
    },
    {
        "nome": "Bruno Teixeira", "cargo": "Membro",
        "ativo": False, "foto": False, "contato": True,
        "vinculos": [],
        "trajetoria": [("2023.1", "Trainee"), ("2023.2", "Membro"), ("2024.2", "Membro")],
    },
]

CATEGORIAS_DE_PARCEIROS = [
    "Consultoria",
    "Educação e carreira",
    "Tecnologia e dados",
    "Finanças",
]

# logo: gera um logo de exemplo. site vazio e logo False testam o card com o mínimo.
PARCEIROS = [
    {"nome": "Atlas Estratégia", "categoria": "Consultoria", "logo": True, "site": "https://example.com/atlas", "ordem": 1,
     "descricao": "Consultoria de estratégia. Apoia o ICC com mentorias, simulados de case e conversas sobre carreira."},
    {
        # Descrição longa, para testar a quebra de linha dos cards.
        "nome": "Norte Advisors", "categoria": "Consultoria", "logo": True, "site": "https://example.com/norte", "ordem": 2,
        "descricao": "Consultoria focada em crescimento, go-to-market e diagnóstico competitivo. Participa das bancas de case, "
                     "propõe desafios reais para os projetos dos membros e recebe os grupos em visitas ao escritório, o que "
                     "torna este texto longo o bastante para testar como o card e a página do parceiro tratam descrições extensas.",
     },
    {"nome": "Prisma Analytics", "categoria": "Tecnologia e dados", "logo": True, "site": "https://example.com/prisma", "ordem": 3,
     "descricao": "Empresa de dados e pesquisa de mercado. Dá suporte analítico aos projetos e às trilhas de capacitação."},
    {"nome": "Vetor Carreiras", "categoria": "Educação e carreira", "logo": True, "site": "https://example.com/vetor", "ordem": 4,
     "descricao": "Plataforma de preparação profissional. Faz workshops de entrevista, currículo e fit interview."},
    {"nome": "Cobalto Capital", "categoria": "Finanças", "logo": True, "site": "https://example.com/cobalto", "ordem": 5,
     "descricao": "Gestora de investimentos. Recebe os membros para conversas sobre mercado financeiro."},
    {"nome": "Rota Logística", "categoria": "Tecnologia e dados", "logo": True, "site": "https://example.com/rota", "ordem": 6,
     "descricao": "Empresa de logística que propôs um desafio de otimização de rotas a um dos projetos."},
    # Sem site e sem logo: o card mostra só o nome. Sem projetos associados.
    {"nome": "Horizonte Educação", "categoria": "Educação e carreira", "logo": False, "site": "", "ordem": 7,
     "descricao": "Parceiro com informações mínimas, para testar o card sem logo, sem site e sem projetos."},
    # Oculto: aparece no admin, não no site.
    {"nome": "Antiga Parceira Ltda", "categoria": "Consultoria", "logo": False, "site": "https://example.com/antiga",
     "ordem": 8, "ativo": False,
     "descricao": "Parceria encerrada. Está com \"Exibir no site\" desmarcado."},
]

ESTATISTICAS = [
    ("40+", "membros ativos", 1),
    ("15+", "projetos e iniciativas", 2),
    ("8+", "parceiros e conexões", 3),
    ("5+", "anos de atuação", 4),
]

# Os quatro programas do ICC, com os nomes e as descrições reais. Subtítulo, tópicos,
# componentes e blocos de conteúdo são exemplos. selo "" deixa o card sem frequência;
# ativo False esconde do site.
PROGRAMAS = [
    {
        "slug": "jornada-do-consultor", "nome": "Jornada do Consultor", "ordem": 1, "icone": True,
        "subtitulo": "O primeiro semestre do membro na entidade",
        "descricao": "Programa que estrutura visitas, capacitações e cases ao longo do primeiro semestre do membro na entidade, "
                     "aproximando-o do ambiente e da prática de consultoria. A aprovação nesta etapa é condição para a "
                     "permanência do membro nos semestres seguintes.",
        "topicos": "Visitas a escritórios de consultoria\nCapacitações semanais\nCase final com banca\nAcompanhamento por mentores",
        "inscricao": "",
        "componentes": [
            ("Visitas corporativas", "Encontros em escritórios de consultoria parceiros, com conversas abertas com consultores."),
            ("Capacitações semanais", "Aulas práticas de estrutura de problemas, Excel, storytelling e comunicação executiva."),
            ("Case final", "Um desafio resolvido em grupo e apresentado a uma banca avaliadora de firmas parceiras."),
        ],
        "blocos": [
            ("Para quem é",
             "A Jornada do Consultor é a porta de entrada do ICC. Todo **trainee** passa por ela no primeiro semestre.\n\n"
             "- Visitas a escritórios de consultoria\n- Capacitações semanais em estrutura de problemas e Excel\n"
             "- Um case final, resolvido em grupo e apresentado a uma banca",
             "right", "Visita ao escritório de uma parceira"),
            ("Como funciona",
             "O semestre tem três fases. Nas primeiras semanas, os trainees conhecem o clube e as ferramentas básicas. "
             "No meio do semestre, as capacitações ficam mais práticas e os grupos de case são formados. No fim, cada grupo "
             "apresenta o seu case.\n\nCada grupo é acompanhado por um mentor, que dá retorno a cada entrega. "
             "Veja o [calendário completo](https://example.com/jornada/calendario) do semestre.",
             "left", "Capacitação semanal em sala"),
            ("Critério de aprovação",
             "A aprovação é condição para continuar no clube. O critério considera presença, entregas e a avaliação da banca do case final.",
             "center", "Banca avaliadora do case final"),
        ],
    },
    {
        "slug": "pedagogico", "nome": "Pedagógico", "ordem": 2, "icone": True,
        "subtitulo": "Preparação para os processos seletivos do mercado",
        "descricao": "Prática de resolução de cases e de processos seletivos, incluindo a vertente quantitativa. Prepara os "
                     "membros para as etapas mais exigidas pelas firmas de consultoria: GMAT, Verbal, Data e Fit Interview.",
        "topicos": "Case interview\nGMAT e raciocínio quantitativo\nVerbal\nData\nFit interview",
        "inscricao": "https://example.com/pedagogico/inscricao",
        "componentes": [
            ("Simulados de case", "Rodadas semanais de case interview, com retorno individual dos mentores."),
            ("Trilha quantitativa", "Treino de GMAT, estimativas e leitura de gráficos."),
            ("Fit interview", "Treino de perguntas comportamentais e construção de histórias pessoais."),
        ],
        "blocos": [
            ("O que se treina",
             "O Pedagógico cobre as quatro etapas que mais eliminam candidatos nos processos seletivos de consultoria:\n\n"
             "1. **GMAT** e raciocínio quantitativo\n2. **Verbal**\n3. **Data**\n4. **Fit interview**",
             "right", "Simulado de case em grupo"),
            ("Rotina semanal",
             "Os encontros são semanais e combinam teoria curta com muita prática. Cada membro acompanha o próprio progresso numa planilha de evolução.",
             "right", None),
        ],
    },
    {
        "slug": "escola-de-mentores", "nome": "Escola de Mentores", "ordem": 3, "icone": False,
        "subtitulo": "Formação de quem acompanha os trainees",
        "descricao": "Formação preparatória para os mentores que acompanham os grupos de trainees ao longo da Jornada do Consultor.",
        "topicos": "Como dar feedback\nLiderança de grupos\nAcompanhamento de cases",
        "inscricao": "",
        "componentes": [
            ("Formação de mentores", "Encontros mensais sobre feedback, escuta e condução de reuniões."),
            ("Acompanhamento de grupos", "Cada mentor acompanha um grupo de trainees durante o semestre."),
        ],
        "blocos": [
            ("Quem pode ser mentor",
             "Membros com pelo menos um semestre completo no ICC e aprovados na Jornada. A escolha considera disponibilidade e perfil.",
             "right", None),
        ],
    },
    {
        # Selo vazio: o card não mostra frequência.
        "slug": "departamento-de-alumni", "nome": "Departamento de Alumni", "ordem": 4, "icone": False,
        "subtitulo": "Preparação para ex-alunos do Insper",
        "descricao": "Programa voltado a ex-alunos do Insper que já se formaram, mas ainda buscam ingressar em grandes firmas de "
                     "consultoria, com preparação equivalente à oferecida aos membros, sem as obrigações do ciclo regular de trainee.",
        "topicos": "Preparação para processos seletivos\nMentoria com membros\nSimulados de case",
        "inscricao": "https://example.com/alumni/inscricao",
        "componentes": [
            ("Preparação para processos seletivos", "Trilha equivalente à dos membros, adaptada a quem já se formou."),
            ("Mentoria com membros", "Conversas individuais com membros e ex-membros que passaram pelos processos."),
        ],
        "blocos": [
            ("Como participar",
             "As inscrições abrem uma vez por semestre, no mesmo calendário do processo seletivo do clube. "
             "Os candidatos preenchem o formulário e passam por uma conversa individual.",
             "right", None),
        ],
    },
    {
        # Oculto: aparece no admin, não no menu nem no site. Sem blocos e sem componentes.
        "slug": "programa-em-reformulacao", "nome": "Programa em reformulação", "ordem": 5, "icone": False,
        "subtitulo": "", "ativo": False,
        "descricao": "Programa com \"Exibir no site\" desmarcado: só aparece no admin.",
        "topicos": "", "inscricao": "",
        "componentes": [], "blocos": [],
    },
]

# (semestre, título, área, tema, banca, premiação, link, participantes)
# participantes: (nome do membro, papel, ordem). ativo False esconde o case do site.
CASES = [
    {"programa": "jornada-do-consultor", "semestre": "2026.1", "titulo": "1º Case", "area": "Varejo", "ordem": 1,
     "tema": "Como uma rede de supermercados regional deve responder à entrada de um grande concorrente nacional?",
     "banca": "Atlas Estratégia\nNorte Advisors", "premiacao": "1º lugar", "link": "https://example.com/cases/2026-1-varejo",
     "participantes": [("Júlia Nogueira", "integrante", 1), ("Sofia Brandão", "integrante", 2),
                       ("Pedro Henrique Cavalcanti Albuquerque de Vasconcelos Neto", "integrante", 3), ("Isabela Fontes", "mentor", 1)]},
    {"programa": "jornada-do-consultor", "semestre": "2026.1", "titulo": "2º Case", "area": "Saúde", "ordem": 2,
     "tema": "Expansão de uma rede de clínicas populares para o interior de São Paulo.",
     "banca": "Atlas Estratégia", "premiacao": "", "link": "",
     "participantes": [("Mateus Ribeiro", "integrante", 1), ("Davi Lacerda", "integrante", 2), ("Isabela Fontes", "mentor", 1)]},
    {"programa": "jornada-do-consultor", "semestre": "2025.2", "titulo": "", "area": "Educação", "ordem": 1,
     "tema": "Modelo de precificação para uma plataforma de cursos online voltada a quem presta concurso.",
     "banca": "Norte Advisors\nPrisma Analytics\nVetor Carreiras", "premiacao": "Menção honrosa",
     "link": "https://example.com/cases/2025-2-educacao",
     "participantes": [("Gabriel Ferraz", "integrante", 1), ("Larissa Quintela", "integrante", 2),
                       ("Carolina Mendonça", "mentor", 1), ("Isabela Fontes", "mentor", 2)]},
    {"programa": "jornada-do-consultor", "semestre": "2025.1", "titulo": "", "area": "Tecnologia", "ordem": 1,
     "tema": "Estratégia de entrada de uma fintech no mercado de crédito para pequenas empresas.",
     "banca": "Cobalto Capital", "premiacao": "1º lugar", "link": "",
     "participantes": [("Bruno Teixeira", "integrante", 1), ("Davi Lacerda", "integrante", 2), ("Carolina Mendonça", "mentor", 1)]},
    {"programa": "pedagogico", "semestre": "2026.1", "titulo": "", "area": "Logística", "ordem": 1,
     "tema": "Redução do custo de entrega de última milha numa operação de e-commerce.",
     "banca": "Rota Logística", "premiacao": "", "link": "",
     "participantes": [("Lucas Tavares", "integrante", 1), ("Thiago Marques", "integrante", 2)]},
    # Oculto: aparece no admin, não no site.
    {"programa": "jornada-do-consultor", "semestre": "2024.2", "titulo": "", "area": "Energia", "ordem": 1, "ativo": False,
     "tema": "Case escondido: está com \"Exibir no site\" desmarcado.", "banca": "", "premiacao": "", "link": "",
     "participantes": [("Helena Prado", "integrante", 1)]},
]

# Projetos. fim None é projeto em andamento. fim igual ao início é um evento de um dia só.
# ativo False arquiva. programa None deixa o projeto fora de qualquer programa ("Outros projetos").
# imagens: legendas das fotos. eventos: (data, título, descrição, ordem). blocos: (título, texto, posição, legenda da imagem).
PROJETOS = [
    {
        "titulo": "Diagnóstico de crescimento para marketplace B2B", "programa": "jornada-do-consultor",
        "inicio": date(2025, 3, 3), "fim": date(2025, 5, 30),
        "descricao": "Análise de funil, entrevistas com usuários e recomendações de priorização comercial.",
        "parceiros": ["Atlas Estratégia", "Prisma Analytics"],
        "membros": ["Helena Prado", "Camila Duarte", "Gabriel Ferraz", "Bruno Teixeira"],
        "imagens": ["Equipe no kickoff", "Oficina de priorização", "Entrega final ao cliente"],
        "eventos": [(date(2025, 3, 3), "Kickoff", "Alinhamento de escopo, objetivos e hipóteses iniciais.", 1),
                    (date(2025, 4, 10), "Análise intermediária", "Validação de dados, benchmark e entrevistas.", 2),
                    (date(2025, 5, 30), "Entrega final", "Apresentação executiva com recomendações priorizadas.", 3)],
        "blocos": [("Contexto", "O time estruturou um diagnóstico de crescimento para identificar gargalos de conversão e oportunidades comerciais.", "right", None),
                   ("Método", "Foram feitas 12 entrevistas com compradores e vendedores, além da análise do funil dos últimos dois anos.", "left", "Mapa do funil comercial"),
                   ("Resultado", "A entrega final consolidou hipóteses, critérios de priorização e próximos passos para execução.", "center", "Matriz de priorização")],
    },
    {
        "titulo": "Estratégia de entrada em novo mercado", "programa": "jornada-do-consultor",
        "inicio": date(2026, 8, 17), "fim": None,
        "descricao": "Dimensionamento de mercado, análise competitiva e recomendação de rota de entrada. Projeto em andamento, sem data de conclusão.",
        "parceiros": ["Norte Advisors"],
        "membros": ["Camila Duarte", "Thiago Marques", "Davi Lacerda"],
        "imagens": ["Sprint de pesquisa"],
        "eventos": [(date(2026, 8, 17), "Kickoff", "Definição das perguntas-chave e do plano de análise.", 1),
                    (date(2026, 9, 21), "Sprint de pesquisa", "Mapeamento de concorrentes, preços e canais.", 2)],
        "blocos": [("Abordagem", "A equipe combinou pesquisa secundária, benchmarks e entrevistas exploratórias para orientar a recomendação.", "right", None)],
    },
    {
        "titulo": "Plano de expansão para rede de clínicas populares", "programa": "pedagogico",
        "inicio": date(2024, 9, 2), "fim": date(2024, 12, 6),
        "descricao": "Projeto concluído com três parceiros e sem imagens, para testar a página sem galeria.",
        "parceiros": ["Atlas Estratégia", "Norte Advisors", "Vetor Carreiras"],
        "membros": ["Rafael Moura", "Beatriz Salgado"],
        "imagens": [],
        "eventos": [(date(2024, 9, 2), "Kickoff", "", 1),
                    (date(2024, 12, 6), "Entrega final", "Plano de expansão com cronograma de três anos.", 2)],
        "blocos": [("", "Bloco sem título, só com texto: testa o layout quando o bloco não tem cabeçalho.", "right", None),
                   ("Recomendação", "Abrir cinco unidades em dois anos, começando pelas cidades com maior densidade de planos populares.", "right", None)],
    },
    {
        "titulo": "Otimização de rotas de entrega", "programa": "departamento-de-alumni",
        "inicio": date(2026, 2, 9), "fim": date(2026, 6, 26),
        "descricao": "Projeto de um grupo de alumni para uma empresa de logística, com modelagem de rotas e simulação de custos.",
        "parceiros": ["Rota Logística", "Prisma Analytics"],
        "membros": ["Lucas Tavares", "Larissa Quintela"],
        "imagens": [],
        "eventos": [(date(2026, 2, 9), "Kickoff", "Entendimento da operação e coleta de dados.", 1),
                    (date(2026, 6, 26), "Entrega final", "", 2)],
        "blocos": [],
    },
    {
        # Evento de um dia: a página mostra a data uma vez só. Sem programa: aparece em "Outros projetos".
        "titulo": "Visita técnica a uma consultoria parceira", "programa": None,
        "inicio": date(2026, 5, 14), "fim": date(2026, 5, 14),
        "descricao": "Visita de um dia ao escritório de uma consultoria parceira, com palestra e conversa com os consultores.",
        "parceiros": ["Atlas Estratégia"],
        "membros": ["Rafael Moura", "Júlia Nogueira", "Sofia Brandão"],
        "imagens": [], "eventos": [], "blocos": [],
    },
    {
        # Sem parceiros, sem programa, sem membros, sem cronograma e sem blocos: todas as seções vazias.
        "titulo": "Projeto mínimo, sem parceiros nem programa", "programa": None,
        "inicio": date(2026, 9, 7), "fim": None,
        "descricao": "Testa todas as seções vazias da página de projeto.",
        "parceiros": [], "membros": [], "imagens": [], "eventos": [], "blocos": [],
    },
    {
        # Arquivado: some do site e da API, continua no admin.
        "titulo": "Projeto piloto descontinuado", "programa": "jornada-do-consultor",
        "inicio": date(2024, 2, 5), "fim": date(2024, 6, 14), "ativo": False,
        "descricao": "Está com \"Ativo\" desmarcado: some do site, mas continua guardado.",
        "parceiros": ["Atlas Estratégia"], "membros": ["Helena Prado"],
        "imagens": [], "eventos": [], "blocos": [],
    },
]

TEXTO_LONGO_DO_ARTIGO = (
    "## Contexto\n\n"
    "A precificação dinâmica deixou de ser exclusividade do e-commerce. **Redes físicas** passaram a ajustar preços por "
    "região, horário e estoque, com ganhos de margem entre 2% e 5%.\n\n"
    "![](imagem-1)\n\n"
    "## Metodologia\n\n"
    "O estudo combinou entrevistas e dados públicos de três redes varejistas:\n\n"
    "- Rede A: 120 lojas, foco em alimentos\n- Rede B: 45 lojas, foco em eletrônicos\n- Rede C: 300 lojas, formato de proximidade\n\n"
    "A elasticidade da demanda foi estimada por\n\n$$\\varepsilon = \\frac{\\Delta Q / Q}{\\Delta P / P}$$\n\n"
    "## Resultados\n\n"
    "As redes que automatizaram a revisão semanal de preços reduziram a ruptura de estoque. Mais detalhes no "
    "[relatório completo](https://example.com/relatorio).\n\n"
    "![](imagem-2)\n\n"
    "## Recomendações\n\n"
    "Começar por categorias de alto giro, medir a elasticidade antes de automatizar e manter uma regra de teto para evitar "
    "reações negativas dos clientes."
)

# imagens: legendas das figuras do texto, na ordem 1, 2, ... capa False deixa o artigo sem imagem de capa.
# publicado False é rascunho. data None deixa o artigo sem data.
CONTEUDO_DE_FORMATACAO = r"""## Visão geral

Este artigo existe só para testar **todos** os recursos de formatação do editor e do site: *itálico*, **negrito**, ~~tachado~~, `código no meio da frase`, [um link externo](https://example.com) e acentuação completa: ação, coração, ônibus, pingüim.

> "Uma citação em destaque: o texto aparece recuado e com uma barra ao lado."

### Listas

- Primeiro item
- Segundo item, com **negrito**
- Terceiro item

1. Passo um
2. Passo dois
3. Passo três

#### Subsubseção

Um parágrafo dentro de uma subsubseção, para ver os três níveis de título lado a lado.

---

## Tabela

| Matriz | Quando usar | Custo |
|---|---|---|
| Impacto x esforço | Primeira triagem | Baixo |
| Custo do atraso | Projetos com prazo | Médio |
| Atratividade x capacidade | Portfólio de iniciativas | Alto |

## Fórmulas

Em linha, o retorno é $$ROI = \frac{ganho - custo}{custo}$$ e o valor presente de um fluxo é $$VP = \sum_{t=1}^{n} \frac{F_t}{(1+i)^t}$$.

Em bloco próprio:

$$
\text{Margem} = \frac{\text{Receita} - \text{Custos variáveis}}{\text{Receita}} \times 100\%
$$

O cifrão sozinho não vira fórmula: o projeto custou R$ 10 mi e rendeu R$ 20 mi.

## Código

Uma chamada no meio da frase, como `pandas.read_csv()`, e agora um bloco de várias linhas:

```python
import pandas as pd

vendas = pd.read_csv("vendas.csv")
por_regiao = vendas.groupby("regiao")["receita"].sum()
print(por_regiao.sort_values(ascending=False).head(5))
```

E outro, em SQL, com uma linha bem longa para testar a rolagem horizontal:

```sql
SELECT regiao, SUM(receita) AS receita_total, COUNT(DISTINCT cliente_id) AS clientes_ativos, AVG(ticket_medio) AS ticket FROM vendas WHERE data >= '2026-01-01' GROUP BY regiao ORDER BY receita_total DESC;
```

## Imagens

A primeira imagem usa a legenda cadastrada:

![](imagem-1)

A segunda troca a legenda só neste ponto:

![Legenda escrita entre os colchetes, só aqui](imagem-2)

Uma imagem que não existe é omitida em vez de aparecer quebrada: ![](imagem-9)

## HTML não é executado

<script>alert("isto aparece como texto, não roda")</script>

Fim do artigo de teste."""

ARTIGOS = [
    {"titulo": "Precificação dinâmica no varejo brasileiro: um estudo de caso", "slug": "precificacao-dinamica-no-varejo",
     "autores": ["Helena Prado", "Camila Duarte", "Robert {Lucas Jr}"], "temas": "Varejo, Precificação", "data": date(2026, 3, 12), "ordem": 1,
     "resumo": "Análise de estratégias de precificação em redes varejistas e do impacto delas na margem.",
     "conteudo": TEXTO_LONGO_DO_ARTIGO,
     "capa": True, "imagens": ["Margem por formato de loja", "Ruptura de estoque antes e depois da automação"], "publicado": True},
    {"titulo": "Transformação digital em PMEs: barreiras e alavancas", "slug": "",
     "autores": ["Thiago Marques", "Maria da Silva"], "temas": "Tecnologia, PMEs", "data": date(2026, 4, 8), "ordem": 2,
     "resumo": "Levantamento com pequenas e médias empresas sobre a adoção de tecnologia. Artigo sem slug, aberto pelo número.",
     "conteudo": "O que trava a adoção de tecnologia em pequenas e médias empresas.\n\nAs alavancas que funcionaram nos casos analisados.",
     "capa": False, "imagens": [], "publicado": True},
    {"titulo": "Como escolher a ferramenta certa para priorizar projetos", "slug": "priorizacao-de-projetos",
     "autores": ["Lucas Tavares", "Beatriz Salgado", "Rafael Moura"], "temas": "Estratégia", "data": date(2026, 5, 20), "ordem": 3,
     "resumo": "Comparação de matrizes de priorização usadas em projetos de estratégia.",
     "conteudo": "## Matrizes mais usadas\n\nImpacto por esforço, atratividade por capacidade e custo do atraso.\n\n"
                 "| Matriz | Quando usar |\n|---|---|\n| Impacto x esforço | Primeira triagem |\n| Custo do atraso | Projetos com prazo |\n\n"
                 "![](imagem-1)\n\n## Quando usar cada uma\n\nCada matriz responde a uma pergunta diferente.",
     "capa": True, "imagens": ["Matriz de impacto por esforço"], "publicado": True},
    {
        "titulo": "Entrevista com uma mentora do ICC", "slug": "entrevista-com-uma-mentora",
        "autores": ["Beatriz Salgado"], "temas": "Carreira", "data": date(2026, 6, 2), "ordem": 4,
        "resumo": "Uma conversa sobre carreira em consultoria, com uma mentora do clube.",
        "conteudo": "Uma conversa com uma mentora do ICC sobre carreira em consultoria.",
     "capa": False, "imagens": [], "publicado": True,
    },
    {
        # Título muito longo, para testar a quebra no card, na página e na citação.
        "titulo": "Um título propositalmente muito longo para verificar como o card, a página do artigo e a citação lidam com "
                  "textos extensos que ocupam várias linhas em telas pequenas",
        "slug": "titulo-muito-longo", "autores": ["Pedro Henrique Cavalcanti Albuquerque de Vasconcelos Neto"],
        "temas": "Teste de layout, Textos longos, Quebra de linha", "data": date(2026, 6, 15), "ordem": 5,
        "resumo": "Artigo de teste para o layout.",
        "conteudo": "Texto curto de um artigo cujo único objetivo é ter um título muito longo.",
     "capa": True, "imagens": [], "publicado": True,
    },
    {
        # Mais antigo, com tabela e sem imagens.
        "titulo": "Estimativas de mercado em cinco passos", "slug": "estimativas-de-mercado",
        "autores": ["Rafael Moura"], "temas": "Case interview", "data": date(2025, 11, 3), "ordem": 6,
        "resumo": "Roteiro para estimar o tamanho de um mercado sem dados prontos.",
        "conteudo": "## Passo a passo\n\n1. Defina o mercado\n2. Segmente\n3. Estime cada segmento\n4. Some\n5. Teste a ordem de grandeza",
     "capa": False, "imagens": [], "publicado": True,
    },
    {
        # Artigo de teste de formatação: usa todos os recursos do editor e do site (títulos, listas, tabela, citação,
        # fórmulas, código, imagens, linha divisória, HTML como texto, nome de autor com chaves).
        "titulo": "Guia de formatação: todos os recursos do editor", "slug": "guia-de-formatacao",
        "autores": ["Robert {Lucas Jr}", "Rafael Moura"], "temas": "Teste de layout, Formatação",
        "data": date(2026, 6, 20), "ordem": 8,
        "resumo": "Artigo de teste com títulos, listas, tabela, citação, fórmulas, blocos de código e imagens.",
        "conteudo": CONTEUDO_DE_FORMATACAO,
        "capa": True, "imagens": ["Primeira imagem de teste", "Segunda imagem de teste"], "publicado": True,
    },
    {
        # Rascunho sem data: aparece no admin, não no site nem na API.
        "titulo": "Rascunho ainda não publicado", "slug": "rascunho-nao-publicado",
        "autores": ["Mateus Ribeiro"], "temas": "Rascunho", "data": date(2026, 7, 1), "ordem": 9,
        "resumo": "Está com \"Publicado\" desmarcado: aparece no admin, mas não no site.",
        "conteudo": "Texto em construção.",
     "capa": False, "imagens": [], "publicado": False,
    },
]

# Processos seletivos: o antigo é criado primeiro, porque ativar um processo desativa os outros.
PROCESSOS = [
    {
        "titulo": "Processo Seletivo ICC 2026.1", "ativo": False, "abertas": False, "link": "",
        "datas": [("Inscrição", "9 a 20 de fevereiro", 1), ("Dinâmica em grupo", "Semana de 23 de fevereiro", 2),
                  ("Entrevista individual", "Semana de 2 de março", 3), ("Resultado", "Até 13 de março", 4)],
        "etapas": [("01", "Inscrição", "Envio de dados e das respostas iniciais.", "15 minutos", "", 1, False),
                   ("02", "Dinâmica", "Resolução em grupo de um pequeno case.", "60 minutos", "Escute o grupo\nEstruture hipóteses", 2, False)],
        "requisitos": [("Ser aluno de graduação do Insper.", 1, False)],
        "materiais": [],
    },
    {
        "titulo": "Processo Seletivo ICC 2026.2", "ativo": True, "abertas": True, "link": "https://example.com/inscricao-ps-2026-2",
        "datas": [("Inscrição", "17 a 28 de agosto", 1), ("Dinâmica em grupo", "Primeira semana de setembro", 2),
                  ("Entrevista individual", "Segunda semana de setembro", 3), ("Resultado", "Até 20 de setembro", 4)],
        "etapas": [
            ("01", "Inscrição", "Envio de dados, motivação e perguntas iniciais sobre o interesse em consultoria.", "15 minutos",
             "Revise sua motivação\nMostre clareza sobre o ICC\nExplique aprendizados relevantes", 1, True),
            ("02", "Dinâmica", "Resolução em grupo, para avaliar comunicação, colaboração e pensamento estruturado.", "60 minutos",
             "Escute o grupo\nEstruture hipóteses\nComunique a síntese", 2, True),
            # Sem ícone, para testar a etapa sem imagem.
            ("03", "Entrevista", "Conversa individual com perguntas de fit, experiências e motivação para a rotina do clube.", "30 minutos",
             "Prepare exemplos concretos\nMostre consistência\nSeja objetivo", 3, False),
            # Sem duração e sem dicas.
            ("04", "Resultado", "Retorno final e próximos passos para o onboarding e a trilha de formação.", "", "", 4, False),
        ],
        "requisitos": [("Ser aluno de graduação do Insper.", 1, True),
                       ("Ter disponibilidade para reuniões, treinamentos e projetos semanais.", 2, False),
                       ("Demonstrar interesse por consultoria, estratégia e resolução de problemas.", 3, False)],
        "materiais": [("Materiais para case interview", ["Livro de case interview para iniciantes", "Casos resolvidos do próprio ICC", "Simulados internos"], 1),
                      ("Preparação para fit interview", ["Mapeie as suas experiências relevantes", "Prepare a motivação para consultoria", "Treine respostas objetivas"], 2)],
    },
]

# Itens de menu a mais que o padrão (os padrões vêm da migration). area "rodape" aparece só no rodapé;
# um item inativo fica fora do site.
ITENS_DE_MENU = [
    {"texto": "Código no GitHub", "area": "rodape", "url": "https://github.com/insper-consulting-club", "ordem": 20, "ativo": True},
    {"texto": "Eventos (em breve)", "area": "menu", "url": "/eventos", "ordem": 21, "ativo": False},
]
