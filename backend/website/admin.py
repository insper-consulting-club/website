from django import forms
from django.conf import settings
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import UploadedFile
from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
import re

from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.text import capfirst
from django.utils.html import format_html
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import action as acao_unfold
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .site_texts import PADRAO as PADRAO_TEXTOS
from .widgets import MarkdownPreviewWidget
from .models import (
    PartnerCategory, ProgramComponent,
    Partner, Member, Article, ArticleImage, Position, Directorate,
    DirectorateMembership, Statistic,
    Project, ProjectImage, ProjectTimelineEvent, ProjectContentBlock,
    Program,
    ProgramCase, ProgramCaseParticipant,
    SelectionProcess, SelectionProcessStage, SelectionProcessStep,
    SelectionProcessRequirement, PreparationMaterial, PreparationMaterialItem,
    SiteConfig, PartnerBenefit, ProgramContentBlock, SiteText, NavItem, MemberTrajectory,
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


ACOES_DE_PERMISSAO = {'add': 'adicionar', 'change': 'alterar', 'delete': 'remover', 'view': 'ver'}


def rotulo_da_permissao(permissao):
    """
    Nome da permissão em português para as listas de permissões de usuários e grupos. O
    Django guarda os nomes em inglês ("Can add group") no momento em que cria a permissão.
    """
    acao = permissao.codename.split('_', 1)[0]
    modelo = permissao.content_type.model_class()
    if acao not in ACOES_DE_PERMISSAO or modelo is None:
        return permissao.name
    return f'{modelo._meta.app_config.verbose_name} · {capfirst(modelo._meta.verbose_name)} · pode {ACOES_DE_PERMISSAO[acao]}'


class PermissoesEmPortuguesMixin:
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        campo = super().formfield_for_manytomany(db_field, request, **kwargs)
        if campo is not None and db_field.name in ('user_permissions', 'permissions'):
            campo.label_from_instance = rotulo_da_permissao
        return campo


@admin.register(User)
class UserAdmin(PermissoesEmPortuguesMixin, BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(PermissoesEmPortuguesMixin, BaseGroupAdmin, ModelAdmin):
    pass


def url_do_site(caminho):
    """Endereço público de uma página do site, ou None se FRONTEND_URL não estiver definido."""
    base = settings.FRONTEND_URL.rstrip('/')
    return f'{base}{caminho}' if base else None


def miniatura(imagem, altura=40):
    """Mostra a imagem pequena nas listas e no formulário do admin."""
    if not imagem:
        return '—'
    return format_html(
        '<img src="{}" style="height:{}px;border-radius:4px;object-fit:cover">',
        imagem.url, altura,
    )


class TextoCompactoMixin:
    """
    Deixa as caixas de texto com poucas linhas, em vez da altura padrão (que faz
    uma descrição de uma frase ocupar meia tela). Em linhas_dos_campos, cada campo
    recebe o número de linhas desejado.
    """
    linhas_dos_campos = {}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        campo = super().formfield_for_dbfield(db_field, request, **kwargs)
        linhas = self.linhas_dos_campos.get(db_field.name)
        if campo is not None and linhas:
            campo.widget.attrs['rows'] = linhas
        return campo


class AvisoDeAtrasoMixin:
    """
    Depois de salvar, avisa que a mudança pode levar um pouco para aparecer no site: a API
    deixa o navegador de quem visita reaproveitar as respostas por API_CACHE_SECONDS. Sem o
    aviso, quem edita acha que a mudança não pegou. Só uma mensagem por requisição, mesmo
    que a lista salve várias linhas de uma vez.
    """

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        segundos = settings.API_CACHE_SECONDS
        if segundos <= 0 or getattr(request, '_aviso_de_atraso', False):
            return
        request._aviso_de_atraso = True
        if segundos < 60:
            tempo = f'{segundos} segundos'
        elif segundos % 60 == 0:
            tempo = '1 minuto' if segundos == 60 else f'{segundos // 60} minutos'
        else:
            tempo = f'{segundos} segundos'
        self.message_user(
            request,
            f'A mudança aparece no site em até {tempo}: o navegador de quem visita guarda as respostas por esse tempo.',
            messages.INFO,
        )


class AdminDoSite(AvisoDeAtrasoMixin, TextoCompactoMixin, ModelAdmin):
    """Base dos admins de conteúdo do site (não vale para Usuários e Grupos)."""


# ---------------------------------------------------------------------------
# Parceiros
# ---------------------------------------------------------------------------

@admin.register(PartnerCategory)
class PartnerCategoryAdmin(AdminDoSite):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(Partner)
class PartnerAdmin(AdminDoSite):
    list_display = ('logo', 'name', 'category', 'is_active')
    list_display_links = ('logo', 'name')
    list_editable = ('is_active',)
    ordering_field = 'order'
    hide_ordering_field = True
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    fields = ('name', 'logo_url', 'category', 'site', 'description', 'is_active', 'order')
    linhas_dos_campos = {'description': 4}

    @admin.display(description='Logo')
    def logo(self, obj):
        return miniatura(obj.logo_url)

    def view_on_site(self, obj):
        return url_do_site(f'/parceiros/{obj.pk}') if obj.is_active else None


# ---------------------------------------------------------------------------
# Equipe
# ---------------------------------------------------------------------------

@admin.register(Position)
class PositionAdmin(AdminDoSite):
    list_display = ('title', 'power')
    list_editable = ('power',)
    search_fields = ('title',)
    ordering = ('power', 'title')


@admin.register(Directorate)
class DirectorateAdmin(AdminDoSite):
    list_display = ('name',)
    ordering_field = 'order'
    hide_ordering_field = True
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
    ordering_field = 'order'
    hide_ordering_field = True
    tab = True


class MemberTrajectoryInline(TabularInline):
    # Uma linha por semestre, em ordem de semestre no perfil público.
    model = MemberTrajectory
    extra = 1
    fields = ('semester', 'role')
    tab = True


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
class MemberAdmin(AdminDoSite):
    form = MemberForm
    inlines = [MemberTrajectoryInline, DirectorateMembershipInline]
    list_display = ('foto', 'name', 'get_directorates', 'position', 'course', 'year', 'atual')
    list_display_links = ('foto', 'name')
    list_filter = (SituacaoFilter, 'directorate_memberships__directorate', 'position', 'year')
    # Exigido pelo autocomplete de participantes dos cases, e útil por si só
    # quando a lista acumula alumni além dos membros ativos.
    search_fields = ('name', 'email', 'course', 'linkedin')
    list_select_related = ('position',)
    # Busca com seleção, em vez do seletor duplo, que não cabe na largura do formulário.
    autocomplete_fields = ('projects',)
    date_hierarchy = 'entry_date'
    list_per_page = 50
    actions = ['arquivar', 'reativar']
    linhas_dos_campos = {'biography': 3}
    fieldsets = (
        (None, {'fields': ('name', 'photo', 'position', 'linkedin', 'email')}),
        ('Formação', {'fields': ('course', 'year')}),
        ('No ICC', {'fields': ('entry_date', 'exit_date', 'biography', 'hours', 'projects')}),
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

    @admin.display(description='Atual', boolean=True)
    def atual(self, obj):
        return obj.exit_date is None

    @admin.action(description='Arquivar selecionados (sai da página Equipe)', permissions=['change'])
    def arquivar(self, request, queryset):
        n = queryset.filter(exit_date__isnull=True).update(exit_date=timezone.localdate())
        self.message_user(request, f'{n} membro(s) arquivado(s). O histórico continua guardado.', messages.SUCCESS)

    @admin.action(description='Reativar selecionados (volta para a página Equipe)', permissions=['change'])
    def reativar(self, request, queryset):
        n = queryset.exclude(exit_date__isnull=True).update(exit_date=None)
        self.message_user(request, f'{n} membro(s) reativado(s).', messages.SUCCESS)

    def view_on_site(self, obj):
        # O perfil de quem saiu continua acessível por link, então o botão vale para todos.
        return url_do_site(f'/equipe/{obj.pk}')


# ---------------------------------------------------------------------------
# Projetos
# ---------------------------------------------------------------------------

class ProjectImageInline(TabularInline):
    model = ProjectImage
    extra = 1
    fields = ('image', 'caption', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    tab = True


class ProjectTimelineEventInline(TextoCompactoMixin, TabularInline):
    model = ProjectTimelineEvent
    extra = 1
    fields = ('date', 'title', 'description', 'order')
    ordering = ('order',)
    linhas_dos_campos = {'description': 2}
    tab = True


class ProjectContentBlockInline(TextoCompactoMixin, StackedInline):
    model = ProjectContentBlock
    extra = 1
    fields = ('title', 'text', 'image', 'image_caption', 'image_align', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    linhas_dos_campos = {'text': 6}
    tab = True


@admin.register(Project)
class ProjectAdmin(AdminDoSite):
    list_display = ('title', 'program', 'start_date', 'end_date', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'program', 'start_date')
    search_fields = ('title', 'description')
    # Busca com seleção, em vez do seletor duplo, que não cabe na largura do formulário.
    autocomplete_fields = ('partners',)
    linhas_dos_campos = {'description': 4}
    fieldsets = (
        (None, {'fields': ('title', 'description', 'program', 'partners', 'start_date', 'end_date', 'is_active')}),
    )
    date_hierarchy = 'start_date'
    list_select_related = ('program',)
    actions = ['arquivar', 'reativar']
    inlines = [ProjectImageInline, ProjectTimelineEventInline, ProjectContentBlockInline]

    @admin.action(description='Arquivar selecionados (somem do site)', permissions=['change'])
    def arquivar(self, request, queryset):
        n = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(request, f'{n} projeto(s) arquivado(s). O histórico continua guardado.', messages.SUCCESS)

    @admin.action(description='Reativar selecionados (voltam para o site)', permissions=['change'])
    def reativar(self, request, queryset):
        n = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f'{n} projeto(s) reativado(s).', messages.SUCCESS)

    def view_on_site(self, obj):
        return url_do_site(f'/projetos/projeto/{obj.pk}') if obj.is_active else None

# ---------------------------------------------------------------------------
# Programas e componentes
# ---------------------------------------------------------------------------

@admin.register(ProgramComponent)
class ProgramComponentAdmin(AdminDoSite):
    linhas_dos_campos = {'description': 3}
    list_display = ('title', 'program')
    list_filter = ('program',)
    search_fields = ('title', 'description')
    list_select_related = ('program',)


class ProgramContentBlockInline(TextoCompactoMixin, StackedInline):
    model = ProgramContentBlock
    extra = 0
    fields = ('title', 'text', 'image', 'image_caption', 'image_align', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    tab = True

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'text':
            kwargs['widget'] = MarkdownPreviewWidget(modo='programa')
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Program)
class ProgramAdmin(AdminDoSite):
    inlines = [ProgramContentBlockInline]
    linhas_dos_campos = {'description': 4, 'highlights': 4}
    fieldsets = (
        (None, {'fields': ('label', 'slug', 'subtitle', 'description', 'highlights', 'icon')}),
        ('Exibição no site', {'fields': ('badge', 'badge_class', 'signup_url', 'is_active', 'order')}),
    )
    list_display = ('label', 'slug', 'badge', 'is_active')
    list_editable = ('is_active',)
    ordering_field = 'order'
    hide_ordering_field = True
    list_filter = ('is_active',)
    search_fields = ('label', 'slug', 'description')
    ordering = ('order',)
    prepopulated_fields = {'slug': ('label',)}

    def view_on_site(self, obj):
        return url_do_site(f'/projetos/{obj.slug}') if obj.is_active else None

# ---------------------------------------------------------------------------
# Home e notícias
# ---------------------------------------------------------------------------

@admin.register(Statistic)
class StatisticAdmin(AdminDoSite):
    list_display = ('value', 'description')
    ordering_field = 'order'
    hide_ordering_field = True
    search_fields = ('value', 'description')
    ordering = ('order',)


class ArticleImageInline(TabularInline):
    model = ArticleImage
    extra = 1
    fields = ('number', 'image', 'caption')
    ordering = ('number',)
    tab = True


@admin.register(Article)
class ArticleAdmin(AdminDoSite):
    linhas_dos_campos = {'description': 4}
    # O endereço do artigo é sugerido a partir do título (e pode ser trocado).
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'authors', 'topics', 'description', 'content')}),
        ('Publicação', {'fields': ('published', 'date', 'order', 'source', 'link', 'image')}),
    )
    actions = ['publicar', 'despublicar']
    list_display = ('title', 'slug', 'authors', 'published', 'date', 'order')
    search_fields = ('title', 'slug', 'authors', 'topics', 'description', 'content', 'source')
    list_editable = ('published', 'order')
    list_filter = ('published', 'source', 'date')
    date_hierarchy = 'date'
    ordering = ('-date', 'order')
    inlines = [ArticleImageInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'content':
            kwargs['widget'] = MarkdownPreviewWidget(modo='artigo', imagens=self._imagens_do_artigo(request))
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def _imagens_do_artigo(self, request):
        # Imagens já salvas do artigo, para a prévia trocar ![](imagem-N) pela foto.
        # A foto de um artigo novo, ainda sem registro, só aparece depois de salvar.
        id_do_artigo = (request.resolver_match.kwargs or {}).get('object_id') if request.resolver_match else None
        if not id_do_artigo or not str(id_do_artigo).isdigit():
            return []
        return [
            {'number': imagem.number, 'image_url': request.build_absolute_uri(imagem.image.url), 'caption': imagem.caption}
            for imagem in ArticleImage.objects.filter(article_id=int(id_do_artigo))
        ]

    @admin.action(description='Publicar selecionados (aparecem no site)', permissions=['change'])
    def publicar(self, request, queryset):
        n = queryset.filter(published=False).update(published=True)
        sem_data = queryset.filter(date__isnull=True).count()
        self.message_user(request, f'{n} artigo(s) publicado(s).', messages.SUCCESS)
        if sem_data:
            self.message_user(
                request,
                f'{sem_data} artigo(s) selecionado(s) estão sem data de publicação: a ordem na lista do site '
                'depende dela. Preencha a data em cada um.',
                messages.WARNING,
            )

    @admin.action(description='Despublicar selecionados (voltam a rascunho)', permissions=['change'])
    def despublicar(self, request, queryset):
        n = queryset.filter(published=True).update(published=False)
        self.message_user(request, f'{n} artigo(s) despublicado(s). O texto continua guardado como rascunho.', messages.SUCCESS)

    def view_on_site(self, obj):
        # Rascunho responde 404 no site.
        return url_do_site(f'/artigos/{obj.slug or obj.pk}') if obj.published else None

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
class ProgramCaseAdmin(AdminDoSite):
    inlines = [ProgramCaseParticipantInline]
    linhas_dos_campos = {'theme': 3, 'panel': 3}
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
    ordering_field = 'order'
    hide_ordering_field = True
    tab = True


class SelectionProcessStepInline(TextoCompactoMixin, StackedInline):
    model = SelectionProcessStep
    extra = 0
    fields = ('number', 'title', 'description', 'image', 'duration', 'tips', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    linhas_dos_campos = {'description': 3, 'tips': 4}
    tab = True


class SelectionProcessRequirementInline(TabularInline):
    model = SelectionProcessRequirement
    extra = 1
    fields = ('text', 'icon', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    tab = True


@admin.register(SelectionProcess)
class SelectionProcessAdmin(AdminDoSite):
    fieldsets = (
        (None, {'fields': ('title', 'is_active', 'registrations_open', 'registration_url')}),
    )
    list_display = ('title', 'is_active', 'registrations_open')
    list_editable = ('is_active', 'registrations_open')
    list_filter = ('is_active',)
    search_fields = ('title',)
    actions = ['duplicar']
    actions_detail = ['duplicar_este']
    inlines = [SelectionProcessStageInline, SelectionProcessStepInline,
               SelectionProcessRequirementInline]

    @admin.action(description='Duplicar selecionados (cópia inativa, para o próximo semestre)', permissions=['add'])
    def duplicar(self, request, queryset):
        copias = [processo.duplicate() for processo in queryset]
        self.message_user(
            request,
            f'{len(copias)} processo(s) duplicado(s). As cópias estão inativas e com as inscrições fechadas: '
            'ajuste as datas, preencha o link do formulário e ative quando for a hora.',
            messages.SUCCESS,
        )

    @acao_unfold(description='Duplicar este processo', icon='content_copy', permissions=['website.add_selectionprocess'])
    def duplicar_este(self, request, object_id):
        copia = SelectionProcess.objects.get(pk=object_id).duplicate()
        self.message_user(
            request,
            'Cópia criada. Ela está inativa e com as inscrições fechadas: ajuste as datas, preencha o link do '
            'formulário e ative quando for a hora.',
            messages.SUCCESS,
        )
        return redirect(reverse('admin:website_selectionprocess_change', args=[copia.pk]))

    def view_on_site(self, obj):
        return url_do_site('/processo') if obj.is_active else None

class PreparationMaterialItemInline(TabularInline):
    model = PreparationMaterialItem
    extra = 1
    fields = ('text', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True


@admin.register(PreparationMaterial)
class PreparationMaterialAdmin(AdminDoSite):
    list_display = ('title', 'process')
    ordering_field = 'order'
    hide_ordering_field = True
    list_filter = ('process',)
    search_fields = ('title',)
    inlines = [PreparationMaterialItemInline]


# ---------------------------------------------------------------------------
# Configuração do site (textos e contatos que não pertencem a outro cadastro)
# ---------------------------------------------------------------------------

class PartnerBenefitInline(TextoCompactoMixin, TabularInline):
    model = PartnerBenefit
    extra = 0
    fields = ('title', 'description', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    linhas_dos_campos = {'description': 2}
    tab = True


class SiteConfigForm(forms.ModelForm):
    """Confere o formato das imagens de marca no momento do envio."""

    class Meta:
        model = SiteConfig
        fields = '__all__'

    @staticmethod
    def _medidas(arquivo):
        # Só confere o que acabou de ser enviado. Uma imagem já salva (FieldFile) ou
        # a opção de remover não passam por aqui, e abrir uma imagem guardada no
        # Cloudinary só para medir seria um acesso de rede desnecessário.
        if not isinstance(arquivo, UploadedFile):
            return None
        return get_image_dimensions(arquivo)

    def clean_favicon(self):
        arquivo = self.cleaned_data.get('favicon')
        medidas = self._medidas(arquivo)
        if medidas:
            largura, altura = medidas
            if largura != altura:
                raise forms.ValidationError(
                    f'O ícone precisa ser quadrado, mas a imagem enviada tem {largura} x {altura} pixels. '
                    'Recorte-a para um quadrado (de preferência 256 x 256).'
                )
            if largura < 32:
                raise forms.ValidationError(
                    f'O ícone está pequeno demais ({largura} x {altura} pixels). Use pelo menos 32 x 32.'
                )
        return arquivo

    def clean_og_image(self):
        arquivo = self.cleaned_data.get('og_image')
        medidas = self._medidas(arquivo)
        if medidas:
            largura, altura = medidas
            proporcao = largura / altura if altura else 0
            if largura < 600:
                raise forms.ValidationError(
                    f'A imagem de compartilhamento está pequena demais ({largura} x {altura} pixels). '
                    'Use pelo menos 600 de largura; o ideal é 1200 x 630.'
                )
            if not 1.6 <= proporcao <= 2.2:
                raise forms.ValidationError(
                    f'A proporção da imagem ({largura} x {altura} pixels) é muito diferente da usada pelo '
                    'WhatsApp e pelo LinkedIn, e ela seria cortada. Use 1200 x 630.'
                )
        return arquivo


class NavItemInline(TabularInline):
    model = NavItem
    extra = 0
    fields = ('label', 'area', 'page', 'url', 'order', 'is_active')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    tab = True


@admin.register(SiteConfig)
class SiteConfigAdmin(AdminDoSite):
    form = SiteConfigForm
    linhas_dos_campos = {'home_about_text': 4, 'mission': 3, 'mission_how': 3, 'mission_goal': 3}
    inlines = [NavItemInline, PartnerBenefitInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'privacy_text':
            kwargs['widget'] = MarkdownPreviewWidget(modo='politica')
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    fieldsets = (
        ('Marca e compartilhamento', {
            'classes': ['tab'],
            'description': 'Nome, descrição e imagens do site. Mudanças aqui só aparecem na prévia dos links '
                           '(WhatsApp, LinkedIn) e no ícone da aba depois que o site é reconstruído, o que o '
                           'sistema pede sozinho ao salvar.',
            'fields': (
                'site_name', 'site_description',
                'logo', 'favicon', 'og_image',
            ),
        }),
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
                'home_about_photo', 'home_about_photo_alt',
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

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if set(form.changed_data) & set(SiteConfig.CAMPOS_DO_HTML):
            if settings.RENDER_FRONTEND_DEPLOY_HOOK:
                aviso = 'O site será reconstruído para aplicar a mudança na marca ou na prévia dos links. ' \
                        'Leva alguns minutos.'
            else:
                aviso = 'Para aplicar a mudança na marca ou na prévia dos links, é preciso publicar o ' \
                        'frontend de novo (o deploy automático não está configurado).'
            self.message_user(request, aviso, messages.WARNING)

    # Registro único: não há lista, nem adicionar, nem excluir. Abrir o item
    # no menu leva direto para a edição.
    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('admin:website_siteconfig_change', args=[SiteConfig.get_solo().pk]))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def view_on_site(self, obj):
        return url_do_site('/')

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
class SiteTextAdmin(AdminDoSite):
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

    @admin.action(description='Restaurar texto original', permissions=['change'])
    def restaurar(self, request, queryset):
        n = 0
        for texto in queryset:
            original = PADRAO_TEXTOS.get(texto.key)
            if original is not None and texto.value != original:
                texto.value = original
                texto.save(update_fields=['value'])
                n += 1
        self.message_user(request, f'{n} texto(s) restaurado(s) ao original.', messages.SUCCESS)
