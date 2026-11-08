"""Painel da página inicial do /admin: o que precisa de atenção, números e atalhos.

O Unfold chama painel(request, context) ao abrir a página inicial. Cada item só
aparece para quem tem permissão de ver (ou criar) o que ele mostra.
"""
from django.conf import settings
from django.urls import reverse

from website.models import (
    Article, Member, NavItem, Partner, Program, Project, SelectionProcess, SiteConfig,
)


def _pode(usuario, acao, modelo):
    return usuario.has_perm(f"website.{acao}_{modelo}")


def _lista(modelo, filtro=""):
    return reverse(f"admin:website_{modelo}_changelist") + filtro


def _plural(n, singular, plural):
    return f"{n} {singular if n == 1 else plural}"


def _alertas(usuario):
    alertas = []

    if _pode(usuario, "view", "article"):
        n = Article.objects.filter(published=False).count()
        if n:
            alertas.append({
                "icone": "edit_note",
                "texto": (
                    "1 artigo em rascunho: não aparece no site até ser publicado."
                    if n == 1 else f"{n} artigos em rascunho: não aparecem no site até serem publicados."
                ),
                "link": _lista("article", "?published__exact=0"),
            })

    if _pode(usuario, "view", "selectionprocess"):
        ativo = SelectionProcess.objects.filter(is_active=True).order_by("-id").first()
        if ativo is None:
            alertas.append({
                "icone": "warning",
                "aviso": True,
                "texto": "Nenhum processo seletivo ativo: a página Processo Seletivo mostra que não há processo no momento.",
                "link": _lista("selectionprocess"),
            })
        else:
            situacao = "abertas" if ativo.registrations_open else "encerradas"
            alertas.append({
                "icone": "how_to_reg",
                "texto": f"Processo seletivo ativo: “{ativo.title}”. Inscrições {situacao}.",
                "link": reverse("admin:website_selectionprocess_change", args=[ativo.pk]),
            })

    config = SiteConfig.objects.filter(pk=1).first()
    if config and config.featured_program_slug and _pode(usuario, "view", "siteconfig"):
        if not Program.objects.filter(slug=config.featured_program_slug, is_active=True).exists():
            alertas.append({
                "icone": "warning",
                "aviso": True,
                "texto": f"O programa em destaque da página Projetos (“{config.featured_program_slug}”) não existe ou está oculto: "
                         "a seção de cases some. Ajuste em Configuração do site, aba Páginas.",
                "link": reverse("admin:website_siteconfig_change", args=[1]),
            })

    if _pode(usuario, "view", "siteconfig") and not NavItem.objects.filter(is_active=True, area__in=["menu", "topo"]).exists():
        alertas.append({
            "icone": "warning",
            "aviso": True,
            "texto": "Nenhum item ativo no menu do topo: o site está sem navegação. Veja Configuração do site, aba Itens de navegação.",
            "link": reverse("admin:website_siteconfig_change", args=[1]),
        })

    if _pode(usuario, "view", "project"):
        n = Project.objects.filter(is_active=False).count()
        if n:
            alertas.append({
                "icone": "inventory_2",
                "texto": (
                    "1 projeto arquivado: fora do site, mas guardado."
                    if n == 1 else f"{n} projetos arquivados: fora do site, mas guardados."
                ),
                "link": _lista("project", "?is_active__exact=0"),
            })
    if _pode(usuario, "view", "partner"):
        n = Partner.objects.filter(is_active=False).count()
        if n:
            alertas.append({
                "icone": "visibility_off",
                "texto": f"{_plural(n, 'parceiro oculto', 'parceiros ocultos')} no site.",
                "link": _lista("partner", "?is_active__exact=0"),
            })
    if _pode(usuario, "view", "program"):
        n = Program.objects.filter(is_active=False).count()
        if n:
            alertas.append({
                "icone": "visibility_off",
                "texto": f"{_plural(n, 'programa oculto', 'programas ocultos')} no site.",
                "link": _lista("program", "?is_active__exact=0"),
            })

    # Aviso técnico, só para quem administra: em produção, mudar a marca do site
    # exige reconstruir o frontend, e sem o deploy hook isso fica manual.
    if usuario.is_superuser and not settings.DEBUG and not settings.RENDER_FRONTEND_DEPLOY_HOOK:
        alertas.append({
            "icone": "warning",
            "aviso": True,
            "texto": "O deploy automático do frontend não está configurado (variável RENDER_FRONTEND_DEPLOY_HOOK): "
                     "mudanças em nome, descrição, logo e imagens de compartilhamento exigem um deploy manual no Render.",
            "link": "",
        })
    return alertas


def _numeros(usuario):
    numeros = []
    consultas = [
        ("member", "Membros atuais", lambda: Member.objects.filter(exit_date__isnull=True).count(), ""),
        ("partner", "Parceiros no site", lambda: Partner.objects.filter(is_active=True).count(), "?is_active__exact=1"),
        ("project", "Projetos no site", lambda: Project.objects.filter(is_active=True).count(), "?is_active__exact=1"),
        ("program", "Programas no site", lambda: Program.objects.filter(is_active=True).count(), "?is_active__exact=1"),
        ("article", "Artigos publicados", lambda: Article.objects.filter(published=True).count(), "?published__exact=1"),
    ]
    for modelo, rotulo, contar, filtro in consultas:
        if _pode(usuario, "view", modelo):
            numeros.append({"rotulo": rotulo, "valor": contar(), "link": _lista(modelo, filtro)})
    return numeros


def _atalhos(usuario):
    atalhos = []
    novos = [("article", "Novo artigo", "post_add"), ("project", "Novo projeto", "create_new_folder"),
             ("member", "Novo membro", "person_add"), ("partner", "Novo parceiro", "handshake")]
    for modelo, texto, icone in novos:
        if _pode(usuario, "add", modelo):
            atalhos.append({"texto": texto, "icone": icone, "link": reverse(f"admin:website_{modelo}_add")})
    if _pode(usuario, "change", "siteconfig"):
        atalhos.append({"texto": "Configuração do site", "icone": "tune", "link": reverse("admin:website_siteconfig_change", args=[1])})
    if _pode(usuario, "change", "sitetext"):
        atalhos.append({"texto": "Textos do site", "icone": "text_fields", "link": _lista("sitetext")})
    if settings.FRONTEND_URL:
        atalhos.append({"texto": "Ver o site", "icone": "open_in_new", "link": settings.FRONTEND_URL, "externo": True})
    return atalhos


def painel(request, context):
    usuario = request.user
    context["painel"] = {
        "alertas": _alertas(usuario),
        "numeros": _numeros(usuario),
        "atalhos": _atalhos(usuario),
    }
    return context
