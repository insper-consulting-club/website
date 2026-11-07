from django import forms
from django.contrib import admin, messages
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    Partner_Category, Activity, ActivityImage, ActivityContentBlock,
    Partner, Team_Member, Media, ArticleImage, Member_Position, Directorate,
    DirectorateMembership, Statistic, Participant,
    Project, ProjectImage, ProjectTimelineEvent, ProjectContentBlock,
    ActivityCategory, CalendarMonth, Contact,
    SuccessCase, SuccessCaseParticipant,
    SelectionProcess, SelectionProcessStage, SelectionProcessStep,
    SelectionProcessRequirement, PreparationMaterial, PreparationMaterialItem,
)

# Títulos do topo e da página inicial do /admin
admin.site.site_header = 'Administração · Insper Consulting Club'
admin.site.site_title = 'Admin ICC'
admin.site.index_title = 'Conteúdo do site'


def miniatura(imagem, altura=40):
    """Mostra a imagem pequena nas listas e no formulário do admin."""
    if not imagem:
        return '—'
    return format_html(
        '<img src="{}" style="height:{}px;border-radius:4px;object-fit:cover">',
        imagem.url, altura,
    )


# ---------------------------------------------------------------------------
# Parceiros
# ---------------------------------------------------------------------------

@admin.register(Partner_Category)
class PartnerCategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('logo', 'name', 'category', 'is_active', 'order')
    list_display_links = ('logo', 'name')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'category')
    # search_fields também é exigido pelo autocomplete de "parceiro responsável" em Atividades.
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    readonly_fields = ('logo_atual',)
    fields = ('name', 'logo_url', 'logo_atual', 'category', 'site', 'description', 'is_active', 'order')

    @admin.display(description='Logo')
    def logo(self, obj):
        return miniatura(obj.logo_url)

    @admin.display(description='Logo atual')
    def logo_atual(self, obj):
        return miniatura(obj.logo_url, 80)


# ---------------------------------------------------------------------------
# Equipe
# ---------------------------------------------------------------------------

@admin.register(Member_Position)
class MemberPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'power')
    list_editable = ('power',)
    search_fields = ('title',)
    ordering = ('power', 'title')


@admin.register(Directorate)
class DirectorateAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    search_fields = ('name',)
    ordering = ('order',)


class DirectorateMembershipForm(forms.ModelForm):
    class Meta:
        model = DirectorateMembership
        fields = '__all__'
        labels = {'directorate': 'Diretoria'}


class DirectorateMembershipInline(admin.TabularInline):
    model = DirectorateMembership
    form = DirectorateMembershipForm
    extra = 1
    fields = ('directorate', 'cargo', 'order')
    ordering = ('order',)


class SituacaoFilter(admin.SimpleListFilter):
    """Separa membros atuais de ex-membros (quem tem data de saída)."""
    title = 'situação'
    parameter_name = 'situacao'

    def lookups(self, request, model_admin):
        return [('atual', 'Membros atuais'), ('ex', 'Ex-membros')]

    def queryset(self, request, queryset):
        if self.value() == 'atual':
            return queryset.filter(exit_date__isnull=True)
        if self.value() == 'ex':
            return queryset.filter(exit_date__isnull=False)
        return queryset


class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = Team_Member
        fields = '__all__'
        labels = {
            'name': 'Nome',
            'photo': 'Foto',
            'biography': 'Biografia',
            'position': 'Cargo principal',
            'course': 'Curso',
            'year': 'Período',
            'hours': 'Horas dedicadas',
            'entry_date': 'Data de entrada',
            'exit_date': 'Data de saída (preencha para arquivar o membro)',
        }
        help_texts = {
            'exit_date': 'Quem tem data de saída deixa de aparecer na página Equipe, '
                         'mas o histórico continua guardado. Apague a data para reativar.',
        }


@admin.register(Team_Member)
class TeamMemberAdmin(admin.ModelAdmin):
    form = TeamMemberForm
    inlines = [DirectorateMembershipInline]
    list_display = ('foto', 'name', 'get_directorates', 'position', 'course', 'year', 'atual')
    list_display_links = ('foto', 'name')
    list_filter = (SituacaoFilter, 'directorate_memberships__directorate', 'position', 'year')
    # Exigido pelo autocomplete de participantes dos cases, e útil por si só
    # quando a lista acumula alumni além dos membros ativos.
    search_fields = ('name', 'email', 'course', 'linkedin')
    list_select_related = ('position',)
    filter_horizontal = ('projects',)
    date_hierarchy = 'entry_date'
    list_per_page = 50
    actions = ['arquivar', 'reativar']
    readonly_fields = ('foto_atual',)
    fieldsets = (
        (None, {'fields': ('name', 'photo', 'foto_atual', 'position', 'linkedin', 'email')}),
        ('Formação', {'fields': ('course', 'year')}),
        ('No ICC', {'fields': ('entry_date', 'exit_date', 'biography', 'trajetoria', 'hours', 'projects')}),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('directorate_memberships__directorate')

    @admin.display(description='Diretorias')
    def get_directorates(self, obj):
        return ', '.join(m.directorate.name for m in obj.directorate_memberships.all())

    @admin.display(description='Foto')
    def foto(self, obj):
        return miniatura(obj.photo)

    @admin.display(description='Foto atual')
    def foto_atual(self, obj):
        return miniatura(obj.photo, 120)

    @admin.display(description='Atual', boolean=True)
    def atual(self, obj):
        return obj.exit_date is None

    @admin.action(description='Arquivar selecionados (sai da página Equipe)')
    def arquivar(self, request, queryset):
        n = queryset.filter(exit_date__isnull=True).update(exit_date=timezone.localdate())
        self.message_user(request, f'{n} membro(s) arquivado(s). O histórico continua guardado.', messages.SUCCESS)

    @admin.action(description='Reativar selecionados (volta para a página Equipe)')
    def reativar(self, request, queryset):
        n = queryset.exclude(exit_date__isnull=True).update(exit_date=None)
        self.message_user(request, f'{n} membro(s) reativado(s).', messages.SUCCESS)


# ---------------------------------------------------------------------------
# Contato e inscrições
# ---------------------------------------------------------------------------

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'contact_type')
    list_filter = ('contact_type',)
    search_fields = ('name', 'email', 'phone', 'message')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'course', 'semester', 'created_at')
    list_filter = ('semester', 'course', 'created_at')
    search_fields = ('name', 'email', 'course', 'reason')
    date_hierarchy = 'created_at'


# ---------------------------------------------------------------------------
# Projetos
# ---------------------------------------------------------------------------

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'caption', 'order')
    ordering = ('order',)


class ProjectTimelineEventInline(admin.TabularInline):
    model = ProjectTimelineEvent
    extra = 1
    fields = ('date', 'title', 'description', 'order')
    ordering = ('order',)


class ProjectContentBlockInline(admin.StackedInline):
    model = ProjectContentBlock
    extra = 1
    fields = ('title', 'text', 'image', 'image_caption', 'image_align', 'order')
    ordering = ('order',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'start_date', 'end_date', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'category', 'start_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('partners',)
    date_hierarchy = 'start_date'
    list_select_related = ('category',)
    actions = ['arquivar', 'reativar']
    inlines = [ProjectImageInline, ProjectTimelineEventInline, ProjectContentBlockInline]

    # Soft delete: projetos não são apagados, só arquivados (is_active = False).
    #def has_delete_permission(self, request, obj=None):
    #    return False

    @admin.action(description='Arquivar selecionados (somem do site)')
    def arquivar(self, request, queryset):
        n = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(request, f'{n} projeto(s) arquivado(s). O histórico continua guardado.', messages.SUCCESS)

    @admin.action(description='Reativar selecionados (voltam para o site)')
    def reativar(self, request, queryset):
        n = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f'{n} projeto(s) reativado(s).', messages.SUCCESS)


# ---------------------------------------------------------------------------
# Atividades e calendário
# ---------------------------------------------------------------------------

class ActivityImageInline(admin.TabularInline):
    model = ActivityImage
    extra = 1
    fields = ('image', 'caption', 'order')
    ordering = ('order',)


class ActivityContentBlockInline(admin.StackedInline):
    model = ActivityContentBlock
    extra = 1
    fields = ('title', 'text', 'image', 'image_caption', 'image_align', 'order')
    ordering = ('order',)


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'responsible_partner')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    autocomplete_fields = ('responsible_partner',)
    list_select_related = ('category', 'responsible_partner')
    inlines = [ActivityImageInline, ActivityContentBlockInline]


@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('label', 'slug', 'badge', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('label', 'slug', 'description')
    ordering = ('order',)
    prepopulated_fields = {'slug': ('label',)}


@admin.register(CalendarMonth)
class CalendarMonthAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'semester', 'order')
    list_editable = ('order', 'semester')
    list_filter = ('semester', 'year')
    search_fields = ('month', 'items')
    ordering = ('year', 'order')


# ---------------------------------------------------------------------------
# Home e notícias
# ---------------------------------------------------------------------------

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('value', 'description', 'order')
    list_editable = ('order',)
    search_fields = ('value', 'description')
    ordering = ('order',)


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1
    fields = ('number', 'image', 'caption', 'previa')
    readonly_fields = ('previa',)
    ordering = ('number',)

    @admin.display(description='Prévia')
    def previa(self, obj):
        return miniatura(obj.image if obj.pk else None, 60)


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'authors', 'published', 'date', 'order')
    search_fields = ('title', 'slug', 'authors', 'topics', 'description', 'content', 'source')
    list_editable = ('published', 'order')
    list_filter = ('published', 'source', 'date')
    date_hierarchy = 'date'
    ordering = ('-date', 'order')
    inlines = [ArticleImageInline]


# ---------------------------------------------------------------------------
# Cases de sucesso
# ---------------------------------------------------------------------------

class SuccessCaseParticipantInline(admin.TabularInline):
    model = SuccessCaseParticipant
    extra = 1
    fields = ('member', 'role', 'order')
    ordering = ('role', 'order')
    autocomplete_fields = ('member',)


@admin.register(SuccessCase)
class SuccessCaseAdmin(admin.ModelAdmin):
    inlines = [SuccessCaseParticipantInline]
    list_display = ('semester', 'title', 'area', 'category', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'category', 'semester')
    search_fields = ('title', 'area', 'theme', 'award')
    list_select_related = ('category',)


# ---------------------------------------------------------------------------
# Processo seletivo (página /processo)
# ---------------------------------------------------------------------------

class SelectionProcessStageInline(admin.TabularInline):
    model = SelectionProcessStage
    extra = 1
    fields = ('label', 'date', 'order')
    ordering = ('order',)


class SelectionProcessStepInline(admin.StackedInline):
    model = SelectionProcessStep
    extra = 0
    fields = ('number', 'title', 'description', 'image', 'duration', 'tips', 'order')
    ordering = ('order',)


class SelectionProcessRequirementInline(admin.TabularInline):
    model = SelectionProcessRequirement
    extra = 1
    fields = ('text', 'icon', 'order')
    ordering = ('order',)


@admin.register(SelectionProcess)
class SelectionProcessAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'registrations_open')
    list_editable = ('is_active', 'registrations_open')
    list_filter = ('is_active',)
    search_fields = ('title',)
    inlines = [SelectionProcessStageInline, SelectionProcessStepInline,
               SelectionProcessRequirementInline]


class PreparationMaterialItemInline(admin.TabularInline):
    model = PreparationMaterialItem
    extra = 1
    fields = ('text', 'order')
    ordering = ('order',)


@admin.register(PreparationMaterial)
class PreparationMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'process', 'order')
    list_editable = ('order',)
    list_filter = ('process',)
    search_fields = ('title',)
    inlines = [PreparationMaterialItemInline]