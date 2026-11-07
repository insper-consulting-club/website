import logging
from django.conf import settings
from django.db.models import Min, F
from django.utils.html import escape
from django.http import Http404, JsonResponse
from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework.throttling import ScopedRateThrottle
from .models import (
    Team_Member, Partner, Statistic, Project, Activity,
    ActivityCategory, CalendarMonth, SelectionProcess,
    Media, Contact, Directorate, SuccessCase
)
from .serializers import (
    TeamMemberListSerializer, TeamMemberDetailSerializer,
    PartnerSerializer, StatisticSerializer,
    ProjectListSerializer, ProjectDetailSerializer,
    ActivitySerializer, ActivityDetailSerializer,
    ActivityCategorySerializer, CalendarMonthSerializer,
    DirectorateSerializer, SuccessCaseSerializer,
    SelectionProcessSerializer, MediaSerializer,
    ContactSerializer
)


class TeamMemberListView(generics.ListAPIView):
    serializer_class = TeamMemberListSerializer

    def get_queryset(self):
        # Uma pessoa pode estar em mais de uma diretoria (ex: diretora de
        # Pedagógico e também mentora), então a ordem é dada pela primeira
        # (menor order) delas; membros sem nenhuma vão para o fim.
        qs = Team_Member.objects.select_related("position").prefetch_related(
            "directorate_memberships__directorate"
        ).annotate(
            min_directorate_order=Min("directorate_memberships__directorate__order")
        ).order_by(
            F("min_directorate_order").asc(nulls_last=True),
            "position__power", "name",
        )
        # Membros arquivados (com data de saída) nunca aparecem na API pública.
        return qs.filter(exit_date__isnull=True)


class TeamMemberDetailView(generics.RetrieveAPIView):
    serializer_class = TeamMemberDetailSerializer
    # Sem filtro de propósito: membros arquivados (com data de saída) não entram
    # na listagem da equipe, mas o perfil deles continua acessível por link
    # (ex.: a partir da equipe de um projeto).
    queryset = Team_Member.objects.select_related("position").prefetch_related(
        "projects__partners", "directorate_memberships__directorate"
    ).all()


class DirectorateListView(generics.ListAPIView):
    serializer_class = DirectorateSerializer
    queryset = Directorate.objects.all().order_by("order")


class PartnerListView(generics.ListAPIView):
    serializer_class = PartnerSerializer

    def get_queryset(self):
        qs = Partner.objects.select_related("category").filter(is_active=True).order_by("order", "name")
        category_id = self.request.query_params.get("category")
        if category_id:
            qs = qs.filter(category__id=category_id)
        return qs


class PartnerDetailView(generics.RetrieveAPIView):
    serializer_class = PartnerSerializer
    queryset = Partner.objects.select_related("category").filter(is_active=True)



class ActivityCategoryListView(generics.ListAPIView):
    serializer_class = ActivityCategorySerializer
    queryset = ActivityCategory.objects.filter(is_active=True).order_by("order")



class CalendarMonthListView(generics.ListAPIView):
    serializer_class = CalendarMonthSerializer

    def get_queryset(self):
        qs = CalendarMonth.objects.all().order_by("order")
        semester = self.request.query_params.get("semester")
        if semester:
            qs = qs.filter(semester__in=[semester, "both"])
        return qs


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectListSerializer

    def get_queryset(self):
        # Projetos arquivados (is_active=False) não aparecem na API pública.
        qs = Project.objects.filter(is_active=True).prefetch_related(
            "partners").select_related("category")
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        return qs


class ProjectDetailView(generics.RetrieveAPIView):
    serializer_class = ProjectDetailSerializer
    # Projeto arquivado responde 404, como se não existisse.
    queryset = Project.objects.filter(is_active=True).prefetch_related(
        "partners", "members", "images", "timeline_events", "content_blocks"
    ).select_related("category")


class ActivityListView(generics.ListAPIView):
    serializer_class = ActivitySerializer

    def get_queryset(self):
        qs = Activity.objects.select_related("category").exclude(category__is_active=False)
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        return qs


class SuccessCaseListView(generics.ListAPIView):
    serializer_class = SuccessCaseSerializer

    def get_queryset(self):
        qs = SuccessCase.objects.filter(
            is_active=True, category__is_active=True
        ).select_related("category").prefetch_related(
            "participants__member"
        )
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category__slug=category)
        return qs


class ActivityDetailView(generics.RetrieveAPIView):
    serializer_class = ActivityDetailSerializer
    queryset = Activity.objects.prefetch_related(
        "images", "content_blocks"
    ).select_related("category", "responsible_partner").all()


class StatisticListView(generics.ListAPIView):
    serializer_class = StatisticSerializer
    queryset = Statistic.objects.all().order_by("order")


class MediaListView(generics.ListAPIView):
    serializer_class = MediaSerializer
    # Rascunhos (Publicado desmarcado) não aparecem no site.
    queryset = Media.objects.filter(published=True).prefetch_related("images")


class MediaDetailView(generics.RetrieveAPIView):
    serializer_class = MediaSerializer
    # Rascunho responde 404, como se não existisse.
    queryset = Media.objects.filter(published=True).prefetch_related("images")

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


# class ContactInfoView(generics.RetrieveAPIView):
#     serializer_class = ContactInfoSerializer

#     def get_object(self):
#         return get_object_or_404(ContactInfo, is_active=True)


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


class ContactCreateView(generics.CreateAPIView):
    serializer_class = ContactSerializer
    queryset = Contact.objects.all()
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"
    # Só aceita JSON: um <form> HTML comum de outro site não consegue montar
    # esse tipo de corpo sem JavaScript, e JavaScript de outra origem já é
    # barrado pelo CORS. Fecha a via de um envio automático disfarçado.
    parser_classes = [JSONParser]

    def perform_create(self, serializer):
        contact = serializer.save()
        self._send_notification(contact)

    def _send_notification(self, contact):
        api_key = settings.SENDGRID_API_KEY
        to_email = settings.EMAIL_DESTINATARIO
        from_email = settings.EMAIL_REMETENTE

        if not api_key or not to_email:
            return

        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=f"Novo pedido de contato [{contact.get_contact_type_display()}]",
                # Campos preenchidos pelo visitante: escapados antes de entrar
                # no HTML do email, pra não permitir injeção de marcação/links.
                html_content=f"""
                    <h2>Novo pedido de contato recebido!</h2>
                    <p><strong>Nome:</strong> {escape(contact.name)}</p>
                    <p><strong>Email:</strong> {escape(contact.email)}</p>
                    <p><strong>Telefone:</strong> {escape(contact.phone)}</p>
                    <p><strong>Mensagem:</strong></p>
                    <p>{escape(contact.message)}</p>
                """
            )
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            sg.send(message)
        except Exception:
            logging.getLogger(__name__).exception("Falha no envio do email")


def health(request):
    # Usado pelo monitor de uptime para manter o backend acordado; não consulta o banco.
    return JsonResponse({"status": "ok"})
