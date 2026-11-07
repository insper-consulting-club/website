from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


class Partner_Category(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'Categorias dos Parceiros'

    def __str__(self):
        return self.title


class Directorate(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nome')
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name = 'Diretoria'
        verbose_name_plural = 'Diretorias'
        ordering = ['order']

    def __str__(self):
        return self.name

    @property
    def slug(self):
        # Identificador das âncoras de /equipe. Derivado do nome, e não um
        # campo próprio, para que criar uma diretoria pelo admin não dependa
        # de alguém lembrar de preencher mais um campo.
        return slugify(self.name)


class Member_Position(models.Model):
    title = models.CharField(max_length=200, verbose_name='Cargo')
    power = models.IntegerField(
        verbose_name='Prioridade para exibição',
        help_text='0 = Presidência, 1 = Vice, 2 = Diretoria, 3 = Coordenação, '
                  '4 = Membro/Mentor, 5 = Trainee. Até 2 aparece na Home como liderança.'
    )

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

    def __str__(self):
        return self.title


class Partner(models.Model):
    logo_url = models.ImageField(upload_to='partners/', verbose_name='Logo')
    name = models.CharField(max_length=200, verbose_name='Nome')
    description = models.TextField(verbose_name='Descrição')
    category = models.ForeignKey(
        Partner_Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Categoria'
    )
    contato = models.CharField(max_length=20, blank=True)


    site = models.URLField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name='Site do parceiro'
    )
    is_active = models.BooleanField(
        default=True, verbose_name='Exibir no site',
        help_text='Desmarque para esconder do site sem apagar.'
    )
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name_plural = 'Parceiros'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def projects_count(self):
        return self.projects.filter(is_active=True).count()

    @property
    def success_cases_count(self):
        return self.projects.filter(is_active=True, end_date__isnull=False).count()


BADGE_CHOICES = [
    ('badge--continuo', 'Contínuo'),
    ('badge--semanal', 'Semanal'),
    ('badge--mensal', 'Mensal'),
    ('badge--semestral', 'Semestral'),
]

SEMESTER_CHOICES = [
    ('1', 'Primeiro Semestre'),
    ('2', 'Segundo Semestre'),
    ('both', 'Ambos'),
]

IMAGE_ALIGN_CHOICES = [
    ('right', 'Imagem à direita'),
    ('left', 'Imagem à esquerda'),
    ('center', 'Imagem centralizada (sem texto)'),
]


class ActivityCategory(models.Model):
    slug = models.SlugField(max_length=50, unique=True, verbose_name='Slug (identificador na URL)')
    label = models.CharField(max_length=200, verbose_name='Nome')
    subtitle = models.CharField(
        max_length=200, blank=True, verbose_name='Subtítulo',
        help_text='Uma linha descrevendo o formato do programa, exibida abaixo do nome.'
    )
    description = models.TextField(verbose_name='Descrição')
    highlights = models.TextField(verbose_name='Tópicos', blank=True, help_text='Um tópico por linha.')
    icon = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Ícone do card')
    badge = models.CharField(
        max_length=50, blank=True, verbose_name='Frequência (badge)',
        help_text='Opcional. Deixe vazio quando a categoria não tiver uma periodicidade definida.'
    )
    badge_class = models.CharField(max_length=50, choices=BADGE_CHOICES, verbose_name='Estilo do badge', default='badge--semanal')
    signup_url = models.URLField(
        max_length=300, blank=True, verbose_name='Link de inscrição',
        help_text='Preenchido apenas nos programas que têm formulário próprio de inscrição.'
    )
    is_active = models.BooleanField(
        default=True, verbose_name='Exibir no site',
        help_text='Desmarque para esconder do site sem apagar.'
    )
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name = 'Categoria de Atividade'
        verbose_name_plural = 'Categorias de Atividades'
        ordering = ['order']

    def __str__(self):
        return self.label

    def get_highlights_list(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]


class CalendarMonth(models.Model):
    month = models.CharField(max_length=50, verbose_name='Mês')
    year = models.IntegerField(
        null=True, blank=True, verbose_name='Ano',
        help_text='Necessário para o frontend desenhar a grade de dias da semana. Sem ano, só a lista de tópicos é exibida.',
    )
    items = models.TextField(
        verbose_name='Tópicos',
        help_text='Um tópico por linha. Para aparecer na grade de dias, use o formato "DD/MM - Título" (é o que import_calendar_ics gera).',
    )
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='both', verbose_name='Semestre')
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name = 'Mês do Calendário'
        verbose_name_plural = 'Calendário do Semestre'
        ordering = ['year', 'order']
        constraints = [
            models.UniqueConstraint(fields=['month', 'year'], name='unique_month_per_year'),
        ]

    def __str__(self):
        return f"{self.month}/{self.year}" if self.year else self.month

    def get_items_list(self):
        return [line.strip() for line in self.items.splitlines() if line.strip()]


class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descrição')
    category = models.ForeignKey(
        ActivityCategory, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Categoria', related_name='projects'
    )
    partners = models.ManyToManyField(Partner, blank=True, verbose_name='Parceiros envolvidos', related_name='projects')
    start_date = models.DateField(verbose_name='Data de início')
    end_date = models.DateField(null=True, blank=True, verbose_name='Data de conclusão')
    is_active = models.BooleanField(
        default=True, verbose_name='Ativo',
        help_text='Desmarque para arquivar o projeto: ele some do site, mas continua guardado.'
    )

    class Meta:
        verbose_name_plural = 'Projetos'
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images', verbose_name='Projeto')
    image = models.ImageField(upload_to='projects/images/', verbose_name='Imagem')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Legenda')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Imagem do Projeto'
        verbose_name_plural = 'Imagens do Projeto'
        ordering = ['order']

    def __str__(self):
        return f"Imagem {self.order} — {self.project.title}"


class ProjectTimelineEvent(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timeline_events', verbose_name='Projeto')
    date = models.DateField(verbose_name='Data')
    title = models.CharField(max_length=200, verbose_name='Título do evento')
    description = models.TextField(blank=True, verbose_name='Descrição')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Evento do Cronograma'
        verbose_name_plural = 'Eventos do Cronograma'
        ordering = ['date', 'order']

    def __str__(self):
        return f"{self.date} — {self.title}"


class ProjectContentBlock(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='content_blocks', verbose_name='Projeto')
    title = models.CharField(max_length=200, blank=True, verbose_name='Título do bloco (opcional)')
    text = models.TextField(blank=True, verbose_name='Texto')
    image = models.ImageField(upload_to='projects/content/', null=True, blank=True, verbose_name='Imagem (opcional)')
    image_caption = models.CharField(max_length=200, blank=True, verbose_name='Legenda da imagem')
    image_align = models.CharField(max_length=10, choices=IMAGE_ALIGN_CHOICES, default='right', verbose_name='Posição da imagem')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Bloco de Conteúdo'
        verbose_name_plural = 'Blocos de Conteúdo'
        ordering = ['order']

    def __str__(self):
        return f"Bloco {self.order} — {self.project.title}"


class Team_Member(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nome')
    photo = models.ImageField(upload_to='team/', null=True, blank=True, verbose_name='Foto')
    biography = models.TextField(max_length=200, blank=True, verbose_name='Biografia')
    position = models.ForeignKey(Member_Position, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Cargo principal')
    course = models.CharField(max_length=200, null=True, blank=True, verbose_name='Curso')
    year = models.CharField(max_length=50, null=True, blank=True, verbose_name='Período')
    hours = models.IntegerField(null=True, blank=True, verbose_name='Horas dedicadas')
    entry_date = models.DateField(verbose_name='Data de entrada')
    exit_date = models.DateField(
        null=True, blank=True, verbose_name='Data de saída',
        help_text='Preencha quando a pessoa sair do clube: ela some da página Equipe, '
                  'mas o histórico (cases, trajetória) continua guardado.'
    )
    email = models.EmailField(null=True, blank=True, verbose_name='Email')
    linkedin = models.URLField(null=True, blank=True, verbose_name='LinkedIn')
    trajetoria = models.JSONField(
        default=list, blank=True, verbose_name='Trajetória',
        help_text='Lista de {"semestre": "2026.1", "cargo": "Trainee"}, mais recente por último.'
    )
    projects = models.ManyToManyField(Project, blank=True, verbose_name='Projetos participados', related_name='members')

    class Meta:
        verbose_name = 'Membro'
        verbose_name_plural = 'Membros'

    def __str__(self):
        return self.name

    @property
    def number_of_projects(self):
        return self.projects.filter(is_active=True).count()


class DirectorateMembership(models.Model):
    """
    Vincula um membro a uma diretoria com o cargo específico que ele tem
    nela. Existe como model à parte (em vez de M2M direto ou FK único em
    Team_Member) porque uma pessoa pode estar em mais de uma diretoria ao
    mesmo tempo com cargos diferentes em cada uma (ex: Diretora de
    Pedagógico e, também, Mentora na Escola de Mentores).
    """
    member = models.ForeignKey(Team_Member, on_delete=models.CASCADE, related_name='directorate_memberships')
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE, related_name='memberships')
    cargo = models.CharField(max_length=200, verbose_name='Cargo nessa diretoria')
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name = 'Vínculo com Diretoria'
        verbose_name_plural = 'Vínculos com Diretorias'
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['member', 'directorate'], name='unique_member_per_directorate'),
        ]

    def __str__(self):
        return f"{self.member.name} - {self.cargo} ({self.directorate.name})"


class Activity(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        ActivityCategory, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Categoria', related_name='activities'
    )
    responsible_partner = models.ForeignKey(Partner, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Atividades'

    def __str__(self):
        return self.title


class ActivityImage(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='images', verbose_name='Atividade')
    image = models.ImageField(upload_to='activities/images/', verbose_name='Imagem')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Legenda')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Imagem da Atividade'
        verbose_name_plural = 'Imagens da Atividade'
        ordering = ['order']

    def __str__(self):
        return f"Imagem {self.order} — {self.activity.title}"


class ActivityContentBlock(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='content_blocks', verbose_name='Atividade')
    title = models.CharField(max_length=200, blank=True, verbose_name='Título do bloco (opcional)')
    text = models.TextField(blank=True, verbose_name='Texto')
    image = models.ImageField(upload_to='activities/content/', null=True, blank=True, verbose_name='Imagem (opcional)')
    image_caption = models.CharField(max_length=200, blank=True, verbose_name='Legenda da imagem')
    image_align = models.CharField(max_length=10, choices=IMAGE_ALIGN_CHOICES, default='right', verbose_name='Posição da imagem')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Bloco de Conteúdo'
        verbose_name_plural = 'Blocos de Conteúdo'
        ordering = ['order']

    def __str__(self):
        return f"Bloco {self.order} — {self.activity.title}"


class Media(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título')
    slug = models.SlugField(
        max_length=200, unique=True, null=True, blank=True,
        verbose_name='Slug da URL',
        help_text='Opcional. Usado no link do artigo; se vazio, o site usa o ID.',
    )
    authors = models.CharField(
        max_length=300, blank=True, verbose_name='Autores',
        help_text='Separados por vírgula. Ex.: Ana Silva, João Souza.'
    )
    topics = models.CharField(
        max_length=200, blank=True, verbose_name='Temas',
        help_text='Separados por vírgula. Ex.: Estratégia, Varejo.'
    )
    description = models.TextField(verbose_name='Resumo', help_text='Aparece no card da lista e no topo da página do artigo.')
    content = models.TextField(
        blank=True, verbose_name='Texto do artigo',
        help_text='Texto completo, em Markdown: **negrito**, ## Título, - item de lista, [link](https://...). '
                  'Separe os parágrafos com uma linha em branco. Para pôr uma imagem, envie-a em "Imagens do artigo", '
                  'abaixo, e escreva aqui, numa linha sozinha, ![](imagem-1), trocando 1 pelo número da imagem.'
    )
    link = models.URLField(
        blank=True, verbose_name='Link externo (opcional)',
        help_text='PDF, LinkedIn ou revista onde o artigo também foi publicado.'
    )
    image = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name='Imagem de capa')
    source = models.CharField(
        max_length=200, blank=True, verbose_name='Publicação',
        help_text='Opcional: revista ou evento, se o artigo também saiu fora do site.'
    )
    date = models.DateField(null=True, blank=True, verbose_name='Data de publicação')
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')
    published = models.BooleanField(
        default=False, verbose_name='Publicado',
        help_text='Desmarcado, o artigo é um rascunho: fica salvo aqui, mas não aparece no site.'
    )

    class Meta:
        verbose_name = 'Artigo'
        verbose_name_plural = 'Artigos'
        ordering = ['-date', 'order']


    def __str__(self):
        return self.title


class ArticleImage(models.Model):
    """Imagem usada dentro do texto de um artigo.

    No texto, a imagem é chamada pelo número, como ![](imagem-1), e não pelo
    endereço: assim dá para escrever o texto e enviar as imagens de uma vez,
    sem salvar antes para descobrir o endereço gerado pelo Cloudinary.
    """
    article = models.ForeignKey(Media, on_delete=models.CASCADE, related_name='images', verbose_name='Artigo')
    number = models.PositiveIntegerField(
        verbose_name='Número',
        help_text='No texto, escreva ![](imagem-1) para a imagem de número 1.'
    )
    image = models.ImageField(upload_to='articles/', verbose_name='Imagem')
    caption = models.CharField(
        max_length=300, blank=True, verbose_name='Legenda',
        help_text='Aparece embaixo da imagem no artigo.'
    )

    class Meta:
        verbose_name = 'Imagem do artigo'
        verbose_name_plural = 'Imagens do artigo'
        ordering = ['number']
        constraints = [
            models.UniqueConstraint(fields=['article', 'number'], name='numero_unico_por_artigo'),
        ]

    def __str__(self):
        return f'imagem-{self.number}'


class Statistic(models.Model):
    value = models.CharField(max_length=50, verbose_name='Valor/Número')
    description = models.CharField(max_length=200, verbose_name='Descrição')
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name_plural = 'Estatísticas'
        ordering = ['order']

    def __str__(self):
        return f"{self.value} - {self.description}"


class Participant(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nome')
    email = models.EmailField(verbose_name='Email')
    course = models.CharField(max_length=200, verbose_name='Curso')
    semester = models.CharField(max_length=50, verbose_name='Semestre')
    reason = models.TextField(verbose_name='Por que quer entrar no ICC?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de inscrição')

    class Meta:
        verbose_name_plural = 'Participantes'

    def __str__(self):
        return self.name

class Contact(models.Model):

    class ContactType(models.TextChoices):
        ALUNO = 'aluno', 'Aluno do Insper'
        EMPRESA = 'empresa', 'Empresa / Parceiro'
        ALUMNI = 'alumni', 'Ex-aluno do ICC'
        IMPRENSA = 'imprensa', 'Imprensa'
        OUTRO = 'outro', 'Outro'

    name = models.CharField(max_length=200, verbose_name="Nome")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=200, verbose_name="Telefone")
    contact_type = models.CharField(
        max_length=10,
        choices=ContactType.choices
    )
    message = models.TextField(verbose_name="Mensagem", default="")

    class Meta:
        verbose_name_plural = "Pedidos de contato"

    def __str__(self):
        return f"{self.name} | {self.contact_type}"
    
class SelectionProcess(models.Model):
    title = models.CharField(
        max_length=200,
        default="Próximo Processo Seletivo",
        verbose_name="Título"
    )
    is_active = models.BooleanField(
        default=True, verbose_name='Ativo',
        help_text='Só um processo aparece no site por vez. Ativar este desativa os outros.'
    )


    registrations_open = models.BooleanField(
        default=False, verbose_name='Inscrições abertas',
        help_text='Marque quando o PS abrir. Desmarcado, o site mostra "inscrições encerradas" e não leva a nenhum formulário.'
    )
    registration_url = models.URLField(
        max_length=300, blank=True, verbose_name='Link de inscrição',
        help_text='Formulário de inscrição (Google Forms). Só aparece no site com as inscrições abertas.'
    )
    
    class Meta:
        verbose_name = "Processo Seletivo"
        verbose_name_plural = "Processos Seletivos"
    
    def __str__(self):
        return self.title
    
    def clean(self):
        if self.registrations_open and not self.registration_url:
            raise ValidationError({'registration_url': 'Informe o link para abrir as inscrições.'})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Só um processo aparece no site; ativar este desativa os demais.
        if self.is_active:
            SelectionProcess.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)


    

class SelectionProcessStage(models.Model):
    process = models.ForeignKey(
        SelectionProcess, 
        on_delete=models.CASCADE, 
        related_name='stages', 
        verbose_name='Processo Seletivo'
        )
    label = models.CharField(max_length=200, verbose_name="Nome da etapa")
    date = models.CharField(max_length=200, verbose_name="Data/Período")
    order = models.IntegerField(default=0, verbose_name="Ordem")
    
    class Meta:
        verbose_name = "Data do Processo"
        verbose_name_plural = "Datas do Processo"
        ordering = ['order']
        
    def __str__(self):
        return f"{self.label} - {self.date}"

class SelectionProcessStep(models.Model):
    process = models.ForeignKey(
        SelectionProcess,
        on_delete=models.CASCADE, 
        related_name='steps', 
        verbose_name='Processo Seletivo'
    )
    number = models.CharField(max_length=10, verbose_name='Número')
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descrição')
    image = models.ImageField(upload_to='process/steps/', null=True, blank=True, verbose_name='Ícone do quadrado')
    duration = models.CharField(max_length=100, blank=True, verbose_name='Duração')
    tips = models.TextField(blank=True, verbose_name='Dicas', help_text='Um tópico por linha.')
    order = models.IntegerField(default=0, verbose_name='Ordem')
    
    class Meta:
        verbose_name = 'Etapa Detalhada'
        verbose_name_plural = 'Etapas Detalhadas'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.number}. {self.title}"
    
    def get_tips_list(self):
        return [line.strip() for line in self.tips.splitlines() if line.strip()]


class SelectionProcessRequirement(models.Model):
    process = models.ForeignKey(SelectionProcess, on_delete=models.CASCADE, related_name='requirements', verbose_name='Processo Seletivo')
    text = models.CharField(max_length=300, verbose_name='Texto do requisito')
    icon = models.ImageField(upload_to='process/requirements/', null=True, blank=True, verbose_name='Ícone (imagem)')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Requisito'
        verbose_name_plural = 'Requisitos'
        ordering = ['order']
    
    def __str__(self):
        return self.text
    

class PreparationMaterial(models.Model):
    process = models.ForeignKey(
        SelectionProcess, 
        on_delete=models.CASCADE,
        related_name='materials',
        verbose_name='Processo Seletivo'
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    order = models.IntegerField(default=0, verbose_name='Ordem')
    
    class Meta:
        verbose_name = 'Material de Preparação'
        verbose_name_plural = 'Materiais de Preparação'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class PreparationMaterialItem(models.Model):
    """
    Item de um material de preparação.
    Ex: Victor Cheng - Case Interview Secrets
    """
    material = models.ForeignKey(
        PreparationMaterial,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Material'
    )
    text = models.CharField(max_length=300, verbose_name='Texto')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        ordering = ['order']

    def __str__(self):
        return self.text

class SuccessCase(models.Model):
    """
    Case resolvido por um grupo de membros dentro de um programa.
    Ex: o case final da Jornada do Consultor de 2025.1.
    """
    category = models.ForeignKey(
        ActivityCategory,
        on_delete=models.CASCADE,
        related_name='success_cases',
        verbose_name='Programa'
    )
    semester = models.CharField(max_length=10, verbose_name='Semestre', help_text='No formato AAAA.S, por exemplo 2025.1.')
    title = models.CharField(
        max_length=100, blank=True, verbose_name='Título',
        help_text='Só é necessário quando o semestre tem mais de um case, por exemplo "1º Case".'
    )
    area = models.CharField(max_length=200, verbose_name='Área')
    theme = models.TextField(verbose_name='Tema')
    panel = models.TextField(
        blank=True, verbose_name='Banca avaliadora',
        help_text='Uma firma por linha.'
    )
    award = models.CharField(max_length=300, blank=True, verbose_name='Premiação')
    publication_url = models.URLField(max_length=300, blank=True, verbose_name='Link da publicação')
    is_active = models.BooleanField(
        default=True, verbose_name='Exibir no site',
        help_text='Desmarque para esconder do site sem apagar.'
    )
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name = 'Case de Sucesso'
        verbose_name_plural = 'Cases de Sucesso'
        ordering = ['-semester', 'order']

    def __str__(self):
        return f"{self.semester} {self.title}".strip() + f" - {self.area}"

    def get_panel_list(self):
        return [line.strip() for line in self.panel.splitlines() if line.strip()]


class SuccessCaseParticipant(models.Model):
    """
    Participação de um membro num case, como integrante do grupo ou mentor.
    O vínculo é com o membro, e não com o nome escrito à mão, para que o
    LinkedIn exibido no case seja sempre o mesmo do perfil da pessoa.
    Quem já saiu do clube continua cadastrado com data de saída, o que o
    mantém fora da listagem da Equipe sem tirá-lo dos cases antigos.
    """
    class Role(models.TextChoices):
        INTEGRANTE = 'integrante', 'Integrante do grupo'
        MENTOR = 'mentor', 'Mentor'

    case = models.ForeignKey(
        SuccessCase,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Case'
    )
    member = models.ForeignKey(
        Team_Member,
        on_delete=models.PROTECT,
        related_name='success_cases',
        verbose_name='Membro'
    )
    role = models.CharField(
        max_length=12,
        choices=Role.choices,
        default=Role.INTEGRANTE,
        verbose_name='Papel'
    )
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name = 'Participante do Case'
        verbose_name_plural = 'Participantes do Case'
        ordering = ['role', 'order']
        constraints = [
            models.UniqueConstraint(fields=['case', 'member'], name='unique_member_per_case'),
        ]

    def __str__(self):
        return f"{self.member.name} ({self.get_role_display()})"
