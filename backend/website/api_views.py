from django.db.models import F, Min, Prefetch
from django.http import Http404, JsonResponse
from rest_framework import generics
from .models import (
    Member, Partner, Statistic, Project, ProgramComponent,
    Program, SelectionProcess,
    Article, Directorate, ProgramCase, SiteConfig
)
from .serializers import (
    MemberListSerializer, MemberDetailSerializer,
    PartnerSerializer, StatisticSerializer,
    ProjectListSerializer, ProjectDetailSerializer,
    ProgramComponentSerializer, ProgramSerializer,
    DirectorateSerializer, ProgramCaseSerializer,
    SelectionProcessSerializer, ArticleSerializer, ArticleListSerializer,
    SiteConfigSerializer
)


# Projetos ativos de cada parceiro, carregados de uma vez para o
# PartnerSerializer calcular contagens e lista sem uma consulta por parceiro.
ACTIVE_PROJECTS_PREFETCH = Prefetch(
    "projects",
    queryset=Project.objects.filter(is_active=True).select_related("program"),
    to_attr="active_projects",
)


class MemberListView(generics.ListAPIView):
    serializer_class = MemberListSerializer

    def get_queryset(self):
        # Uma pessoa pode estar em mais de uma diretoria (ex: diretora de
        # Pedagógico e também mentora), então a ordem é dada pela primeira
        # (menor order) delas; membros fora de qualquer diretoria vão para o fim.
        qs = Member.objects.select_related("position").prefetch_related(
            "directorate_memberships__directorate"
        ).annotate(
            min_directorate_order=Min("directorate_memberships__directorate__order")
        ).order_by(
            F("min_directorate_order").asc(nulls_last=True),
            "position__power", "name",
        )
        # Membros arquivados (com data de saída) nunca aparecem na API pública.
        return qs.filter(exit_date__isnull=True)


class MemberDetailView(generics.RetrieveAPIView):
    serializer_class = MemberDetailSerializer
    # Sem filtro de propósito: membros arquivados (com data de saída) não entram
    # na listagem da equipe, mas o perfil deles continua acessível por link
    # (ex.: a partir da equipe de um projeto).
    queryset = Member.objects.select_related("position").prefetch_related(
        "projects__partners", "directorate_memberships__directorate"
    ).all()


class DirectorateListView(generics.ListAPIView):
    serializer_class = DirectorateSerializer
    queryset = Directorate.objects.all().order_by("order")


class PartnerListView(generics.ListAPIView):
    serializer_class = PartnerSerializer

    def get_queryset(self):
        qs = (
            Partner.objects.select_related("category")
            .prefetch_related(ACTIVE_PROJECTS_PREFETCH)
            .filter(is_active=True)
            .order_by("order", "name")
        )
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category__id=category_id)
        return qs


class PartnerDetailView(generics.RetrieveAPIView):
    serializer_class = PartnerSerializer
    queryset = (
        Partner.objects.select_related("category")
        .prefetch_related(ACTIVE_PROJECTS_PREFETCH)
        .filter(is_active=True)
    )


class ProgramListView(generics.ListAPIView):
    serializer_class = ProgramSerializer
    queryset = Program.objects.filter(is_active=True).order_by("order")


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        # Projetos arquivados (is_active=False) não aparecem na API pública.
        qs = Project.objects.filter(is_active=True).prefetch_related(
            "partners").select_related("program")
        program = self.request.query_params.get("program")
        if program:
            qs = qs.filter(program__slug=program)
        return qs


class ProjectDetailView(generics.RetrieveAPIView):
    serializer_class = ProjectDetailSerializer
    # Projeto arquivado responde 404, como se não existisse.
    queryset = Project.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            "partners",
            queryset=Partner.objects.select_related("category").prefetch_related(ACTIVE_PROJECTS_PREFETCH),
        ),
        "members", "images", "timeline_events", "content_blocks",
    ).select_related("program")


class ProgramComponentListView(generics.ListAPIView):
    serializer_class = ProgramComponentSerializer

    def get_queryset(self):
        qs = ProgramComponent.objects.select_related("program").exclude(program__is_active=False)
        program = self.request.query_params.get("program")
        if program:
            qs = qs.filter(program__slug=program)
        return qs


class ProgramCaseListView(generics.ListAPIView):
    serializer_class = ProgramCaseSerializer

    def get_queryset(self):
        qs = ProgramCase.objects.filter(
            is_active=True, program__is_active=True
        ).select_related("program").prefetch_related(
            "participants__member"
        )
        program = self.request.query_params.get("program")
        if program:
            qs = qs.filter(program__slug=program)
        return qs


class StatisticListView(generics.ListAPIView):
    serializer_class = StatisticSerializer
    queryset = Statistic.objects.all().order_by("order")


class ArticleListView(generics.ListAPIView):
    # A lista não leva o texto nem as imagens do corpo; o artigo completo vem do detalhe.
    serializer_class = ArticleListSerializer
    # Rascunhos (Publicado desmarcado) não aparecem no site.
    queryset = Article.objects.filter(published=True).defer("content")


class ArticleDetailView(generics.RetrieveAPIView):
    serializer_class = ArticleSerializer
    # Rascunho responde 404, como se não existisse.
    queryset = Article.objects.filter(published=True).prefetch_related("images")

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        identifier = self.kwargs["identifier"]
        article = queryset.filter(slug=identifier).first()

        if article is None and identifier.isdecimal():
            article = queryset.filter(pk=int(identifier)).first()

        if article is None:
            raise Http404

        self.check_object_permissions(self.request, article)
        return article


class SelectionProcessView(generics.RetrieveAPIView):
    serializer_class = SelectionProcessSerializer

    def get_object(self):
        # Se por engano houver mais de um processo ativo, vale o mais recente.
        processo = SelectionProcess.objects.prefetch_related(
            'stages', 'steps', 'requirements',
            'materials', 'materials__items'
        ).filter(is_active=True).order_by('-id').first()
        if processo is None:
            raise Http404
        return processo


class SiteConfigView(generics.RetrieveAPIView):
    serializer_class = SiteConfigSerializer

    def get_object(self):
        # Registro único; criado na hora se, por algum motivo, ainda não existir.
        return SiteConfig.get_solo()


def health(request):
    # Usado pelo monitor de uptime para manter o backend acordado; não consulta o banco.
    return JsonResponse({"status": "ok"})
