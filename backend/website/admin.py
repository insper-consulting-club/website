from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
import re

from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .site_texts import PADRAO as PADRAO_TEXTOS
from .models import (
    PartnerCategory, ProgramComponent,
    Partner, Member, Article, ArticleImage, Position, Directorate,
    DirectorateMembership, Statistic,
    Project, ProjectImage, ProjectTimelineEvent, ProjectContentBlock,
    Program,
    ProgramCase, ProgramCaseParticipant,
    SelectionProcess, SelectionProcessStage, SelectionProcessStep,
    SelectionProcessRequirement, PreparationMaterial, PreparationMaterialItem,
    SiteConfig, PartnerBenefit, ProgramContentBlock, SiteText,
)

# Título da página inicial do /admin. O topo (nome e cabeçalho) fica em UNFOLD,
# no settings.
admin.site.index_title = 'Conteúdo do site'


# ---------------------------------------------------------------------------
# Usuários e grupos (models do Django, refeitos com as classes do Unfold para
# o painel ter um visual só)
# ---------------------------------------------------------------------------

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


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

@admin.register(PartnerCategory)
class PartnerCategoryAdmin(ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(Partner)
class PartnerAdmin(ModelAdmin):
    list_display = ('logo', 'name', 'category', 'is_active', 'order')
    list_display_links = ('logo', 'name')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'category')
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

@admin.register(Position)
class PositionAdmin(ModelAdmin):
    list_display = ('title', 'power')
    list_editable = ('power',)
    search_fields = ('title',)
    ordering = ('power', 'title')


@admin.register(Directorate)
class DirectorateAdmin(ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    search_fields = ('name',)
    ordering = ('order',)


class DirectorateMembershipForm(forms.ModelForm):
    class Meta:
        model = DirectorateMembership
        fields = '__all__'
        labels = {'directorate': 'Diretoria'}


class DirectorateMembershipInline(TabularInline):
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


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
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


@admin.register(Member)
class MemberAdmin(ModelAdmin):
    form = MemberForm
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
# Projetos
# ---------------------------------------------------------------------------

class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'caption', 'order')
    ordering = ('order',)


class ProjectTimelineEventInline(TabularInline):
    model = ProjectTimelineEvent
    extra = 1
    fields = ('date', 'title', 'description', 'order')
    ordering = ('order',)


class ProjectContentBlockInline(StackedInline):
    model = ProjectContentBlock
    extra = 1
    fields = ('title', 'text', 'image', 'image_caption', 'image_align', 'order')
    ordering = ('order',)


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ('title', 'program', 'start_date', 'end_date', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'program', 'start_date')
    search_fields = ('title', 'description')
    filter_horizontal = ('partners',)
    date_hierarchy = 'start_date'
    list_select_related = ('program',)
    actions = ['arquivar', 'reativar']
    inlines = [ProjectImageInline, ProjectTimelineEventInline, ProjectContentBlockInline]

    @admin.action(description='Arquivar selecionados (somem do site)')
    def arquivar(self, request, queryset):
        n = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(request, f'{n} projeto(s) arquivado(s). O histórico continua guardado.', messages.SUCCESS)

    @admin.action(description='Reativar selecionados (voltam para o site)')
    def reativar(self, request, queryset):
        n = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f'{n} projeto(s) reativado(s).', messages.SUCCESS)


# ---------------------------------------------------------------------------
# Programas e componentes
# ---------------------------------------------------------------------------

@admin.register(ProgramComponent)
class ProgramComponentAdmin(ModelAdmin):
    list_display = ('title', 'program')
    list_filter = ('program',)
    search_fields = ('title', 'description')
    list_select_related = ('program',)


class ProgramContentBlockInline(StackedInline):
    model = ProgramContentBlock
    extra = 0
    fields = ('title', 'text', 'image', 'image_caption', 'image_align', 'order')
    ordering = ('order',)


@admin.register(Program)
class ProgramAdmin(ModelAdmin):
    inlines = [ProgramContentBlockInline]
    list_display = ('label', 'slug', 'badge', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('label', 'slug', 'description')
    ordering = ('order',)
    prepopulated_fields = {'slug': ('label',)}


# ---------------------------------------------------------------------------
# Home e notícias
# ---------------------------------------------------------------------------

@admin.register(Statistic)
class StatisticAdmin(ModelAdmin):
    list_display = ('value', 'description', 'order')
    list_editable = ('order',)
    search_fields = ('value', 'description')
    ordering = ('order',)


class ArticleImageInline(TabularInline):
    model = ArticleImage
    extra = 1
    fields = ('number', 'image', 'caption', 'previa')
    readonly_fields = ('previa',)
    ordering = ('number',)

    @admin.display(description='Prévia')
    def previa(self, obj):
        return miniatura(obj.image if obj.pk else None, 60)


@admin.register(Article)
class ArticleAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'authors', 'published', 'date', 'order')
    search_fields = ('title', 'slug', 'authors', 'topics', 'description', 'content', 'source')
    list_editable = ('published', 'order')
    list_filter = ('published', 'source', 'date')
    date_hierarchy = 'date'
    ordering = ('-date', 'order')
    inlines = [ArticleImageInline]


# ---------------------------------------------------------------------------
# Cases dos programas
# ---------------------------------------------------------------------------

class ProgramCaseParticipantInline(TabularInline):
    model = ProgramCaseParticipant
    extra = 1
    fields = ('member', 'role', 'order')
    ordering = ('role', 'order')
    autocomplete_fields = ('member',)


@admin.register(ProgramCase)
class ProgramCaseAdmin(ModelAdmin):
    inlines = [ProgramCaseParticipantInline]
    list_display = ('semester', 'title', 'area', 'program', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'program', 'semester')
    search_fields = ('title', 'area', 'theme', 'award')
    list_select_related = ('program',)


# ---------------------------------------------------------------------------
# Processo seletivo (página /processo)
# ---------------------------------------------------------------------------

class SelectionProcessStageInline(TabularInline):
    model = SelectionProcessStage
    extra = 1
    fields = ('label', 'date', 'order')
    ordering = ('order',)


class SelectionProcessStepInline(StackedInline):
    model = SelectionProcessStep
    extra = 0
    fields = ('number', 'title', 'description', 'image', 'duration', 'tips', 'order')
    ordering = ('order',)


class SelectionProcessRequirementInline(TabularInline):
    model = SelectionProcessRequirement
    extra = 1
    fields = ('text', 'icon', 'order')
    ordering = ('order',)


@admin.register(SelectionProcess)
class SelectionProcessAdmin(ModelAdmin):
    list_display = ('title', 'is_active', 'registrations_open')
    list_editable = ('is_active', 'registrations_open')
    list_filter = ('is_active',)
    search_fields = ('title',)
    inlines = [SelectionProcessStageInline, SelectionProcessStepInline,
               SelectionProcessRequirementInline]


class PreparationMaterialItemInline(TabularInline):
    model = PreparationMaterialItem
    extra = 1
    fields = ('text', 'order')
    ordering = ('order',)


@admin.register(PreparationMaterial)
class PreparationMaterialAdmin(ModelAdmin):
    list_display = ('title', 'process', 'order')
    list_editable = ('order',)
    list_filter = ('process',)
    search_fields = ('title',)
    inlines = [PreparationMaterialItemInline]


# ---------------------------------------------------------------------------
# Configuração do site (textos e contatos que não pertencem a outro cadastro)
# ---------------------------------------------------------------------------

class PartnerBenefitInline(TabularInline):
    model = PartnerBenefit
    extra = 0
    fields = ('title', 'description', 'order')
    ordering = ('order',)
    tab = True


@admin.register(SiteConfig)
class SiteConfigAdmin(ModelAdmin):
    inlines = [PartnerBenefitInline]
    readonly_fields = ('foto_atual',)
    fieldsets = (
        ('Contatos', {
            'classes': ['tab'],
            'description': 'Aparecem no topo, no rodapé, na página Contato, na Política de Privacidade e '
                           'no botão de inscrições. Trocar aqui atualiza o site inteiro.',
            'fields': (
                'email',
                ('instagram_url', 'instagram_label'),
                ('linkedin_url', 'linkedin_label'),
                ('github_url', 'github_label'),
            ),
        }),
        ('Home', {
            'classes': ['tab'],
            'description': 'Textos da página inicial. As estatísticas ficam em Estatísticas, e os programas, '
                           'os membros e os parceiros vêm dos próprios cadastros.',
            'fields': (
                'home_hero_title', 'home_statement',
                'home_about_title', 'home_about_title_highlight', 'home_about_text',
                'home_about_photo', 'foto_atual', 'home_about_photo_alt',
                'mission', 'mission_how', 'mission_goal',
                'home_cta_title',
            ),
        }),
        ('Rodapé', {
            'classes': ['tab'],
            'fields': ('footer_tagline',),
        }),
        ('Páginas', {
            'classes': ['tab'],
            'description': 'O texto que aparece logo abaixo do título de cada página.',
            'fields': (
                'team_lead', 'partners_lead', 'partners_benefits_title',
                'projects_lead', 'featured_program_slug',
                'articles_lead', 'contact_lead',
                'process_lead', 'process_closed_message',
            ),
        }),
        ('Política de Privacidade', {
            'classes': ['tab'],
            'fields': ('privacy_updated', 'privacy_text'),
        }),
    )

    @admin.display(description='Foto atual')
    def foto_atual(self, obj):
        return miniatura(obj.home_about_photo, 120)

    # Registro único: não há lista, nem adicionar, nem excluir. Abrir o item
    # no menu leva direto para a edição.
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('admin:website_siteconfig_change', args=[SiteConfig.get_solo().pk]))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# ---------------------------------------------------------------------------
# Textos do site (títulos de seção, rótulos, botões e mensagens)
# ---------------------------------------------------------------------------

class SiteTextForm(forms.ModelForm):
    class Meta:
        model = SiteText
        fields = ('value',)

    def clean_value(self):
        valor = self.cleaned_data['value']
        original = PADRAO_TEXTOS.get(self.instance.key, '')
        faltando = sorted(set(re.findall(r'\{\w+\}', original)) - set(re.findall(r'\{\w+\}', valor)))
        if faltando:
            raise forms.ValidationError(
                'Mantenha no texto: ' + ', '.join(faltando) + '. O site preenche esses trechos.'
            )
        return valor


@admin.register(SiteText)
class SiteTextAdmin(ModelAdmin):
    list_display = ('group', 'description', 'value')
    list_display_links = ('description',)
    list_editable = ('value',)
    list_filter = ('group',)
    search_fields = ('key', 'description', 'value')
    list_per_page = 200
    ordering = ('order',)
    actions = ['restaurar']
    readonly_fields = ('group', 'description', 'key')
    fields = ('group', 'description', 'key', 'value')

    def get_changelist_form(self, request, **kwargs):
        return SiteTextForm

    def get_form(self, request, obj=None, **kwargs):
        kwargs['form'] = SiteTextForm
        return super().get_form(request, obj, **kwargs)

    # As entradas vêm do catálogo no código: aqui só se edita o texto.
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='Restaurar texto original')
    def restaurar(self, request, queryset):
        n = 0
        for texto in queryset:
            original = PADRAO_TEXTOS.get(texto.key)
            if original is not None and texto.value != original:
                texto.value = original
                texto.save(update_fields=['value'])
                n += 1
        self.message_user(request, f'{n} texto(s) restaurado(s) ao original.', messages.SUCCESS)
