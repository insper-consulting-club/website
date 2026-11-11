"""Menu lateral do /admin (django-unfold), agrupado por assunto.

O Unfold chama navegacao(request) a cada página. Um item só aparece para quem
tem permissão de ver ou alterar o modelo, então um login limitado enxerga
apenas o que pode usar.
"""
from django.urls import reverse

# (título do grupo, [(app, modelo, texto do menu, ícone)]). Ícones: Material Symbols.
# A ordem segue o uso: o que se edita toda semana vem primeiro, e a configuração vem no fim.
GRUPOS = [
    ("Artigos", [
        ("website", "article", "Artigos", "article"),
    ]),
    ("Equipe", [
        ("website", "member", "Membros", "groups"),
        ("website", "position", "Cargos", "badge"),
        ("website", "directorate", "Diretorias", "account_tree"),
    ]),
    ("Parceiros", [
        ("website", "partner", "Parceiros", "handshake"),
        ("website", "partnercategory", "Categorias dos parceiros", "category"),
    ]),
    ("Programas e projetos", [
        ("website", "project", "Projetos", "folder_open"),
        ("website", "program", "Programas", "school"),
        ("website", "programcase", "Cases dos programas", "emoji_events"),
    ]),
    ("Processo seletivo", [
        ("website", "selectionprocess", "Processos seletivos", "how_to_reg"),
        ("website", "preparationmaterial", "Materiais de preparação", "menu_book"),
    ]),
    ("Site", [
        ("website", "siteconfig", "Configuração do site", "tune"),
        ("website", "paginadosite", "Textos do site", "text_fields"),
        ("website", "secaodahome", "Seções da Home", "view_agenda"),
        ("website", "statistic", "Estatísticas", "bar_chart"),
    ]),
    ("Acesso", [
        ("auth", "user", "Usuários", "person"),
        ("auth", "group", "Grupos", "admin_panel_settings"),
        ("admin", "logentry", "Atividade recente", "history"),
    ]),
]


# Cadastros que o editor só consulta (ele cria um cargo pelo formulário do membro, mas não o altera): ficam fora do
# menu de quem não pode alterar, para não parecerem uma lista de trabalho.
SO_PARA_QUEM_ALTERA = {("website", "position")}


def pode_abrir(usuario, app, modelo):
    if (app, modelo) in SO_PARA_QUEM_ALTERA:
        return usuario.has_perm(f"{app}.change_{modelo}")
    return usuario.has_perm(f"{app}.view_{modelo}") or usuario.has_perm(f"{app}.change_{modelo}")


def navegacao(request):
    grupos = []
    for titulo, itens in GRUPOS:
        visiveis = [
            {
                "title": texto,
                "icon": icone,
                "link": reverse(f"admin:{app}_{modelo}_changelist"),
            }
            for app, modelo, texto, icone in itens
            if pode_abrir(request.user, app, modelo)
        ]
        if visiveis:
            grupos.append({"title": titulo, "separator": True, "items": visiveis})
    return grupos


# Página inicial do /admin: poucos atalhos para o que se faz com frequência, em vez da lista de todos os cadastros.
# (título, explicação, ícone, [(texto do link, app, modelo, "lista" ou "novo")]). O primeiro link é o principal.
ATALHOS = [
    ("Artigos", "Escreva, revise e publique os artigos do site.", "article", [
        ("Escrever um artigo", "website", "article", "novo"),
        ("Ver artigos", "website", "article", "lista"),
    ]),
    ("Equipe", "Membros do clube e as diretorias.", "groups", [
        ("Membros", "website", "member", "lista"),
        ("Novo membro", "website", "member", "novo"),
        ("Diretorias", "website", "directorate", "lista"),
    ]),
    ("Parceiros", "Empresas parceiras e as categorias delas.", "handshake", [
        ("Parceiros", "website", "partner", "lista"),
        ("Novo parceiro", "website", "partner", "novo"),
    ]),
    ("Programas e projetos", "Programas, projetos e cases.", "folder_open", [
        ("Projetos", "website", "project", "lista"),
        ("Novo projeto", "website", "project", "novo"),
        ("Programas", "website", "program", "lista"),
    ]),
    ("Processo seletivo", "Abra e feche as inscrições e atualize as etapas.", "how_to_reg", [
        ("Processos seletivos", "website", "selectionprocess", "lista"),
    ]),
    ("Textos do site", "Os títulos e as frases de cada página, e as seções da Home.", "text_fields", [
        ("Editar textos", "website", "paginadosite", "lista"),
        ("Seções da Home", "website", "secaodahome", "lista"),
    ]),
    ("Acesso", "Logins e o histórico das alterações (só administradores).", "admin_panel_settings", [
        ("Usuários", "auth", "user", "lista"),
        ("Atividade recente", "admin", "logentry", "lista"),
    ]),
]


def _pode_usar_atalho(usuario, app, modelo, acao):
    if acao == "novo":
        return usuario.has_perm(f"{app}.add_{modelo}")
    return pode_abrir(usuario, app, modelo)


def atalhos_do_usuario(usuario):
    cartoes = []
    for titulo, explicacao, icone, links in ATALHOS:
        visiveis = [
            {
                "texto": texto,
                "url": reverse(f"admin:{app}_{modelo}_{'add' if acao == 'novo' else 'changelist'}"),
            }
            for texto, app, modelo, acao in links
            if _pode_usar_atalho(usuario, app, modelo, acao)
        ]
        if visiveis:
            cartoes.append({"titulo": titulo, "explicacao": explicacao, "icone": icone, "links": visiveis})
    return cartoes


def painel(request, context):
    """DASHBOARD_CALLBACK do Unfold: acrescenta os atalhos e o nível de acesso à página inicial."""
    usuario = request.user
    context["atalhos"] = atalhos_do_usuario(usuario)
    context["nivel_de_acesso"] = "Administrador" if usuario.is_superuser else "Editor"
    return context
