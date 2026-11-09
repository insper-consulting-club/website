"""
Grupo "Editores": o acesso padrão de quem cuida do conteúdo do site, sem ser
superusuário. Não inclui Usuários nem Grupos, e não permite apagar registros
que têm "esconder" (membros, parceiros, projetos, programas, cases, artigos,
processos seletivos), para que ninguém perca histórico por engano.

O grupo é criado uma vez, depois do primeiro `migrate`. Se alguém ajustar as
permissões dele no admin (Grupos > Editores), os ajustes ficam: o `migrate`
nunca os desfaz. Para voltar ao padrão, apague o grupo no admin: o próximo `migrate`
(todo deploy roda um) o recria com as permissões originais.
"""

NOME = "Editores"

COMPLETO = ("add", "change", "delete", "view")
EDICAO = ("add", "change", "view")
ALTERACAO = ("change", "view")
LEITURA = ("view",)

# modelo (nome em minúsculas) -> ações permitidas
PERMISSOES = {
    # Cadastros principais: criam, editam e escondem, mas não apagam.
    "member": EDICAO,
    "directorate": EDICAO,
    "partner": EDICAO,
    "partnercategory": EDICAO,
    "program": EDICAO,
    "programcase": EDICAO,
    "project": EDICAO,
    "article": EDICAO,
    "selectionprocess": EDICAO,
    # Cargos: o editor cria um cargo novo (sempre como membro comum, a prioridade fica com os
    # administradores) mas não altera os existentes, porque a prioridade decide a liderança da Home.
    "position": ("add", "view"),
    # Registro único e textos fixos: só alteram, não criam nem apagam. As abas Marca e
    # compartilhamento e Política de Privacidade da configuração, o menu e os benefícios
    # para parceiros são só dos administradores (ver SiteConfigAdmin).
    "siteconfig": ALTERACAO,
    "paginadosite": ALTERACAO,
    # Itens que vivem dentro de outro registro (tabelas do formulário):
    # precisam de todas as ações, senão o botão de remover linha não funciona.
    "directoratemembership": COMPLETO,
    "programcomponent": COMPLETO,
    "programcontentblock": COMPLETO,
    "programcaseparticipant": COMPLETO,
    "projectimage": COMPLETO,
    "projecttimelineevent": COMPLETO,
    "projectcontentblock": COMPLETO,
    "articleimage": COMPLETO,
    "statistic": COMPLETO,
    "selectionprocessstage": COMPLETO,
    "selectionprocessstep": COMPLETO,
    "selectionprocessrequirement": COMPLETO,
    "preparationmaterial": COMPLETO,
    "preparationmaterialitem": COMPLETO,
}


def codenames():
    return {f"{acao}_{modelo}" for modelo, acoes in PERMISSOES.items() for acao in acoes}


def _acrescenta_permissoes_novas(grupo, Permission):
    """
    Um grupo que já existe não é refeito, mas ganha as permissões de telas que nasceram depois dele. Hoje, a de
    "Textos do site" (PaginaDoSite), que substituiu a lista antiga de textos: quem podia alterar textos continua podendo.
    """
    novas = Permission.objects.filter(
        content_type__app_label="website", codename__in=("change_paginadosite", "view_paginadosite"),
    )
    if novas.exists() and not grupo.permissions.filter(codename__in=("change_paginadosite", "view_paginadosite")).exists() \
            and grupo.permissions.filter(codename="change_sitetext").exists():
        grupo.permissions.add(*novas)


def sincroniza_grupo_editores(apps, app_config=None):
    """
    Cria o grupo com as permissões padrão. Se ele já existe, não mexe (ajustes feitos no
    admin ficam). Devolve True quando criou o grupo e gravou as permissões.
    """
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    if app_config is not None:
        # As permissões de um app são criadas no fim do migrate; garante que já
        # existem antes de procurá-las.
        from django.contrib.auth.management import create_permissions
        create_permissions(app_config, apps=apps, verbosity=0)

    grupo, criado = Group.objects.get_or_create(name=NOME)
    if not criado:
        _acrescenta_permissoes_novas(grupo, Permission)
        return False
    permissoes = Permission.objects.filter(content_type__app_label="website", codename__in=codenames())
    grupo.permissions.set(permissoes)
    return True
