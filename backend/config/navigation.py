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
        ("website", "sitetext", "Textos do site", "text_fields"),
        ("website", "statistic", "Estatísticas", "bar_chart"),
    ]),
    ("Acesso", [
        ("auth", "user", "Usuários", "person"),
        ("auth", "group", "Grupos", "admin_panel_settings"),
    ]),
]


def pode_abrir(usuario, app, modelo):
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
