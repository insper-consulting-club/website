from datetime import date

from django.core.management.base import BaseCommand

from website.models import (
    Activity,
    ActivityCategory,
    ActivityContentBlock,
    CalendarMonth,
    Media,
    Member_Position,
    Partner,
    Partner_Category,
    PreparationMaterial,
    PreparationMaterialItem,
    Project,
    ProjectContentBlock,
    ProjectTimelineEvent,
    SelectionProcess,
    SelectionProcessRequirement,
    SelectionProcessStage,
    SelectionProcessStep,
    Statistic,
    Team_Member,
)


POSITIONS = [
    ("Presidente", 0),
    ("Vice-presidente", 1),
    ("Diretor de Projetos", 2),
    ("Diretor de Capacitacao", 2),
    ("Diretor de Relacionamento", 2),
    ("Mentor", 3),
    ("Membro", 4),
    ("Trainee", 5),
]

MEMBERS = [
    {
        "name": "Ana Silva",
        "position": "Presidente",
        "biography": "Membro mock para ambiente local. Atua na lideranca e organizacao do ICC.",
        "course": "Administracao",
        "year": "5o semestre",
        "hours": 420,
        "entry_date": date(2024, 2, 1),
        "email": "ana.silva@al.insper.edu.br",
        "linkedin": "https://www.linkedin.com/",
    },
    {
        "name": "Bruno Costa",
        "position": "Diretor de Projetos",
        "biography": "Membro mock para ambiente local. Apoia a gestao de projetos e entregas.",
        "course": "Economia",
        "year": "6o semestre",
        "hours": 360,
        "entry_date": date(2024, 3, 15),
        "email": "bruno.costa@al.insper.edu.br",
        "linkedin": "https://www.linkedin.com/",
    },
    {
        "name": "Carla Mendes",
        "position": "Mentor",
        "biography": "Membro mock para ambiente local. Contribui com orientacao e acompanhamento.",
        "course": "Administracao",
        "year": "Alumni",
        "hours": 520,
        "entry_date": date(2023, 8, 10),
        "email": "carla.mendes@al.insper.edu.br",
        "linkedin": "https://www.linkedin.com/",
    },
    {
        "name": "Daniel Pereira",
        "position": "Membro",
        "biography": "Membro mock para ambiente local. Participa das atividades e projetos do ICC.",
        "course": "Engenharia",
        "year": "4o semestre",
        "hours": 180,
        "entry_date": date(2025, 2, 20),
        "email": "daniel.pereira@al.insper.edu.br",
        "linkedin": "https://www.linkedin.com/",
    },
    {
        "name": "Eduarda Lima",
        "position": "Trainee",
        "biography": "Membro mock para ambiente local. Participa do ciclo de formacao do ICC.",
        "course": "Administracao",
        "year": "2o semestre",
        "hours": 80,
        "entry_date": date(2025, 8, 5),
        "email": "eduarda.lima@al.insper.edu.br",
        "linkedin": "https://www.linkedin.com/",
    },
    {
        "name": "Felipe Rocha",
        "position": "Diretor de Capacitacao",
        "biography": "Membro mock para ambiente local. Conduz treinamentos de case, mercado e storytelling.",
        "course": "Economia",
        "year": "5o semestre",
        "hours": 310,
        "entry_date": date(2024, 8, 12),
        "email": "felipe.rocha@al.insper.edu.br",
        "linkedin": "https://www.linkedin.com/",
    },
    {
        "name": "Marina Torres",
        "position": "Diretor de Relacionamento",
        "biography": "Membro mock para ambiente local. Coordena contato com parceiros e eventos institucionais.",
        "course": "Administracao",
        "year": "6o semestre",
        "hours": 340,
        "entry_date": date(2024, 2, 19),
        "email": "marina.torres@al.insper.edu.br",
        "linkedin": "https://www.linkedin.com/",
    },
]

PARTNER_CATEGORIES = [
    "Consultoria",
    "Educacao e carreira",
    "Tecnologia e dados",
]

PARTNERS = [
    {
        "name": "Atlas Strategy",
        "category": "Consultoria",
        "description": "Parceiro mock para mentorias, simulados de case e conversas sobre carreira em estrategia.",
        "contato": "mock",
        "site": "https://example.com/atlas-strategy",
    },
    {
        "name": "Norte Advisors",
        "category": "Consultoria",
        "description": "Parceiro mock focado em desafios de crescimento, go-to-market e diagnostico competitivo.",
        "contato": "mock",
        "site": "https://example.com/norte-advisors",
    },
    {
        "name": "Prisma Analytics",
        "category": "Tecnologia e dados",
        "description": "Parceiro mock para trilhas de dados, pesquisa de mercado e suporte analitico aos projetos.",
        "contato": "mock",
        "site": "https://example.com/prisma-analytics",
    },
    {
        "name": "Vetor Carreiras",
        "category": "Educacao e carreira",
        "description": "Parceiro mock para workshops de entrevista, CV, fit interview e preparacao profissional.",
        "contato": "mock",
        "site": "https://example.com/vetor-carreiras",
    },
]

CATEGORIES = [
    {
        "slug": "projetos",
        "label": "Projetos de consultoria",
        "description": "Frente dedicada a diagnostico, estruturacao de problemas e recomendacoes praticas.",
        "highlights": "Diagnostico de negocio\nBenchmarking\nAnalise de mercado\nStorytelling executivo",
        "badge": "Continuo",
        "badge_class": "badge--continuo",
        "order": 1,
    },
    {
        "slug": "capacitacao",
        "label": "Capacitacao",
        "description": "Trilha de treinamento para cases, entrevistas, pensamento estruturado e comunicacao.",
        "highlights": "Case interview\nFit interview\nExcel e dados\nApresentacoes",
        "badge": "Semanal",
        "badge_class": "badge--semanal",
        "order": 2,
    },
    {
        "slug": "eventos",
        "label": "Eventos",
        "description": "Palestras, paineis e encontros com consultorias, alumni e liderancas de mercado.",
        "highlights": "Paineis de carreira\nWorkshops com parceiros\nEventos abertos\nBate-papos com alumni",
        "badge": "Mensal",
        "badge_class": "badge--mensal",
        "order": 3,
    },
    {
        "slug": "networking",
        "label": "Networking",
        "description": "Conexoes entre membros, ex-membros, empresas parceiras e comunidade Insper.",
        "highlights": "Comunidade de membros\nMentorias\nAlumni\nParceiros",
        "badge": "Semestral",
        "badge_class": "badge--semestral",
        "order": 4,
    },
]

CALENDAR = [
    ("Fevereiro", "Abertura do semestre\nOnboarding de novos membros\nKickoff da trilha de cases", "1", 1),
    ("Marco", "Treinamentos tecnicos\nDiagnostico dos projetos\nPrimeiro simulado de case", "1", 2),
    ("Abril", "Execucao de projetos\nPainel de carreira\nMentorias com alumni", "1", 3),
    ("Maio", "Sprint final de entregas\nWorkshop de apresentacao executiva", "1", 4),
    ("Agosto", "Processo seletivo\nOnboarding e integracao\nTrilha de fundamentos", "2", 5),
    ("Setembro", "Projetos e eventos com parceiros\nSimulados de entrevista\nRevisao de CV", "2", 6),
    ("Outubro", "Semana de consultoria\nPreparacao para processos seletivos\nBate-papo com alumni", "2", 7),
    ("Novembro", "Fechamento dos projetos\nRetrospectiva de membros\nPlanejamento do proximo ciclo", "2", 8),
]

STATISTICS = [
    ("40+", "membros ativos", 1),
    ("15+", "projetos e iniciativas", 2),
    ("8+", "parceiros e conexoes", 3),
    ("5+", "anos de atuacao", 4),
]

PROJECTS = [
    {
        "title": "Diagnostico de crescimento para marketplace B2B",
        "description": "Projeto mock com analise de funil, entrevistas com usuarios e recomendacoes de priorizacao comercial.",
        "category": "projetos",
        "partners": ["Atlas Strategy", "Prisma Analytics"],
        "start_date": date(2025, 3, 1),
        "end_date": date(2025, 5, 30),
        "events": [
            (date(2025, 3, 1), "Kickoff", "Alinhamento de escopo, objetivos e hipoteses iniciais.", 1),
            (date(2025, 4, 10), "Analise intermediaria", "Validacao de dados, benchmark e entrevistas.", 2),
            (date(2025, 5, 30), "Entrega final", "Apresentacao executiva com recomendacoes priorizadas.", 3),
        ],
        "content": [
            (
                "Contexto",
                "O time estruturou um diagnostico de crescimento para identificar gargalos de conversao e oportunidades comerciais.",
                1,
            ),
            (
                "Resultado",
                "A entrega final consolidou hipoteses, criterios de priorizacao e proximos passos para execucao.",
                2,
            ),
        ],
    },
    {
        "title": "Benchmarks para estrategia de entrada em mercado",
        "description": "Projeto mock focado em dimensionamento de mercado, analise competitiva e recomendacao de rota de entrada.",
        "category": "projetos",
        "partners": ["Norte Advisors"],
        "start_date": date(2025, 8, 15),
        "end_date": None,
        "events": [
            (date(2025, 8, 15), "Kickoff", "Definicao de perguntas-chave e plano de analise.", 1),
            (date(2025, 9, 20), "Sprint de pesquisa", "Mapeamento de concorrentes, precos e canais.", 2),
        ],
        "content": [
            (
                "Abordagem",
                "A equipe combinou pesquisa secundaria, benchmarks e entrevistas exploratorias para orientar a recomendacao.",
                1,
            ),
        ],
    },
]

ACTIVITIES = [
    {
        "title": "Workshop de Case Interview",
        "description": "Atividade mock com pratica de cases, comunicacao estruturada e feedback individual.",
        "category": "capacitacao",
        "partner": "Vetor Carreiras",
        "content": "Sessao voltada para alunos que querem entender como estruturar hipoteses, conduzir calculos e sintetizar recomendacoes.",
    },
    {
        "title": "Painel de carreiras em consultoria",
        "description": "Atividade mock com convidados de mercado e alumni discutindo trajetorias em estrategia.",
        "category": "eventos",
        "partner": "Atlas Strategy",
        "content": "Conversa sobre entrada no mercado, rotina de projetos e habilidades valorizadas em consultorias.",
    },
    {
        "title": "Treinamento de storytelling executivo",
        "description": "Atividade mock para melhorar apresentacoes, piramide logica e narrativa de recomendacoes.",
        "category": "capacitacao",
        "partner": None,
        "content": "Treinamento interno com exemplos de slides, mensagens-chave e revisao em grupo.",
    },
]

NEWS = [
    {
        "title": "[Exemplo] Precificacao dinamica no varejo brasileiro: um estudo de caso",
        "authors": "Autor Exemplo, Autora Exemplo",
        "topics": "Varejo, Precificacao",
        "description": "Resumo mock: analise de estrategias de precificacao em redes varejistas e impacto na margem.",
        "content": (
            "Paragrafo mock 1: contexto do varejo brasileiro e por que a precificacao dinamica ganhou espaco.\n\n"
            "Paragrafo mock 2: metodologia, com entrevistas e dados publicos de tres redes varejistas.\n\n"
            "Paragrafo mock 3: resultados e recomendacoes para empresas que querem adotar o modelo."
        ),
        "link": "https://example.com/artigo-exemplo-1",
        "source": "Revista Exemplo de Administracao",
        "date": date(2026, 3, 12),
        "order": 1,
    },
    {
        "title": "[Exemplo] Transformacao digital em PMEs: barreiras e alavancas",
        "authors": "Autora Exemplo",
        "topics": "Tecnologia, PMEs",
        "description": "Resumo mock: levantamento com pequenas e medias empresas sobre adocao de tecnologia.",
        "content": (
            "Paragrafo mock 1: o que trava a adocao de tecnologia em pequenas e medias empresas.\n\n"
            "Paragrafo mock 2: alavancas que funcionaram nos casos analisados."
        ),
        "link": "",
        "source": "",
        "date": date(2026, 4, 8),
        "order": 2,
    },
    {
        "title": "[Exemplo] Modelos de priorizacao de portfolio em consultoria",
        "authors": "Autor Exemplo, Autor Exemplo 2",
        "topics": "Estrategia",
        "description": "Resumo mock: comparacao de matrizes de priorizacao usadas em projetos de estrategia.",
        "content": (
            "Paragrafo mock 1: as matrizes de priorizacao mais usadas em projetos de estrategia.\n\n"
            "Paragrafo mock 2: quando cada uma funciona melhor.\n\n"
            "Paragrafo mock 3: um exemplo aplicado a um portfolio ficticio."
        ),
        "link": "",
        "source": "",
        "date": date(2026, 5, 20),
        "order": 3,
    },
]



class Command(BaseCommand):
    help = "Popula o banco local com dados mock completos para o site do ICC."

    def handle(self, *args, **options):
        positions = self._seed_positions()
        members = self._seed_members(positions)
        partner_categories = self._seed_partner_categories()
        partners = self._seed_partners(partner_categories)
        categories = self._seed_categories()
        self._seed_calendar()
        self._seed_statistics()
        projects = self._seed_projects(categories, partners, members)
        self._seed_activities(categories, partners)
        self._seed_news()
        self._seed_selection_process()

        self.stdout.write(
            self.style.SUCCESS(
                "Mock concluido: "
                f"{len(members)} membros, {len(partners)} parceiros, "
                f"{len(categories)} categorias e {len(projects)} projetos prontos."
            )
        )

    def _seed_positions(self):
        positions = {}
        for title, power in POSITIONS:
            position, _ = Member_Position.objects.update_or_create(
                title=title,
                defaults={"power": power},
            )
            positions[title] = position
        return positions

    def _seed_members(self, positions):
        members = {}
        for item in MEMBERS:
            member, _ = Team_Member.objects.update_or_create(
                name=item["name"],
                defaults={
                    "biography": item["biography"],
                    "position": positions[item["position"]],
                    "course": item["course"],
                    "year": item["year"],
                    "hours": item["hours"],
                    "entry_date": item["entry_date"],
                    "exit_date": None,
                    "email": item["email"],
                    "linkedin": item["linkedin"],
                },
            )
            members[item["name"]] = member
        return members

    def _seed_partner_categories(self):
        categories = {}
        for title in PARTNER_CATEGORIES:
            category, _ = Partner_Category.objects.get_or_create(title=title)
            categories[title] = category
        return categories

    def _seed_partners(self, partner_categories):
        partners = {}
        for item in PARTNERS:
            partner, _ = Partner.objects.update_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "category": partner_categories[item["category"]],
                    "contato": item["contato"],
                    "site": item["site"],
                    "logo_url": "",
                },
            )
            partners[item["name"]] = partner
        return partners

    def _seed_categories(self):
        categories = {}
        for item in CATEGORIES:
            category, _ = ActivityCategory.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "label": item["label"],
                    "description": item["description"],
                    "highlights": item["highlights"],
                    "badge": item["badge"],
                    "badge_class": item["badge_class"],
                    "order": item["order"],
                },
            )
            categories[item["slug"]] = category
        return categories

    def _seed_calendar(self):
        for month, items, semester, order in CALENDAR:
            CalendarMonth.objects.update_or_create(
                month=month,
                defaults={"items": items, "semester": semester, "order": order},
            )

    def _seed_statistics(self):
        for value, description, order in STATISTICS:
            Statistic.objects.update_or_create(
                description=description,
                defaults={"value": value, "order": order},
            )

    def _seed_projects(self, categories, partners, members):
        seeded_projects = {}
        project_members = list(members.values())[:4]
        for item in PROJECTS:
            project, _ = Project.objects.update_or_create(
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "category": categories[item["category"]],
                    "start_date": item["start_date"],
                    "end_date": item["end_date"],
                },
            )
            project.partners.set([partners[name] for name in item["partners"]])
            project.members.set(project_members)

            for event_date, title, description, order in item["events"]:
                ProjectTimelineEvent.objects.update_or_create(
                    project=project,
                    title=title,
                    defaults={
                        "date": event_date,
                        "description": description,
                        "order": order,
                    },
                )

            for title, text, order in item["content"]:
                ProjectContentBlock.objects.update_or_create(
                    project=project,
                    title=title,
                    defaults={
                        "text": text,
                        "image": None,
                        "image_caption": "",
                        "image_align": "right",
                        "order": order,
                    },
                )

            seeded_projects[item["title"]] = project

        return seeded_projects

    def _seed_activities(self, categories, partners):
        for item in ACTIVITIES:
            partner = partners.get(item["partner"]) if item["partner"] else None
            activity, _ = Activity.objects.update_or_create(
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "category": categories[item["category"]],
                    "responsible_partner": partner,
                },
            )
            ActivityContentBlock.objects.update_or_create(
                activity=activity,
                title="Resumo",
                defaults={
                    "text": item["content"],
                    "image": None,
                    "image_caption": "",
                    "image_align": "right",
                    "order": 1,
                },
            )

    def _seed_news(self):
        for item in NEWS:
            Media.objects.update_or_create(
                title=item["title"],
                defaults={
                    "description": item["description"],
                    "link": item["link"],
                    "image": None,
                    "source": item["source"],
                    "date": item["date"],
                    "order": item["order"],
                    "authors": item["authors"],
                    "topics": item["topics"],
                    "content": item["content"],
                },
            )

    def _seed_selection_process(self):
        has_active = SelectionProcess.objects.filter(is_active=True).exists()
        process, created = SelectionProcess.objects.get_or_create(
            title="Processo Seletivo ICC Mock 2026.2",
            defaults={"is_active": not has_active},
        )
        active_process_exists = SelectionProcess.objects.filter(is_active=True).exclude(pk=process.pk).exists()
        if not active_process_exists and not process.is_active:
            process.is_active = True
            process.save(update_fields=["is_active"])

        steps = [
            ("Inscricao", "18 a 29 de agosto", 1),
            ("Dinamica em grupo", "Primeira semana de setembro", 2),
            ("Entrevista individual", "Segunda semana de setembro", 3),
            ("Resultado", "Ate 20 de setembro", 4),
        ]
        for label, stage_date, order in steps:
            SelectionProcessStage.objects.update_or_create(
                process=process,
                label=label,
                defaults={"date": stage_date, "order": order},
            )

        detailed_steps = [
            (
                "01",
                "Inscricao",
                "Envio de dados, motivacao e perguntas iniciais sobre interesse em consultoria.",
                "15 minutos",
                "Revise sua motivacao\nMostre clareza sobre o ICC\nExplique aprendizados relevantes",
                1,
            ),
            (
                "02",
                "Dinamica",
                "Resolucao em grupo para avaliar comunicacao, colaboracao e pensamento estruturado.",
                "60 minutos",
                "Escute o grupo\nEstruture hipoteses\nComunique sintese",
                2,
            ),
            (
                "03",
                "Entrevista",
                "Conversa individual com perguntas de fit, experiencias e motivacao para a rotina do clube.",
                "30 minutos",
                "Prepare exemplos concretos\nMostre consistencia\nSeja objetivo",
                3,
            ),
            (
                "04",
                "Resultado",
                "Retorno final e proximos passos para onboarding e trilha de formacao.",
                "Ate 1 semana",
                "Acompanhe o e-mail\nConfirme disponibilidade\nPrepare-se para o onboarding",
                4,
            ),
        ]
        for number, title, description, duration, tips, order in detailed_steps:
            SelectionProcessStep.objects.update_or_create(
                process=process,
                number=number,
                defaults={
                    "title": title,
                    "description": description,
                    "duration": duration,
                    "tips": tips,
                    "order": order,
                },
            )

        requirements = [
            ("Ser aluno de graduacao do Insper.", 1),
            ("Ter disponibilidade para reunioes, treinamentos e projetos semanais.", 2),
            ("Demonstrar interesse por consultoria, estrategia e resolucao de problemas.", 3),
        ]
        for text, order in requirements:
            SelectionProcessRequirement.objects.update_or_create(
                process=process,
                text=text,
                defaults={"order": order},
            )

        materials = [
            ("Materiais para case interview", ["Victor Cheng - Case Interview Secrets", "Case in Point", "Simulados internos do ICC"], 1),
            ("Preparacao para fit interview", ["Mapeie experiencias relevantes", "Prepare motivacao para consultoria", "Treine respostas objetivas"], 2),
        ]
        for title, items, order in materials:
            material, _ = PreparationMaterial.objects.update_or_create(
                process=process,
                title=title,
                defaults={"order": order},
            )
            for item_order, text in enumerate(items, start=1):
                PreparationMaterialItem.objects.update_or_create(
                    material=material,
                    text=text,
                    defaults={"order": item_order},
                )
