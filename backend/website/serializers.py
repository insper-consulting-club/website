from rest_framework import serializers
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
    SiteConfig, PartnerBenefit
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
                  "icon_url", "badge", "badge_class", "signup_url", "order"]

    def get_highlights(self, obj):
        return obj.get_highlights_list()

    def get_icon_url(self, obj):
        request = self.context.get("request")
        if obj.icon and request:
            return request.build_absolute_uri(obj.icon.url)
        return None


class PartnerProjectSerializer(serializers.ModelSerializer):
    program = serializers.StringRelatedField()

    class Meta:
        model = Project
        fields = ["id", "title", "description", "program", "start_date", "end_date"]


class PartnerSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    logo_url = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    completed_projects_count = serializers.SerializerMethodField()
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
            "projects_count",
            "completed_projects_count",
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

    def get_projects_count(self, obj):
        return len(self._active_projects(obj))

    def get_completed_projects_count(self, obj):
        return len(self._completed_projects(obj))

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
                  "photo_url", "course", "year", "linkedin"]

    def get_photo_url(self, obj):
        request = self.context.get("request")
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


class MemberDetailSerializer(serializers.ModelSerializer):
    position = serializers.StringRelatedField()
    directorate_memberships = DirectorateMembershipSerializer(many=True)
    photo_url = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()
    number_of_projects = serializers.IntegerField()

    class Meta:
        model = Member
        fields = [
            "id", "name", "position", "directorate_memberships", "photo_url", "biography",
            "number_of_projects", "projects", "hours",
            "entry_date", "exit_date", "course", "year", "linkedin",
            "trajetoria",
        ]

    def get_projects(self, obj):
        # Projetos arquivados não aparecem no perfil do membro.
        qs = obj.projects.filter(is_active=True).select_related("program").prefetch_related("partners")
        return ProjectListSerializer(qs, many=True, context=self.context).data

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


class ArticleSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    # Imagens chamadas no texto como ![](imagem-1); o site troca pelo endereço.
    images = ArticleImageSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ["id", "slug", "title", "authors", "topics", "description", "content", "images", "link", "image_url", "source", "date", "order"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ArticleListSerializer(serializers.ModelSerializer):
    """Versão enxuta para a lista de artigos: sem o texto completo e sem as imagens do corpo."""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["id", "slug", "title", "authors", "topics", "description", "link", "image_url", "source", "date", "order"]

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


class SiteConfigSerializer(serializers.ModelSerializer):
    home_about_photo_url = serializers.SerializerMethodField()
    partner_benefits = PartnerBenefitSerializer(many=True, read_only=True)

    class Meta:
        model = SiteConfig
        # A foto não sai como campo de arquivo: o site recebe só o endereço.
        exclude = ["id", "home_about_photo"]

    def get_home_about_photo_url(self, obj):
        request = self.context.get("request")
        if obj.home_about_photo and request:
            return request.build_absolute_uri(obj.home_about_photo.url)
        return None
