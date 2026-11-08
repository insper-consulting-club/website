from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models, transaction
from django.utils.text import slugify

from .deploy_hook import dispara_deploy_do_frontend


class PartnerCategory(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        verbose_name = 'Categoria do parceiro'
        verbose_name_plural = 'Categorias dos parceiros'

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


class Position(models.Model):
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
        PartnerCategory,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='Categoria'
    )
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
        verbose_name = 'Parceiro'
        verbose_name_plural = 'Parceiros'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def projects_count(self):
        return self.projects.filter(is_active=True).count()

    @property
    def completed_projects_count(self):
        return self.projects.filter(is_active=True, end_date__isnull=False).count()


BADGE_CHOICES = [
    ('badge--continuo', 'Contínuo'),
    ('badge--semanal', 'Semanal'),
    ('badge--mensal', 'Mensal'),
    ('badge--semestral', 'Semestral'),
]

IMAGE_ALIGN_CHOICES = [
    ('right', 'Imagem à direita'),
    ('left', 'Imagem à esquerda'),
    ('center', 'Imagem centralizada (sem texto)'),
]


class Program(models.Model):
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
        help_text='Opcional. Deixe vazio quando o programa não tiver uma periodicidade definida.'
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
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'
        ordering = ['order']

    def __str__(self):
        return self.label

    def get_highlights_list(self):
        return [line.strip() for line in self.highlights.splitlines() if line.strip()]


class Project(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descrição')
    program = models.ForeignKey(
        Program, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Programa', related_name='projects'
    )
    partners = models.ManyToManyField(Partner, blank=True, verbose_name='Parceiros envolvidos', related_name='projects')
    start_date = models.DateField(verbose_name='Data de início')
    end_date = models.DateField(null=True, blank=True, verbose_name='Data de conclusão')
    is_active = models.BooleanField(
        default=True, verbose_name='Ativo',
        help_text='Desmarque para arquivar o projeto: ele some do site, mas continua guardado.'
    )

    class Meta:
        verbose_name = 'Projeto'
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
        verbose_name = 'Imagem do projeto'
        verbose_name_plural = 'Imagens do projeto'
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
        verbose_name = 'Evento do cronograma'
        verbose_name_plural = 'Eventos do cronograma'
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
        verbose_name = 'Bloco de conteúdo'
        verbose_name_plural = 'Blocos de conteúdo'
        ordering = ['order']

    def __str__(self):
        return f"Bloco {self.order} — {self.project.title}"


class Member(models.Model):
    name = models.CharField(max_length=200, verbose_name='Nome')
    photo = models.ImageField(upload_to='team/', null=True, blank=True, verbose_name='Foto')
    biography = models.TextField(max_length=200, blank=True, verbose_name='Biografia')
    position = models.ForeignKey(Position, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Cargo principal')
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
    projects = models.ManyToManyField(Project, blank=True, verbose_name='Projetos participados', related_name='members')

    class Meta:
        verbose_name = 'Membro'
        verbose_name_plural = 'Membros'

    def __str__(self):
        return self.name

    @property
    def number_of_projects(self):
        return self.projects.filter(is_active=True).count()


class MemberTrajectory(models.Model):
    """
    Uma etapa da trajetória de um membro no ICC: o cargo que teve em um semestre.
    Aparece, em ordem de semestre, no perfil público da pessoa.
    """
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='trajectory_steps', verbose_name='Membro')
    semester = models.CharField(
        max_length=10, verbose_name='Semestre',
        validators=[RegexValidator(r'^\d{4}\.[12]$', 'Use o formato AAAA.S, por exemplo 2026.1.')],
        help_text='No formato AAAA.S, por exemplo 2026.1.'
    )
    role = models.CharField(max_length=200, verbose_name='Cargo nesse semestre', help_text='Por exemplo: Trainee, Membro, Diretor de Projetos.')

    class Meta:
        verbose_name = 'Etapa da trajetória'
        verbose_name_plural = 'Trajetória'
        ordering = ['semester', 'id']
        constraints = [
            models.UniqueConstraint(fields=['member', 'semester', 'role'], name='unique_trajectory_step'),
        ]

    def __str__(self):
        return f"{self.semester} - {self.role}"


class DirectorateMembership(models.Model):
    """
    Vincula um membro a uma diretoria com o cargo específico que ele tem
    nela. Existe como model à parte (em vez de M2M direto ou FK único em
    Member) porque uma pessoa pode estar em mais de uma diretoria ao
    mesmo tempo com cargos diferentes em cada uma (ex: Diretora de
    Pedagógico e, também, Mentora na Escola de Mentores).
    """
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='directorate_memberships')
    directorate = models.ForeignKey(Directorate, on_delete=models.CASCADE, related_name='memberships')
    cargo = models.CharField(max_length=200, verbose_name='Cargo nessa diretoria')
    order = models.IntegerField(default=0, verbose_name='Ordem de exibição')

    class Meta:
        verbose_name = 'Vínculo com diretoria'
        verbose_name_plural = 'Vínculos com diretorias'
        ordering = ['order']
        constraints = [
            models.UniqueConstraint(fields=['member', 'directorate'], name='unique_member_per_directorate'),
        ]

    def __str__(self):
        return f"{self.member.name} - {self.cargo} ({self.directorate.name})"


class ProgramComponent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    program = models.ForeignKey(
        Program, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Programa', related_name='components'
    )

    class Meta:
        verbose_name = 'Componente do programa'
        verbose_name_plural = 'Componentes dos programas'

    def __str__(self):
        return self.title


class ProgramContentBlock(models.Model):
    """
    Bloco de texto da página de um programa. Cada programa tem uma estrutura
    própria (Jornada, Pedagógico, Escola de Mentores...), por isso os blocos
    são livres: quem edita escolhe os títulos e a ordem.
    """
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='content_blocks', verbose_name='Programa')
    title = models.CharField(max_length=200, blank=True, verbose_name='Título do bloco (opcional)')
    text = models.TextField(
        blank=True, verbose_name='Texto',
        help_text='Em Markdown: **negrito**, ## Subtítulo, - item de lista, [link](https://...). '
                  'Separe os parágrafos com uma linha em branco.'
    )
    image = models.ImageField(upload_to='programs/content/', null=True, blank=True, verbose_name='Imagem (opcional)')
    image_caption = models.CharField(max_length=200, blank=True, verbose_name='Legenda da imagem')
    image_align = models.CharField(max_length=10, choices=IMAGE_ALIGN_CHOICES, default='right', verbose_name='Posição da imagem')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Bloco de conteúdo'
        verbose_name_plural = 'Blocos de conteúdo'
        ordering = ['order']

    def __str__(self):
        return f"Bloco {self.order} — {self.program.label}"


class Article(models.Model):
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
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images', verbose_name='Artigo')
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
        verbose_name = 'Estatística'
        verbose_name_plural = 'Estatísticas'
        ordering = ['order']

    def __str__(self):
        return f"{self.value} - {self.description}"


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
        help_text='Marque quando o PS abrir. Desmarcado, o site mostra "inscrições encerradas" e o link do formulário fica escondido.'
    )
    registration_url = models.URLField(
        max_length=300, blank=True, verbose_name='Link de inscrição',
        help_text='Formulário de inscrição (Google Forms). Só aparece no site com as inscrições abertas.'
    )
    
    class Meta:
        verbose_name = "Processo seletivo"
        verbose_name_plural = "Processos seletivos"
    
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
        verbose_name = "Data do processo"
        verbose_name_plural = "Datas do processo"
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
        verbose_name = 'Etapa detalhada'
        verbose_name_plural = 'Etapas detalhadas'
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
        verbose_name = 'Material de preparação'
        verbose_name_plural = 'Materiais de preparação'
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

class ProgramCase(models.Model):
    """
    Case resolvido por um grupo de membros dentro de um programa.
    Ex: o case final da Jornada do Consultor de 2025.1.
    """
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='cases',
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
        verbose_name = 'Case do programa'
        verbose_name_plural = 'Cases dos programas'
        ordering = ['-semester', 'order']

    def __str__(self):
        return f"{self.semester} {self.title}".strip() + f" - {self.area}"

    def get_panel_list(self):
        return [line.strip() for line in self.panel.splitlines() if line.strip()]


class ProgramCaseParticipant(models.Model):
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
        ProgramCase,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name='Case'
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='program_cases',
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
        verbose_name = 'Participante do case'
        verbose_name_plural = 'Participantes do case'
        ordering = ['role', 'order']
        constraints = [
            models.UniqueConstraint(fields=['case', 'member'], name='unique_member_per_case'),
        ]

    def __str__(self):
        return f"{self.member.name} ({self.get_role_display()})"


class SiteConfig(models.Model):
    """
    Textos e contatos do site que ficam fora dos demais cadastros:
    a Home, o rodapé, a abertura de cada página, os canais de contato e a
    Política de Privacidade. Existe um único registro (pk=1), criado pela
    migration com os textos que o site já tinha.
    """
    # Campos que o frontend grava no HTML durante o build (ver CAMPOS_DO_HTML).
    site_name = models.CharField(
        max_length=100, default='Liga Insper Consulting Club', verbose_name='Nome do site',
        help_text='Aparece na aba do navegador, no rodapé e na prévia ao compartilhar o link.'
    )
    site_description = models.CharField(
        max_length=300,
        default='A Liga Insper Consulting Club é uma organização estudantil dedicada ao '
                'desenvolvimento de futuros consultores.',
        verbose_name='Descrição do site',
        help_text='Usada na prévia ao compartilhar o link e em páginas sem descrição própria.'
    )
    logo = models.ImageField(
        upload_to='site/', null=True, blank=True, verbose_name='Logo (versão clara)',
        help_text='Opcional. Versão clara, para fundo escuro, usada no topo, no rodapé e na Home. '
                  'Sem logo enviado, o site usa o logo original.'
    )
    favicon = models.ImageField(
        upload_to='site/', null=True, blank=True, verbose_name='Ícone da aba (favicon)',
        help_text='Opcional. Imagem quadrada em PNG, de preferência com 256 x 256 pixels. '
                  'Sem ícone enviado, o site usa o original.'
    )
    og_image = models.ImageField(
        upload_to='site/', null=True, blank=True, verbose_name='Imagem de compartilhamento',
        help_text='Opcional. Aparece na prévia do link no WhatsApp e no LinkedIn. '
                  'Use 1200 x 630 pixels. Sem imagem enviada, o site usa a original.'
    )

    # Contatos
    email = models.EmailField(default='insperconsultingclub@gmail.com', verbose_name='E-mail')
    instagram_url = models.URLField(
        max_length=300, default='https://www.instagram.com/insperconsultingclub/',
        verbose_name='Link do Instagram'
    )
    instagram_label = models.CharField(max_length=100, default='@insperconsultingclub', verbose_name='Nome exibido do Instagram')
    linkedin_url = models.URLField(
        max_length=300, default='https://br.linkedin.com/company/insperconsultingclub',
        verbose_name='Link do LinkedIn'
    )
    linkedin_label = models.CharField(max_length=100, default='Insper Consulting Club', verbose_name='Nome exibido do LinkedIn')
    github_url = models.URLField(
        max_length=300, default='https://github.com/insper-consulting-club',
        verbose_name='Link do GitHub'
    )
    github_label = models.CharField(max_length=100, default='insper-consulting-club', verbose_name='Nome exibido do GitHub')

    # Home
    home_hero_title = models.CharField(
        max_length=200, default='O futuro consultor começa no ICC', verbose_name='Título do topo'
    )
    home_statement = models.CharField(
        max_length=300,
        default='Preparamos nossos membros para os processos seletivos mais exigentes do mercado.',
        verbose_name='Frase de destaque'
    )
    home_about_title = models.CharField(
        max_length=200, default='Mais do que um clube, somos um ambiente de formação',
        verbose_name='Título de "Quem somos"'
    )
    home_about_title_highlight = models.CharField(
        max_length=200, blank=True, default='para futuros consultores.',
        verbose_name='Final do título, em destaque',
        help_text='Opcional. Aparece em vermelho, logo depois do título.'
    )
    home_about_text = models.TextField(
        default='A Liga Insper Consulting Club é uma organização estudantil fundada em 2020, '
                'dedicada ao desenvolvimento de futuros consultores. Ao longo do semestre, '
                'promovemos capacitações, resolução de cases, visitas corporativas e iniciativas '
                'que aproximam nossos membros da realidade das principais empresas do mercado.',
        verbose_name='Texto de "Quem somos"'
    )
    home_about_photo = models.ImageField(
        upload_to='site/', null=True, blank=True, verbose_name='Foto de "Quem somos"',
        help_text='Opcional. Sem foto enviada, o site usa a foto da reunião inaugural.'
    )
    home_about_photo_alt = models.CharField(
        max_length=200, default='Membros da Liga Insper Consulting Club na reunião inaugural',
        verbose_name='Descrição da foto',
        help_text='Lida por leitores de tela. Descreva o que aparece na foto.'
    )
    mission = models.TextField(
        default='Conectar alunos do Insper ao mercado de consultoria, desenvolvendo as competências '
                'técnicas e comportamentais exigidas pelas principais firmas do setor.',
        verbose_name='Missão'
    )
    mission_how = models.TextField(
        default='Treinamento para processos seletivos (GMAT, Verbal, Data e Fit Interview) e '
                'capacitação prática na resolução de cases reais de negócio.',
        verbose_name='Como preparamos'
    )
    mission_goal = models.TextField(
        default='Consolidar o ICC como referência em consultoria entre os clubes estudantis do Brasil '
                'e expandir a atuação para tecnologia e empreendedorismo.',
        verbose_name='Onde queremos chegar'
    )
    home_cta_title = models.CharField(
        max_length=200, default='Pronto para dar o próximo passo na sua carreira?',
        verbose_name='Chamada final'
    )

    # Rodapé
    footer_tagline = models.CharField(
        max_length=300,
        default='Mais do que um clube, somos um ambiente de formação para futuros consultores.',
        verbose_name='Frase do rodapé'
    )

    # Abertura de cada página (o texto abaixo do título)
    team_lead = models.CharField(
        max_length=300, default='Conheça os membros que fazem parte da Liga Insper Consulting Club',
        verbose_name='Página Equipe'
    )
    partners_lead = models.CharField(
        max_length=300,
        default='Conheça as empresas que apoiam o Insper Consulting Club e contribuem para a '
                'formação dos futuros líderes em consultoria.',
        verbose_name='Página Parceiros'
    )
    partners_benefits_title = models.CharField(
        max_length=200, default='O que sua empresa ganha ao apoiar o Insper Consulting Club',
        verbose_name='Título de "Por que ser parceiro"',
        help_text='Os benefícios em si ficam na aba Parceiros.'
    )
    projects_lead = models.CharField(
        max_length=300,
        default='Como formamos consultores, do primeiro semestre na entidade aos cases reais '
                'resolvidos ao longo da Jornada do Consultor.',
        verbose_name='Página Projetos'
    )
    featured_program_slug = models.CharField(
        max_length=50, blank=True, default='jornada-do-consultor',
        verbose_name='Programa dos cases em destaque',
        help_text='Identificador (slug) do programa para onde o botão "Ver os cases" da página Projetos leva. '
                  'Precisa ser igual ao slug de um programa cadastrado. Deixe vazio para esconder a seção.'
    )
    articles_lead = models.CharField(
        max_length=300, default='Artigos e publicações produzidos por membros do ICC',
        verbose_name='Página Artigos'
    )
    contact_lead = models.CharField(
        max_length=300, default='Entre em contato com o Insper Consulting Club',
        verbose_name='Página Contato'
    )
    process_lead = models.CharField(
        max_length=300,
        default='Participe do processo seletivo e faça parte da Liga Insper Consulting Club',
        verbose_name='Página Processo Seletivo'
    )
    process_closed_message = models.CharField(
        max_length=300,
        default='Inscrições encerradas. Acompanhe nosso Instagram para saber quando abrirmos o próximo processo.',
        verbose_name='Mensagem de inscrições encerradas'
    )

    # Política de Privacidade (o texto inicial é criado pela migration)
    privacy_updated = models.CharField(
        max_length=100, default='novembro de 2026', verbose_name='Última atualização',
        help_text='Como deve aparecer no site. Ex.: novembro de 2026.'
    )
    privacy_text = models.TextField(
        blank=True, verbose_name='Texto da política',
        help_text='Em Markdown: ## Título, **negrito**, - item de lista, [link](https://...). '
                  'Separe os parágrafos com uma linha em branco.'
    )

    class Meta:
        verbose_name = 'Configuração do site'
        verbose_name_plural = 'Configuração do site'

    def __str__(self):
        return 'Configuração do site'

    def clean(self):
        if self.featured_program_slug and not Program.objects.filter(slug=self.featured_program_slug).exists():
            raise ValidationError({
                'featured_program_slug': 'Não existe programa com esse slug. Confira em Programas.'
            })

    # Campos que entram no HTML do site durante o build do frontend. Mudar um
    # deles pede um novo deploy do frontend.
    CAMPOS_DO_HTML = ('site_name', 'site_description', 'logo', 'favicon', 'og_image')

    def save(self, *args, **kwargs):
        # Registro único: qualquer salvamento atualiza sempre o mesmo.
        self.pk = 1
        anterior = SiteConfig.objects.filter(pk=1).values(*self.CAMPOS_DO_HTML).first()
        super().save(*args, **kwargs)
        # Só reconstrói o frontend quando um campo do HTML mudou. O primeiro
        # registro (anterior vazio) não conta: é a criação inicial.
        if anterior is not None and any(
            (anterior[campo] or '') != str(getattr(self, campo) or '') for campo in self.CAMPOS_DO_HTML
        ):
            transaction.on_commit(dispara_deploy_do_frontend)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PartnerBenefit(models.Model):
    """Item de "Por que ser parceiro", na página Parceiros."""
    site_config = models.ForeignKey(
        SiteConfig, on_delete=models.CASCADE, related_name='partner_benefits', verbose_name='Configuração'
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descrição')
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Benefício para parceiros'
        verbose_name_plural = 'Benefícios para parceiros'
        ordering = ['order']

    def __str__(self):
        return self.title


class SiteText(models.Model):
    """
    Texto curto do site (título de seção, rótulo, botão, mensagem de lista
    vazia). As entradas nascem do catálogo em site_texts.py; o admin só edita
    o valor, não cria nem exclui.
    """
    key = models.CharField(max_length=100, unique=True, verbose_name='Chave')
    group = models.CharField(max_length=100, verbose_name='Página')
    description = models.CharField(max_length=200, verbose_name='Onde aparece')
    value = models.CharField(
        max_length=300, verbose_name='Texto',
        help_text='Mantenha os trechos entre chaves, como {n} ou {data}: o site os preenche.'
    )
    order = models.IntegerField(default=0, verbose_name='Ordem')

    class Meta:
        verbose_name = 'Texto do site'
        verbose_name_plural = 'Textos do site'
        ordering = ['order']

    def __str__(self):
        return f'{self.group}: {self.description}'


class NavItem(models.Model):
    """
    Item do menu do topo, do rodapé ou botão de destaque do topo. Aponta para
    uma página do site (lista fixa) ou para um link livre.
    """
    class Area(models.TextChoices):
        MENU = 'menu', 'Menu (topo e rodapé)'
        TOPO = 'topo', 'Só no menu do topo'
        RODAPE = 'rodape', 'Só no rodapé'
        BOTAO = 'botao', 'Botão de destaque do topo'

    # Páginas que existem no site. Quem edita escolhe daqui, em vez de digitar
    # o endereço, para o link não quebrar por erro de digitação.
    PAGINAS = {
        'home': '/',
        'equipe': '/equipe',
        'parceiros': '/parceiros',
        'projetos': '/projetos',
        'artigos': '/artigos',
        'processo': '/processo',
        'contato': '/contato',
        'politica-de-privacidade': '/politica-de-privacidade',
    }
    PAGE_CHOICES = [
        ('home', 'Página inicial'),
        ('equipe', 'Equipe'),
        ('parceiros', 'Parceiros'),
        ('projetos', 'Projetos'),
        ('artigos', 'Artigos'),
        ('processo', 'Processo seletivo'),
        ('contato', 'Contato'),
        ('politica-de-privacidade', 'Política de Privacidade'),
    ]

    site_config = models.ForeignKey(
        SiteConfig, on_delete=models.CASCADE, related_name='nav_items', verbose_name='Configuração'
    )
    label = models.CharField(max_length=60, verbose_name='Texto exibido')
    area = models.CharField(max_length=10, choices=Area.choices, default=Area.MENU, verbose_name='Onde aparece')
    page = models.CharField(
        max_length=40, choices=PAGE_CHOICES, blank=True, verbose_name='Página do site',
        help_text='Escolha uma página do site, ou deixe vazio e preencha "Link livre". '
                  'Em Projetos e Equipe, o menu do topo mostra também a lista de programas e de diretorias.'
    )
    url = models.CharField(
        max_length=300, blank=True, verbose_name='Link livre',
        help_text='Endereço completo (https://...) ou um caminho do site (/equipe). Use só se não houver página na lista.'
    )
    order = models.IntegerField(default=0, verbose_name='Ordem')
    is_active = models.BooleanField(
        default=True, verbose_name='Exibir no site',
        help_text='Desmarque para esconder o item sem apagar.'
    )

    class Meta:
        verbose_name = 'Item de navegação'
        verbose_name_plural = 'Itens de navegação'
        ordering = ['order']

    def __str__(self):
        return self.label

    @property
    def path(self):
        return self.PAGINAS[self.page] if self.page else self.url

    @property
    def external(self):
        return self.path.startswith(('http://', 'https://', 'mailto:'))

    def clean(self):
        if self.page and self.url:
            raise ValidationError('Preencha a página do site ou o link livre, não os dois.')
        if not self.page and not self.url:
            raise ValidationError('Escolha uma página do site ou informe um link livre.')
        if self.url and not self.url.startswith(('/', 'http://', 'https://', 'mailto:')):
            raise ValidationError({
                'url': 'O link precisa começar com https://, http://, mailto: ou / (caminho do site).'
            })
