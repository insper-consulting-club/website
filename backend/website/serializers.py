from rest_framework import serializers
from . import citacao
from .site_texts import PADRAO as PADRAO_TEXTOS
from .models import (
    Member, Partner, Statistic, Project, ProjectImage,
    Directorate,
    ProjectTimelineEvent, ProjectContentBlock,
    ProgramComponent, Program, DirectorateMembership,
    Article, ArticleImage,
    SelectionProcess, SelectionProcessRequirement,
    SelectionProcessStage, SelectionProcessStep,
    PreparationMaterial, PreparationMaterialItem,
    ProgramCase, ProgramCaseParticipant,
    SiteConfig, PartnerBenefit, ProgramContentBlock, SecaoDaHome, SiteText, NavItem
)


class DirectorateSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)

    class Meta:
        model = Directorate
        fields = ["id", "name", "slug", "order"]


class DirectorateMembershipSerializer(serializers.ModelSerializer):
    directorate = serializers.StringRelatedField()
    directorate_slug = serializers.CharField(source="directorate.slug", read_only=True)

    class Meta:
        model = DirectorateMembership
        fields = ["directorate", "directorate_slug", "cargo", "order"]


class ProgramSerializer(serializers.ModelSerializer):
    highlights = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = Program
        fields = ["id", "slug", "label", "subtitle", "description", "highlights",
                  "icon_url", "signup_url", "order"]

    def get_highlights(self, obj):
        return obj.get_highlights_list()

    def get_icon_url(self, obj):
        request = self.context.get("request")
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        return None


class ProgramContentBlockSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProgramContentBlock
        fields = ["id", "title", "text", "image_url", "image_caption", "image_align", "order"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProgramDetailSerializer(ProgramSerializer):
    # Só o detalhe leva os blocos: a lista de programas alimenta o menu, o
    # rodapé e a Home, e não precisa carregar os textos de todas as páginas.
    content_blocks = ProgramContentBlockSerializer(many=True, read_only=True)

    class Meta(ProgramSerializer.Meta):
        fields = ProgramSerializer.Meta.fields + ["content_blocks"]


class PartnerProjectSerializer(serializers.ModelSerializer):
    program = serializers.StringRelatedField()

    class Meta:
        model = Project
        fields = ["id", "title", "description", "program", "start_date", "end_date"]


class PartnerSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    logo_url = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = [
            "id",
            "name",
            "description",
            "category",
            "site",
            "logo_url",
            "projects",
        ]

    def _active_projects(self, obj):
        # As views trazem os projetos ativos já carregados em `active_projects`
        # (ver `ACTIVE_PROJECTS_PREFETCH`). A consulta abaixo é só um reserva
        # para quem serializa um parceiro sem esse prefetch.
        projects = getattr(obj, "active_projects", None)
        if projects is None:
            projects = list(obj.projects.filter(is_active=True).select_related("program"))
        return projects

    def _completed_projects(self, obj):
        done = [p for p in self._active_projects(obj) if p.end_date is not None]
        return sorted(done, key=lambda p: p.end_date, reverse=True)

    def get_projects(self, obj):
        return PartnerProjectSerializer(
            self._completed_projects(obj), many=True, context=self.context
        ).data

    def get_logo_url(self, obj):
        request = self.context.get("request")
        if obj.logo_url and request:
            return request.build_absolute_uri(obj.logo_url.url)
        return None

class ProjectImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProjectImage
        fields = ["id", "image_url", "caption", "order"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProjectTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTimelineEvent
        fields = ["id", "date", "title", "description", "order"]


class ContentBlockSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "title", "text", "image_url", "image_caption", "image_align", "order"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProjectContentBlockSerializer(ContentBlockSerializer):
    class Meta(ContentBlockSerializer.Meta):
        model = ProjectContentBlock


class ProjectListSerializer(serializers.ModelSerializer):
    partners = serializers.StringRelatedField(many=True)
    program = serializers.SlugRelatedField(slug_field='slug', read_only=True)

    class Meta:
        model = Project
        fields = ["id", "title", "description", "program", "partners", "start_date", "end_date"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    partners = PartnerSerializer(many=True)
    program = ProgramSerializer()
    members = serializers.SerializerMethodField()
    images = ProjectImageSerializer(many=True)
    timeline_events = ProjectTimelineEventSerializer(many=True)
    content_blocks = ProjectContentBlockSerializer(many=True)

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "program",
            "partners", "start_date", "end_date",
            "members", "images", "timeline_events", "content_blocks"
        ]

    def get_members(self, obj):
        return [{"id": m.id, "name": m.name} for m in obj.members.all()]


class ProgramComponentSerializer(serializers.ModelSerializer):
    program = serializers.SlugRelatedField(slug_field='slug', read_only=True)

    class Meta:
        model = ProgramComponent
        fields = ["id", "title", "description", "program"]


class MemberListSerializer(serializers.ModelSerializer):
    position = serializers.StringRelatedField()
    # A prioridade do cargo já existe no model e é o que ordena esta listagem.
    # Exposta para que o frontend selecione a liderança por esse número, em vez
    # de procurar palavras dentro do texto do cargo.
    position_power = serializers.IntegerField(source="position.power", read_only=True)
    directorate_memberships = DirectorateMembershipSerializer(many=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ["id", "name", "position", "position_power", "directorate_memberships",
                  "photo_url", "linkedin"]

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


class MemberDetailSerializer(serializers.ModelSerializer):
    position = serializers.StringRelatedField()
    directorate_memberships = DirectorateMembershipSerializer(many=True)
    photo_url = serializers.SerializerMethodField()
    trajetoria = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            "id", "name", "position", "directorate_memberships", "photo_url", "linkedin",
            "trajetoria",
        ]

    def get_trajetoria(self, obj):
        # Mesmo formato de antes: o frontend lê [{"semestre", "cargo"}], em ordem de semestre.
        return [{"semestre": etapa.semester, "cargo": etapa.role} for etapa in obj.trajectory_steps.all()]

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


class StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        fields = ["id", "value", "description", "order"]


class ArticleImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ArticleImage
        fields = ["number", "image_url", "caption"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


def autores_do_artigo(artigo):
    """
    Os autores como o site os mostra: o nome sem as chaves do BibTeX, o membro (quando há vínculo, para filtrar por
    autor) e se ele tem perfil na página Equipe (só membros ativos têm). Sem autores cadastrados (texto antigo), o autor é o próprio clube.
    """
    if not artigo.article_authors.exists():
        return [{"name": Article.NOME_INSTITUCIONAL, "member_id": None, "has_profile": False}]
    return [
        {
            "name": autor.display_name,
            "member_id": autor.member_id,
            "has_profile": bool(autor.member_id and autor.member.is_active),
        }
        for autor in artigo.article_authors.all()
    ]


class ArticleSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    # Imagens chamadas no texto como ![](imagem-1); o site troca pelo endereço.
    images = ArticleImageSerializer(many=True, read_only=True)
    authors = serializers.SerializerMethodField()
    # As citações do artigo (ABNT, APA, BibTeX, BibLaTeX e RIS). Trazem marcadores de data de acesso, que o site
    # troca pela data de quem copia (ver citacao.py).
    citations = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id", "slug", "title", "authors", "topics", "description", "content", "images", "image_url", "date", "order",
            "citations",
        ]

    def get_authors(self, obj):
        return autores_do_artigo(obj)

    def get_citations(self, obj):
        return citacao.citacoes(obj)

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ArticleListSerializer(serializers.ModelSerializer):
    """Versão enxuta para a lista de artigos: sem o texto completo e sem as imagens do corpo."""
    image_url = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["id", "slug", "title", "authors", "topics", "description", "image_url", "date", "order"]

    def get_authors(self, obj):
        return autores_do_artigo(obj)

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class SelectionProcessStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelectionProcessStage
        fields = ["id", "label", "date", "order"]


class SelectionProcessStepSerializer(serializers.ModelSerializer):
    tips = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = SelectionProcessStep
        fields = ["id", "number", "title", "description", "image_url", "duration", "tips", "order"]

    def get_tips(self, obj):
        return obj.get_tips_list()

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class SelectionProcessRequirementSerializer(serializers.ModelSerializer):
    icon_url = serializers.SerializerMethodField()

    class Meta:
        model = SelectionProcessRequirement
        fields = ["id", "text", "icon_url", "order"]

    def get_icon_url(self, obj):
        request = self.context.get("request")
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        return None

class PreparationMaterialItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreparationMaterialItem
        fields = ['id', 'text', 'order']
 
 
class PreparationMaterialSerializer(serializers.ModelSerializer):
    items = PreparationMaterialItemSerializer(many=True)
 
    class Meta:
        model = PreparationMaterial
        fields = ['id', 'title', 'items', 'order']
 
class SelectionProcessSerializer(serializers.ModelSerializer):
    stages = SelectionProcessStageSerializer(many=True)
    steps = SelectionProcessStepSerializer(many=True)
    requirements = SelectionProcessRequirementSerializer(many=True)
    materials = PreparationMaterialSerializer(many=True)
    registrations_open = serializers.SerializerMethodField()

    class Meta:
        model = SelectionProcess
        fields = ['id', 'title', 'registrations_open', 'registration_url', 'stages', 'steps', 'requirements', 'materials']

    def get_registrations_open(self, obj):
        # O admin recusa abrir as inscrições sem link, mas um cadastro feito por
        # fora do admin poderia deixar "Inscreva-se" sem destino. Sem link, a
        # API informa as inscrições como encerradas.
        return obj.registrations_open and bool(obj.registration_url)
    
class ProgramCaseParticipantSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="member.name", read_only=True)
    linkedin = serializers.CharField(source="member.linkedin", read_only=True)
    member_id = serializers.IntegerField(source="member.id", read_only=True)

    class Meta:
        model = ProgramCaseParticipant
        fields = ["member_id", "name", "linkedin", "role", "order"]


class ProgramCaseSerializer(serializers.ModelSerializer):
    program = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    participants = ProgramCaseParticipantSerializer(many=True, read_only=True)

    panel = serializers.SerializerMethodField()

    class Meta:
        model = ProgramCase
        fields = [
            "id", "program", "semester", "title", "area", "theme", "panel",
            "award", "publication_url", "participants", "order",
        ]

    def get_panel(self, obj):
        return obj.get_panel_list()


class PartnerBenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartnerBenefit
        fields = ["id", "title", "description", "order"]


class NavItemSerializer(serializers.ModelSerializer):
    path = serializers.CharField(read_only=True)
    external = serializers.BooleanField(read_only=True)

    class Meta:
        model = NavItem
        fields = ["id", "label", "area", "page", "path", "external", "order"]


class SiteConfigSerializer(serializers.ModelSerializer):
    home_about_photo_url = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    favicon_url = serializers.SerializerMethodField()
    og_image_url = serializers.SerializerMethodField()
    partner_benefits = PartnerBenefitSerializer(many=True, read_only=True)
    texts = serializers.SerializerMethodField()
    nav_items = serializers.SerializerMethodField()
    home_sections = serializers.SerializerMethodField()

    class Meta:
        model = SiteConfig
        # As imagens não saem como campo de arquivo: o site recebe só o endereço.
        exclude = ["id", "home_about_photo", "logo", "favicon", "og_image"]

    def get_nav_items(self, obj):
        # Item escondido no admin não chega ao site.
        ativos = [item for item in obj.nav_items.all() if item.is_active]
        return NavItemSerializer(ativos, many=True).data

    def get_home_sections(self, obj):
        # As seções visíveis da Home, na ordem do editor (o Topo e a Apresentação ficam fora: são sempre os primeiros).
        # O aviso só sai quando tem texto; o botão, quando tem destino.
        aviso = SiteText.objects.filter(key="home.aviso_texto").values_list("value", flat=True).first() or ""
        secoes = []
        for secao in SecaoDaHome.objects.filter(visible=True):
            if secao.key != "aviso":
                secoes.append({"key": secao.key})
            elif aviso.strip():
                secoes.append({
                    "key": secao.key,
                    "button_path": secao.button_path or None,
                    "button_external": secao.button_external,
                })
        return secoes

    def get_texts(self, obj):
        # Parte do catálogo: um texto que ainda não chegou ao banco sai com o
        # valor original, em vez de faltar na resposta.
        return {**PADRAO_TEXTOS, **dict(SiteText.objects.values_list("key", "value"))}

    def _url(self, imagem):
        request = self.context.get("request")
        if imagem and request:
            return request.build_absolute_uri(imagem.url)
        return None

    def get_home_about_photo_url(self, obj):
        return self._url(obj.home_about_photo)

    def get_logo_url(self, obj):
        return self._url(obj.logo)

    def get_favicon_url(self, obj):
        return self._url(obj.favicon)

    def get_og_image_url(self, obj):
        return self._url(obj.og_image)
