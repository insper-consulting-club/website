from django import forms
from django.forms import BaseInlineFormSet
from django.conf import settings
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import UploadedFile
from django.contrib import admin, messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
import json
import re
from collections import Counter
import unicodedata

from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.filters.admin import DropdownFilter
from unfold.decorators import action as acao_unfold
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextareaWidget, UnfoldAdminTextInputWidget

from .conteudo import PADRAO as PADRAO_DOS_TEXTOS, PAGINAS, POR_CHAVE, POR_SLUG
from .autores import normaliza
from .conteudo.base import Pagina
from .widgets import MarkdownPreviewWidget
from . import citacao
from .models import (
    PartnerCategory, ProgramComponent, SecaoDaHome, ArticleAuthor,
    Partner, Member, Article, ArticleImage, Position, Directorate,
    DirectorateMembership, Statistic,
    Project, ProjectImage, ProjectTimelineEvent, ProjectContentBlock,
    Program,
    ProgramCase, ProgramCaseParticipant,
    SelectionProcess, SelectionProcessStage, SelectionProcessStep,
    SelectionProcessRequirement, PreparationMaterial, PreparationMaterialItem,
    SiteConfig, PartnerBenefit, ProgramContentBlock, SiteText, NavItem, MemberTrajectory, PaginaDoSite,
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


ACOES_DE_PERMISSAO = {
    'add': 'Pode adicionar',
    'change': 'Pode alterar',
    'delete': 'Pode excluir',
    'view': 'Pode ver',
}


def rotulo_da_permissao(permissao):
    """O Django guarda o nome das permissões em inglês ("Can add Artigo"); aqui elas aparecem em português."""
    acao = permissao.codename.split('_', 1)[0]
    return f'{permissao.content_type} | {ACOES_DE_PERMISSAO.get(acao, permissao.name)}'


class RotulosDePermissaoMixin:
    """Mostra as permissões em português nas listas de escolha de Usuários e Grupos."""

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        campo = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name in ('permissions', 'user_permissions'):
            campo.queryset = campo.queryset.select_related('content_type')
            campo.label_from_instance = rotulo_da_permissao
        return campo


@admin.register(User)
class UserAdmin(RotulosDePermissaoMixin, BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(RotulosDePermissaoMixin, BaseGroupAdmin, ModelAdmin):
    pass


# Nomes em português para a página e para as permissões (o padrão do Django é "entrada de log").
LogEntry._meta.verbose_name = 'atividade'
LogEntry._meta.verbose_name_plural = 'atividades'


@admin.register(LogEntry)
class AtividadeRecenteAdmin(ModelAdmin):
    """Quem mudou o quê no admin, só para consulta. Só administradores veem esta página."""
    list_display = ('action_time', 'user', 'tipo', 'cadastro', 'registro', 'o_que_mudou')
    list_display_links = None
    list_filter = ('user', 'action_flag')
    search_fields = ('object_repr',)
    date_hierarchy = 'action_time'
    list_select_related = ('user', 'content_type')
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, {'title': 'Atividade recente', **(extra_context or {})})

    @admin.display(description='Ação')
    def tipo(self, obj):
        return obj.get_action_flag_display()

    @admin.display(description='Cadastro')
    def cadastro(self, obj):
        return str(obj.content_type.name).capitalize() if obj.content_type else '-'

    @admin.display(description='Registro')
    def registro(self, obj):
        return obj.object_repr

    @admin.display(description='O que mudou')
    def o_que_mudou(self, obj):
        return obj.get_change_message()


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


def secao_avancada(*campos):
    """
    Seção recolhida no fim do formulário, para o que quase nunca precisa de ajuste (endereço,
    ordem, estilo). Se algum campo dela der erro, o Django a abre sozinho.
    """
    return ('Avançado', {
        'classes': ['collapse'],
        'description': 'Normalmente não é preciso mexer aqui.',
        'fields': campos,
    })


class AbaOrdenavelTabular(TabularInline):
    """Aba do formulário (lista dentro do registro) cujas linhas se reordenam arrastando."""
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    tab = True


class AbaOrdenavelEmpilhada(StackedInline):
    """Igual a AbaOrdenavelTabular, para linhas com muitos campos (cada uma vira um bloco)."""
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    tab = True


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
    list_select_related = ('category',)
    ordering_field = 'order'
    hide_ordering_field = True
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')
    ordering = ('order', 'name')
    fieldsets = (
        (None, {'fields': ('name', 'logo_url', 'category', 'site', 'description', 'is_active')}),
        secao_avancada('order'),
    )
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

    def get_fields(self, request, obj=None):
        # A prioridade decide quem aparece como liderança na Home. Só administradores a escolhem:
        # um cargo criado por um editor entra como membro comum (valor padrão do modelo).
        return ('title', 'power') if request.user.is_superuser else ('title',)


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


class DirectorateMembershipInline(AbaOrdenavelTabular):
    model = DirectorateMembership
    form = DirectorateMembershipForm
    extra = 1
    fields = ('directorate', 'cargo', 'order')


class MemberTrajectoryInline(TabularInline):
    # Uma linha por semestre, em ordem de semestre no perfil público.
    model = MemberTrajectory
    extra = 1
    fields = ('semester', 'role')
    tab = True


class SituacaoFilter(admin.SimpleListFilter):
    """Separa membros atuais de ex-membros (quem foi arquivado em "Exibir na equipe")."""
    title = 'situação'
    parameter_name = 'situacao'

    def lookups(self, request, model_admin):
        return [('atual', 'Membros atuais'), ('ex', 'Ex-membros')]

    def queryset(self, request, queryset):
        if self.value() == 'atual':
            return queryset.filter(is_active=True)
        if self.value() == 'ex':
            return queryset.filter(is_active=False)
        return queryset


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = '__all__'
        labels = {
            'name': 'Nome',
            'photo': 'Foto',
            'position': 'Cargo principal',
            'is_active': 'Exibir na equipe',
        }
        help_texts = {
            'is_active': 'Desmarque quando a pessoa sair do clube: ela some da página Equipe, '
                         'mas o histórico continua guardado. Marque de novo para reativar.',
        }


@admin.register(Member)
class MemberAdmin(AdminDoSite):
    form = MemberForm
    inlines = [MemberTrajectoryInline, DirectorateMembershipInline]
    list_display = ('foto', 'name', 'get_directorates', 'position', 'is_active', 'id')
    list_display_links = ('foto', 'name')
    list_editable = ('is_active',)
    list_filter = (SituacaoFilter, 'directorate_memberships__directorate', 'position')
    # Exigido pelo autocomplete da equipe do projeto e dos participantes dos cases, e útil
    # por si só quando a lista acumula alumni além dos membros ativos.
    search_fields = ('name', 'linkedin')
    list_select_related = ('position',)
    # Quem está na equipe primeiro, e por ordem alfabética (o cadastro antigo ficava no fim).
    ordering = ('-is_active', 'name')
    list_per_page = 50
    actions = ['arquivar', 'reativar']
    fieldsets = (
        (None, {'fields': ('name', 'photo', 'position', 'linkedin', 'is_active')}),
        secao_avancada('citation_name'),
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

    @admin.action(description='Arquivar selecionados (sai da página Equipe)', permissions=['change'])
    def arquivar(self, request, queryset):
        n = queryset.filter(is_active=True).update(is_active=False)
        self.message_user(request, f'{n} membro(s) arquivado(s). O histórico continua guardado.', messages.SUCCESS)

    @admin.action(description='Reativar selecionados (volta para a página Equipe)', permissions=['change'])
    def reativar(self, request, queryset):
        n = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, f'{n} membro(s) reativado(s).', messages.SUCCESS)

    def view_on_site(self, obj):
        # O perfil de quem saiu continua acessível por link, então o botão vale para todos.
        return url_do_site(f'/equipe/{obj.pk}')


# ---------------------------------------------------------------------------
# Projetos
# ---------------------------------------------------------------------------

class ProjectImageInline(AbaOrdenavelTabular):
    model = ProjectImage
    extra = 1
    fields = ('image', 'caption', 'order')


class ProjectTimelineEventInline(TextoCompactoMixin, TabularInline):
    model = ProjectTimelineEvent
    extra = 1
    fields = ('date', 'title', 'description', 'order')
    ordering = ('order',)
    linhas_dos_campos = {'description': 2}
    tab = True


class ProjectContentBlockInline(TextoCompactoMixin, AbaOrdenavelEmpilhada):
    model = ProjectContentBlock
    extra = 1
    fields = ('title', 'text', 'image', 'image_caption', 'image_align', 'order')
    linhas_dos_campos = {'text': 6}


@admin.register(Project)
class ProjectAdmin(AdminDoSite):
    list_display = ('imagem', 'title', 'program', 'start_date', 'end_date', 'is_active')
    list_display_links = ('imagem', 'title')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'program', 'start_date')
    search_fields = ('title', 'description')
    list_select_related = ('program',)
    # Busca com seleção, em vez do seletor duplo, que não cabe na largura do formulário.
    autocomplete_fields = ('partners', 'members')
    linhas_dos_campos = {'description': 4}

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images')

    @admin.display(description='Imagem')
    def imagem(self, obj):
        # Usa a lista já carregada (prefetch) para não consultar o banco linha a linha.
        primeira = next(iter(obj.images.all()), None)
        return miniatura(primeira.image if primeira else None)
    fieldsets = (
        (None, {'fields': (
            'title', 'description', 'program', 'partners', 'members', 'start_date', 'end_date', 'is_active',
        )}),
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

class ProgramComponentInline(TextoCompactoMixin, TabularInline):
    """Os passos de "Como funciona" da página do programa."""
    model = ProgramComponent
    extra = 0
    fields = ('title', 'description')
    linhas_dos_campos = {'description': 3}
    tab = True


class ProgramContentBlockInline(TextoCompactoMixin, AbaOrdenavelEmpilhada):
    model = ProgramContentBlock
    extra = 0
    fields = ('title', 'text', 'image', 'image_caption', 'image_align', 'order')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'text':
            kwargs['widget'] = MarkdownPreviewWidget(modo='programa')
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Program)
class ProgramAdmin(AdminDoSite):
    inlines = [ProgramComponentInline, ProgramContentBlockInline]
    linhas_dos_campos = {'description': 4, 'highlights': 4}
    fieldsets = (
        (None, {'fields': ('label', 'slug', 'subtitle', 'description', 'highlights', 'icon')}),
        ('Exibição no site', {'fields': ('signup_url', 'is_active')}),
        secao_avancada('order'),
    )
    list_display = ('icone', 'label', 'slug', 'is_active')
    list_display_links = ('icone', 'label')
    list_editable = ('is_active',)
    ordering_field = 'order'
    hide_ordering_field = True
    list_filter = ('is_active',)
    search_fields = ('label', 'slug', 'description')
    ordering = ('order',)
    prepopulated_fields = {'slug': ('label',)}

    @admin.display(description='Ícone')
    def icone(self, obj):
        return miniatura(obj.icon)

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


class ImagemDoArtigoFormSet(BaseInlineFormSet):
    """Numera sozinho as imagens novas que ficaram sem número, sem repetir um número já usado."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        usados = [
            f.cleaned_data.get('number') for f in self.forms
            if f.cleaned_data and not f.cleaned_data.get('DELETE')
        ]
        proximo = max([n for n in usados if n] or [0]) + 1
        for form in self.forms:
            dados = form.cleaned_data
            if not dados or dados.get('DELETE') or dados.get('number') or not form.has_changed():
                continue
            form.instance.number = dados['number'] = proximo
            proximo += 1


class ArticleImageInline(TabularInline):
    model = ArticleImage
    formset = ImagemDoArtigoFormSet
    extra = 1
    fields = ('number', 'image', 'caption', 'trecho')
    readonly_fields = ('trecho',)
    ordering = ('number',)
    tab = True

    @admin.display(description='Para colar no texto')
    def trecho(self, obj):
        if not obj or not obj.pk:
            return 'Aparece depois de salvar'
        codigo = f'![](imagem-{obj.number})'
        # Se o número aparece no texto salvo, a imagem está em uso; senão, o editor ainda precisa colocá-la no texto.
        usadas = {int(n) for n in re.findall(r'!\[[^\]]*\]\(imagem-(\d+)\)', obj.article.content or '')}
        uso = 'Usada no texto' if obj.number in usadas else 'Ainda não usada no texto'
        return format_html(
            '<code>{}</code> <button type="button" class="copiar-trecho" data-trecho="{}" '
            'onclick="navigator.clipboard.writeText(this.dataset.trecho);this.textContent=\'Copiado\'">Copiar</button>'
            '<br><small class="texto-original">{}</small>',
            codigo, codigo, uso,
        )


class CampoDeAutor(UnfoldAdminTextInputWidget):
    """
    Campo de texto do nome do autor, com uma lista de membros que se filtra enquanto se digita (ver autor_combobox.js).
    Escolher um membro grava o ID dele no campo oculto "Membro"; qualquer outro texto é um autor de fora. A lista vai
    embutida no campo, para o filtro ignorar acentos sem pedir nada ao servidor.
    """

    class Media:
        js = ('website/autor_combobox.js',)

    def __init__(self, membros=(), attrs=None):
        super().__init__(attrs)
        self.membros = list(membros)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.update({
            'class': f"{attrs.get('class', '')} autor-combobox__input".strip(),
            'data-membros': json.dumps(self.membros, ensure_ascii=False),
            'autocomplete': 'off',
            'role': 'combobox',
            'aria-autocomplete': 'list',
            'aria-expanded': 'false',
        })
        return attrs


class CampoDeTemas(UnfoldAdminTextInputWidget):
    """
    Campo de temas separados por vírgula que sugere os temas já usados em outros artigos (ver temas_sugestoes.js), para
    não nascer "Varejo" e "varejo" como dois temas.
    """

    class Media:
        js = ('website/temas_sugestoes.js',)

    def __init__(self, temas=(), attrs=None):
        super().__init__(attrs)
        self.temas = list(temas)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs.update({
            'class': f"{attrs.get('class', '')} temas-sugestoes__input".strip(),
            'data-temas': json.dumps(self.temas, ensure_ascii=False),
            'autocomplete': 'off',
        })
        return attrs


def temas_ja_usados():
    """Os temas dos artigos, sem repetir (ignorando acento e maiúscula) e com a grafia mais usada, do mais ao menos comum."""
    contagem = {}
    for texto in Article.objects.values_list('topics', flat=True):
        for tema in (t.strip() for t in (texto or '').split(',')):
            if tema:
                contagem.setdefault(normaliza(tema), Counter())[tema] += 1
    ordenados = sorted(contagem.values(), key=lambda grafias: (-sum(grafias.values()), grafias.most_common(1)[0][0].lower()))
    return [grafias.most_common(1)[0][0] for grafias in ordenados]


class AutoresDoArtigoFormSet(BaseInlineFormSet):
    """Um artigo publicado precisa de ao menos um autor."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        linhas = sum(1 for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE'))
        # Os campos do artigo chegam no mesmo envio do formulário; marcado, o checkbox vem como "on".
        publicado = self.data.get('published') in ('on', 'true', 'True', '1')
        self._ordena_os_novos()
        if publicado and not linhas:
            raise forms.ValidationError('Um artigo publicado precisa de ao menos um autor.')


    def _ordena_os_novos(self):
        """Uma linha nova que ainda não foi arrastada (ordem 0) entra no fim, depois dos autores que já estavam."""
        vivos = [f for f in self.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]
        proximo = max([f.instance.order for f in vivos if f.instance.pk] or [-1]) + 1
        for form in vivos:
            if not form.instance.pk and not form.cleaned_data.get('order'):
                form.instance.order = form.cleaned_data['order'] = proximo
                proximo += 1


def rotulos_dos_membros():
    """
    O texto de cada membro na lista de escolha. Só o nome, a menos que haja homônimos (nomes iguais sem contar acento nem
    maiúscula): aí entra o ID, que é o que garante que nunca haja duas linhas iguais. Cargo e situação não servem para
    distinguir: há quem acumule cargos, e o cargo principal sozinho enganaria. Ex.: "Ana Silva (ID 12)".
    """
    membros = list(Member.objects.order_by('name'))
    grupos = {}
    for membro in membros:
        grupos.setdefault(normaliza(membro.name), []).append(membro)
    return {
        membro.pk: membro.name if len(grupos[normaliza(membro.name)]) == 1 else f'{membro.name} (ID {membro.pk})'
        for membro in membros
    }


class AutoresDoArtigoInline(AbaOrdenavelTabular):
    model = ArticleAuthor
    formset = AutoresDoArtigoFormSet
    extra = 1
    fields = ('name', 'member')
    tab = False  # fica no formulário, e não numa aba: o autor é parte do que se preenche para publicar
    logo_apos_o_primeiro_grupo = True  # desenhado por artigo_change_form.html, abaixo do título e do slug

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'member':
            # Campo oculto: o vínculo vem da escolha na lista do campo de nome, e não de um segundo campo para preencher.
            return forms.ModelChoiceField(queryset=Member.objects.all(), required=False, widget=forms.HiddenInput)
        if db_field.name == 'name':
            rotulos = rotulos_dos_membros()
            membros = [
                {'id': m.pk, 'nome': m.name, 'rotulo': rotulos[m.pk], 'ex': not m.is_active}
                for m in Member.objects.order_by('name')
            ]
            kwargs['widget'] = CampoDeAutor(membros)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class FormDaListaDeArtigos(forms.ModelForm):
    """Publicar pela lista (caixa "Publicado") também exige autor e data, como no formulário do artigo."""

    def clean(self):
        dados = super().clean()
        artigo = self.instance
        if dados.get('published') and artigo.pk and not artigo.article_authors.exists():
            self.add_error('published', 'Adicione os autores antes de publicar.')
        if dados.get('published') and artigo.pk and not artigo.date:
            self.add_error('published', 'Preencha a data de publicação do artigo antes de publicar.')
        return dados


class AutorDoArtigoFilter(DropdownFilter):
    """Os artigos de um autor: um membro (com o ID, se houver homônimos) ou alguém de fora."""
    title = 'autor'
    parameter_name = 'autor'

    def lookups(self, request, model_admin):
        rotulos = rotulos_dos_membros()
        autores = {}
        for autor in ArticleAuthor.objects.all():
            if autor.member_id:
                autores[f'm{autor.member_id}'] = rotulos.get(autor.member_id, autor.display_name)
            else:
                autores.setdefault(f'n{normaliza(autor.display_name)}', autor.display_name)
        opcoes = sorted(autores.items(), key=lambda par: normaliza(par[1]))
        return opcoes

    def queryset(self, request, queryset):
        valor = self.value()
        if not valor:
            return queryset
        if valor.startswith('m') and valor[1:].isdigit():
            return queryset.filter(article_authors__member_id=int(valor[1:])).distinct()
        ids = [a.pk for a in ArticleAuthor.objects.filter(member__isnull=True) if f'n{normaliza(a.display_name)}' == valor]
        return queryset.filter(article_authors__in=ids).distinct()


class TemaDoArtigoFilter(DropdownFilter):
    """Os artigos de um tema. Os temas são os já usados (sem repetir "Varejo" e "varejo") e o texto é separado por vírgula."""
    title = 'tema'
    parameter_name = 'tema'

    def lookups(self, request, model_admin):
        return [(normaliza(tema), tema) for tema in sorted(temas_ja_usados(), key=normaliza)]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        ids = [
            pk for pk, temas in Article.objects.values_list('pk', 'topics')
            if self.value() in {normaliza(t) for t in (temas or '').split(',')}
        ]
        return queryset.filter(pk__in=ids)


@admin.register(Article)
class ArticleAdmin(AdminDoSite):
    linhas_dos_campos = {'description': 4}
    # O endereço do artigo é sugerido a partir do título (e pode ser trocado).
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        (None, {'fields': ('pendencias', 'title', 'slug')}),
        (None, {'fields': ('topics', 'description', 'content')}),
        ('Publicação', {'fields': ('published', 'date', 'image')}),
        ('Como será citado', {'fields': ('previa_da_citacao',), 'classes': ('collapse',)}),
        secao_avancada('order'),
    )
    readonly_fields = ('pendencias', 'previa_da_citacao')
    actions = ['publicar', 'despublicar']
    list_display = ('capa', 'title', 'slug', 'autores', 'published', 'date', 'order')
    list_display_links = ('capa', 'title')
    search_fields = ('title', 'slug', 'article_authors__name', 'topics', 'description', 'content')
    list_editable = ('published', 'order')
    list_filter = ('published', AutorDoArtigoFilter, TemaDoArtigoFilter, 'date')
    date_hierarchy = 'date'
    ordering = ('-date', 'order')
    change_form_template = 'website/admin/artigo_change_form.html'
    inlines = [AutoresDoArtigoInline, ArticleImageInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('article_authors')

    def get_changelist_form(self, request, **kwargs):
        return super().get_changelist_form(request, form=FormDaListaDeArtigos, **kwargs)

    @admin.display(description='Capa')
    def capa(self, obj):
        return miniatura(obj.image)

    @admin.display(description='Para publicar')
    def pendencias(self, obj):
        """O que falta no artigo salvo, para o editor não descobrir por erro na hora de publicar."""
        if obj is None or not obj.pk:
            return 'Salve o rascunho para ver aqui o que falta para publicar.'
        itens = []
        if not obj.article_authors.exists():
            itens.append(('falta', 'Falta ao menos um autor.'))
        enviadas = set(obj.images.values_list('number', flat=True))
        citadas = {int(n) for n in re.findall(r'!\[[^\]]*\]\(imagem-(\d+)\)', obj.content or '')}
        for numero in sorted(citadas - enviadas):
            itens.append(('falta', f'O texto pede a imagem {numero}, que não foi enviada em “Imagens do artigo”.'))
        if not obj.image:
            itens.append(('sugestao', 'Sem imagem de capa, o cartão do artigo na lista mostra só “ICC”.'))
        if not itens:
            return mark_safe('<span class="pendencias pendencias--ok">Tudo pronto para publicar.</span>')
        return format_html(
            '<ul class="pendencias">{}</ul>',
            format_html_join('', '<li class="pendencias--{}">{}</li>', itens),
        )

    @admin.display(description='Citação')
    def previa_da_citacao(self, obj):
        """As citações como o site as entrega, para o editor conferir o nome dos autores. Vale para o que está salvo."""
        if obj is None or not obj.pk:
            return 'Aparece depois de salvar o artigo.'
        if not obj.article_authors.exists():
            return 'Adicione ao menos um autor para ver a citação.'
        hoje = timezone.localdate()
        por_id = {c['id']: c for c in citacao.citacoes(obj)}
        corpo = []
        for id_ in ('abnt', 'apa'):
            marcas = {'b': 'strong', 'i': 'em'}
            partes = [
                (marcas.get(p['e'], 'span'), citacao.com_data_de_hoje(p['t'], hoje), marcas.get(p['e'], 'span'))
                for p in por_id[id_]['partes']
            ]
            corpo.append(format_html(
                '<p><b>{}</b><br>{}</p>', por_id[id_]['label'], format_html_join('', '<{}>{}</{}>', partes),
            ))
        bibtex = citacao.com_data_de_hoje(por_id['bibtex']['texto'], hoje)
        corpo.append(format_html('<p><b>BibTeX</b></p><pre class="previa-citacao">{}</pre>', bibtex))
        corpo.append(mark_safe(
            '<p class="texto-original">Reflete o que está salvo. Se um nome sair errado, ajuste a linha do autor '
            'ou o “Nome na citação” do membro.</p>'
        ))
        return format_html_join('', '{}', ((c,) for c in corpo))

    @admin.display(description='Autores')
    def autores(self, obj):
        return ', '.join(a.display_name for a in obj.article_authors.all())

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'topics':
            kwargs['widget'] = CampoDeTemas(temas_ja_usados())
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
        sem_autor = queryset.filter(published=False, article_authors__isnull=True)
        sem_autor_ids = list(sem_autor.values_list('pk', flat=True))
        n = queryset.filter(published=False).exclude(pk__in=sem_autor_ids).update(published=True)
        sem_data = queryset.filter(date__isnull=True).count()
        self.message_user(request, f'{n} artigo(s) publicado(s).', messages.SUCCESS)
        if sem_autor_ids:
            self.message_user(
                request,
                f'{len(sem_autor_ids)} artigo(s) não foram publicados por não terem autor. Adicione os autores '
                'em cada um.',
                messages.WARNING,
            )
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
    # A ordem em que as pessoas aparecem no case se muda arrastando a linha (o site mostra primeiro
    # os integrantes e depois os mentores, e respeita a ordem dentro de cada papel).
    model = ProgramCaseParticipant
    extra = 1
    fields = ('member', 'role', 'order')
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = True
    autocomplete_fields = ('member',)


@admin.register(ProgramCase)
class ProgramCaseAdmin(AdminDoSite):
    inlines = [ProgramCaseParticipantInline]
    linhas_dos_campos = {'theme': 3, 'panel': 3}
    fieldsets = (
        (None, {'fields': (
            'program', 'semester', 'title', 'area', 'theme', 'panel', 'award', 'publication_url', 'is_active',
        )}),
        secao_avancada('order'),
    )
    list_display = ('semester', 'title', 'area', 'program', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'program', 'semester')
    search_fields = ('title', 'area', 'theme', 'award')
    list_select_related = ('program',)


# ---------------------------------------------------------------------------
# Processo seletivo (página /processo)
# ---------------------------------------------------------------------------

class SelectionProcessStageInline(AbaOrdenavelTabular):
    model = SelectionProcessStage
    extra = 1
    fields = ('label', 'date', 'order')


class SelectionProcessStepInline(TextoCompactoMixin, AbaOrdenavelEmpilhada):
    model = SelectionProcessStep
    extra = 0
    fields = ('number', 'title', 'description', 'image', 'duration', 'tips', 'order')
    linhas_dos_campos = {'description': 3, 'tips': 4}


class SelectionProcessRequirementInline(AbaOrdenavelTabular):
    model = SelectionProcessRequirement
    extra = 1
    fields = ('text', 'icon', 'order')


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

    def has_duplicar_permission(self, request, object_id=None):
        # Usada pelo botão da página de edição (o Unfold a chama com o id do processo).
        return request.user.has_perm('website.add_selectionprocess')

    @admin.action(description='Duplicar selecionados (cópia inativa, para o próximo semestre)', permissions=['add'])
    def duplicar(self, request, queryset):
        copias = [processo.duplicate() for processo in queryset]
        self.message_user(
            request,
            f'{len(copias)} processo(s) duplicado(s). As cópias estão inativas e com as inscrições fechadas: '
            'ajuste as datas, preencha o link do formulário e ative quando for a hora.',
            messages.SUCCESS,
        )

    @acao_unfold(description='Duplicar este processo', icon='content_copy', permissions=['duplicar'])
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

class PartnerBenefitInline(TextoCompactoMixin, AbaOrdenavelTabular):
    model = PartnerBenefit
    extra = 0
    fields = ('title', 'description', 'order')
    linhas_dos_campos = {'description': 2}


class SiteConfigForm(forms.ModelForm):
    """Confere o formato das imagens de marca no momento do envio e lista os programas para escolha."""

    class Meta:
        model = SiteConfig
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        campo = self.fields.get('featured_program_slug')
        if campo is None:  # quem não vê a aba Páginas (a configuração do formulário esconde o campo)
            return
        opcoes = [('', '---------')] + [(p.slug, p.label) for p in Program.objects.order_by('order', 'label')]
        atual = self.instance.featured_program_slug
        if atual and atual not in dict(opcoes):
            # Um valor antigo que não corresponde mais a nenhum programa continua visível, para não sumir calado.
            opcoes.append((atual, f'{atual} (programa não encontrado)'))
        self.fields['featured_program_slug'] = forms.ChoiceField(
            choices=opcoes, required=False, label=campo.label, help_text=campo.help_text,
            initial=atual, widget=UnfoldAdminSelectWidget,
        )

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
                    'Use pelo menos 600 pixels de largura; o ideal é 1200 x 630.'
                )
            if not 1.6 <= proporcao <= 2.2:
                raise forms.ValidationError(
                    f'A proporção da imagem ({largura} x {altura} pixels) é muito diferente da usada pelo '
                    'WhatsApp e pelo LinkedIn, e ela seria cortada. Use 1200 x 630.'
                )
        return arquivo


class NavItemInline(AbaOrdenavelTabular):
    model = NavItem
    extra = 0
    fields = ('label', 'area', 'page', 'url', 'order', 'is_active')


@admin.register(SiteConfig)
class SiteConfigAdmin(AdminDoSite):
    form = SiteConfigForm
    # Estrutura do site: só administradores (superusuários) veem e editam estas abas. As
    # demais ficam com quem tem permissão de alterar a configuração (o grupo Editores).
    SO_ADMINISTRADORES = ('Marca e compartilhamento', 'Política de Privacidade')
    # Campos que entram no HTML do site durante o build do frontend.
    CAMPOS_DA_MARCA = ('site_name', 'site_description', 'logo', 'favicon', 'og_image')
    inlines = [NavItemInline, PartnerBenefitInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'privacy_text':
            kwargs['widget'] = MarkdownPreviewWidget(modo='politica')
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    fieldsets = (
        ('Marca e compartilhamento', {
            'classes': ['tab'],
            'description': 'Nome, descrição e imagens do site. Só administradores veem esta aba. Mudanças aqui só '
                           'aparecem na prévia dos links (WhatsApp, LinkedIn) e no ícone da aba depois que o '
                           'frontend é publicado de novo no Render (Manual Deploy).',
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
            'description': 'A foto de "Quem somos". Os textos da Home ficam em Textos do site, na página Home. '
                           'As estatísticas ficam em Estatísticas, e os programas, os membros e os parceiros '
                           'vêm dos próprios cadastros.',
            'fields': ('home_about_photo', 'home_about_photo_alt'),
        }),
        ('Páginas', {
            'classes': ['tab'],
            'description': 'O texto que aparece abaixo do título de cada página fica em Textos do site.',
            'fields': ('featured_program_slug',),
        }),
        ('Política de Privacidade', {
            'classes': ['tab'],
            'fields': ('privacy_updated', 'privacy_text'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        conjuntos = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return conjuntos
        # Os campos das abas escondidas saem do formulário, então também não são gravados.
        return [conjunto for conjunto in conjuntos if conjunto[0] not in self.SO_ADMINISTRADORES]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if set(form.changed_data) & set(self.CAMPOS_DA_MARCA):
            self.message_user(
                request,
                'Para a mudança na marca aparecer na prévia dos links e no ícone da aba, publique o frontend '
                'de novo: no Render, serviço do frontend, Manual Deploy.',
                messages.WARNING,
            )

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

def nome_do_campo(chave):
    """Nome do campo do formulário para uma chave de texto ("home.sobre_eyebrow" vira "t__home__sobre_eyebrow")."""
    return 't__' + chave.replace('.', '__')


def _rodape_do_original(original, valor, id_do_campo):
    """Abaixo do campo: avisa que o texto foi editado e deixa voltar ao original com um clique."""
    if (valor or '') == original:
        return ''
    return format_html(
        '<div class="texto-original"><span class="texto-editado">editado</span> Original: <em>{}</em> '
        '<button type="button" class="restaurar-texto" data-original="{}" '
        'onclick="document.getElementById(\'{}\').value=this.dataset.original">Restaurar o original</button></div>',
        original or 'vazio', original, id_do_campo,
    )


class CampoDeTextoComOriginal(UnfoldAdminTextInputWidget):
    def __init__(self, original, attrs=None):
        super().__init__(attrs)
        self.original = original

    def render(self, name, value, attrs=None, renderer=None):
        campo = super().render(name, value, attrs, renderer)
        return format_html('{}{}', campo, _rodape_do_original(self.original, value, (attrs or {}).get('id') or f'id_{name}'))


class AreaDeTextoComOriginal(UnfoldAdminTextareaWidget):
    def __init__(self, original, attrs=None):
        super().__init__({'rows': 3, **(attrs or {})})
        self.original = original

    def render(self, name, value, attrs=None, renderer=None):
        campo = super().render(name, value, attrs, renderer)
        return format_html('{}{}', campo, _rodape_do_original(self.original, value, (attrs or {}).get('id') or f'id_{name}'))


def _normaliza(texto):
    """Minúsculas e sem acento, para a busca achar "missao" em "Missão"."""
    return ''.join(c for c in unicodedata.normalize('NFKD', texto.lower()) if not unicodedata.combining(c))


def _valores_dos_textos():
    """O que está no banco, por chave. Texto que ainda não chegou ao banco vale o original."""
    return {**PADRAO_DOS_TEXTOS, **dict(SiteText.objects.values_list('key', 'value'))}


def _chaves_que_batem(termo):
    """As chaves cujo rótulo, seção, página, valor atual ou original contêm o termo buscado."""
    procurado = _normaliza(termo.strip())
    valores = _valores_dos_textos()
    achadas = []
    for chave, (pagina, texto) in POR_CHAVE.items():
        campos = (texto.rotulo, texto.secao, pagina.titulo, texto.padrao, valores.get(chave, texto.padrao))
        if any(procurado in _normaliza(c) for c in campos):
            achadas.append(chave)
    return achadas


def _editados_por_pagina():
    """Quantos textos de cada página já foram editados (diferentes do original)."""
    valores = _valores_dos_textos()
    return {
        pagina.slug: sum(1 for texto in pagina.textos if valores.get(texto.chave, texto.padrao) != texto.padrao)
        for pagina in PAGINAS
    }


class FormDaPagina(forms.ModelForm):
    """Base do formulário de uma página: os campos (um por texto) são acrescentados em PaginaDoSiteAdmin.get_form."""
    _textos = {}

    class Meta:
        model = PaginaDoSite
        fields = []

    def clean(self):
        dados = super().clean()
        for nome, texto in self._textos.items():
            valor = dados.get(nome)
            if valor is None:
                continue
            faltando = sorted(set(re.findall(r'\{\w+\}', texto.padrao)) - set(re.findall(r'\{\w+\}', valor)))
            if faltando:
                self.add_error(nome, 'Mantenha no texto: ' + ', '.join(faltando) + '. O site preenche esses trechos.')
        return dados


class SituacaoDosTextosFilter(admin.SimpleListFilter):
    title = 'situação'
    parameter_name = 'situacao'

    def lookups(self, request, model_admin):
        return [('editados', 'Com textos editados'), ('originais', 'Só com os textos originais')]

    def queryset(self, request, queryset):
        if self.value() not in ('editados', 'originais'):
            return queryset
        editados = _editados_por_pagina()
        com_edicao = [slug for slug, n in editados.items() if n]
        if self.value() == 'editados':
            return queryset.filter(slug__in=com_edicao)
        return queryset.exclude(slug__in=com_edicao)


@admin.register(PaginaDoSite)
class PaginaDoSiteAdmin(AdminDoSite):
    """
    "Textos do site": uma linha por página. Cada página abre num formulário com as suas seções e os seus textos, vindos
    do registro de conteúdo (website/conteudo/). As páginas e os textos nascem sozinhos; aqui só se edita o valor.
    """
    list_display = ('titulo', 'quantos', 'editados')
    list_display_links = ('titulo',)
    list_filter = (SituacaoDosTextosFilter,)
    search_fields = ('title',)  # só para mostrar a caixa de busca; a busca de verdade está em get_search_results
    ordering = ('order',)
    actions = ['restaurar_originais']

    # --- lista de páginas

    @admin.display(description='Página', ordering='order')
    def titulo(self, obj):
        return obj.title

    @admin.display(description='Textos')
    def quantos(self, obj):
        pagina = POR_SLUG.get(obj.slug)
        return len(pagina.textos) if pagina else 0

    @admin.display(description='Já editados')
    def editados(self, obj):
        return _editados_por_pagina().get(obj.slug, 0) or '-'

    def get_list_display(self, request):
        colunas = list(super().get_list_display(request))
        termo = request.GET.get('q', '').strip()
        if termo:
            achadas = set(_chaves_que_batem(termo))

            def encontrados(obj):
                pagina = POR_SLUG.get(obj.slug)
                if not pagina:
                    return ''
                nomes = [f'{t.secao}: {t.rotulo}' for t in pagina.textos if t.chave in achadas]
                return '; '.join(nomes[:3]) + (f' (e mais {len(nomes) - 3})' if len(nomes) > 3 else '')

            encontrados.short_description = 'Textos encontrados'
            colunas.append(encontrados)
        return colunas

    def get_search_results(self, request, queryset, search_term):
        if not search_term.strip():
            return queryset, False
        slugs = {POR_CHAVE[chave][0].slug for chave in _chaves_que_batem(search_term)}
        slugs |= {p.slug for p in PAGINAS if _normaliza(search_term.strip()) in _normaliza(p.titulo)}
        return queryset.filter(slug__in=slugs), False

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, {'title': 'Textos do site', **(extra_context or {})})

    # As páginas vêm do registro: aqui só se edita o texto.
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def view_on_site(self, obj):
        return url_do_site(obj.path)

    # --- formulário de uma página

    def get_form(self, request, obj=None, change=False, **kwargs):
        if obj is not None and obj.slug in POR_SLUG:
            pagina = POR_SLUG[obj.slug]
            valores = _valores_dos_textos()
            campos = {}
            for texto in pagina.textos:
                widget = (AreaDeTextoComOriginal if texto.e_longo else CampoDeTextoComOriginal)(texto.padrao)
                trechos = sorted(set(re.findall(r'\{\w+\}', texto.padrao)))
                campos[nome_do_campo(texto.chave)] = forms.CharField(
                    label=texto.rotulo, max_length=2000 if texto.e_longo else 300, widget=widget,
                    required=not texto.opcional,
                    initial=valores.get(texto.chave, texto.padrao),
                    help_text=f'O site preenche {", ".join(trechos)}: mantenha no texto.' if trechos else '',
                )
            kwargs['form'] = type('FormDaPaginaDoSite', (FormDaPagina,), {
                **campos, '_textos': {nome_do_campo(t.chave): t for t in pagina.textos},
            })
        return super().get_form(request, obj, change=change, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj is None or obj.slug not in POR_SLUG:
            return [(None, {'fields': []})]
        secoes = {}
        raros = []
        for texto in POR_SLUG[obj.slug].textos:
            if texto.raro:
                raros.append(nome_do_campo(texto.chave))
            else:
                secoes.setdefault(texto.secao, []).append(nome_do_campo(texto.chave))
        conjuntos = [(secao, {'fields': campos}) for secao, campos in secoes.items()]
        if raros:
            conjuntos.append((f'Mensagens e estados raros ({len(raros)})', {
                'classes': ['collapse'],
                'description': 'Erros, páginas que não existem e formas no plural: quase nunca precisam de ajuste.',
                'fields': raros,
            }))
        return conjuntos

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        for nome in form.changed_data:
            texto = form._textos.get(nome)
            if texto is not None:
                SiteText.objects.filter(key=texto.chave).update(value=form.cleaned_data[nome])

    @admin.action(description='Restaurar os textos originais das páginas selecionadas', permissions=['change'])
    def restaurar_originais(self, request, queryset):
        n = 0
        for pagina in queryset:
            for texto in POR_SLUG.get(pagina.slug, Pagina('', '', '', ())).textos:
                n += SiteText.objects.filter(key=texto.chave).exclude(value=texto.padrao).update(value=texto.padrao)
        self.message_user(request, f'{n} texto(s) restaurado(s) ao original.', messages.SUCCESS)


@admin.register(SecaoDaHome)
class SecaoDaHomeAdmin(AdminDoSite):
    """
    "Seções da Home": mostrar, esconder e reordenar (arrastando) as seções depois da Apresentação. As linhas nascem do
    registro de conteúdo e não se criam nem se excluem aqui. O aviso tem também o destino do botão.
    """
    list_display = ('title', 'visible')
    list_display_links = ('title',)
    list_editable = ('visible',)
    ordering_field = 'order'
    hide_ordering_field = True
    ordering = ('order',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return super().changelist_view(request, {'title': 'Seções da Home', **(extra_context or {})})

    def get_fieldsets(self, request, obj=None):
        if obj is not None and obj.key == 'aviso':
            return [
                (None, {'fields': ('visible',)}),
                ('Botão do aviso', {
                    'description': 'O título, o texto e o texto do botão ficam em Textos do site, na página Home, '
                                   'seção Aviso. Sem texto, o aviso não aparece, mesmo ligado.',
                    'fields': ('button_page', 'button_url'),
                }),
            ]
        return [(None, {'fields': ('visible',)})]

    def view_on_site(self, obj):
        base = settings.FRONTEND_URL.rstrip('/')
        return f'{base}/' if base else None

