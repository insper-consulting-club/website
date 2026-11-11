from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="parceiro", titulo="Perfil de um parceiro", caminho="/parceiros",
    textos=(
        Texto("parceiro.voltar", "Perfil", "Link para voltar à lista de parceiros", "Voltar para parceiros", raro=True),
        Texto("parceiro.nao_encontrado_titulo", "Quando o parceiro não existe", "Título", "Parceiro não encontrado", raro=True),
        Texto("parceiro.nao_encontrado_texto", "Quando o parceiro não existe", "Texto", "Não foi possível carregar esse parceiro.", raro=True),
        Texto("parceiro.visitar_site", "Perfil", "Botão que abre o site do parceiro", "Visitar site", raro=True),
        Texto("parceiro.casos", "Casos de sucesso", "Título da seção de projetos concluídos com o parceiro", "Casos de sucesso", raro=True),
        Texto("parceiro.caso_link", "Casos de sucesso", "Link de cada projeto", "Ver projeto", raro=True),
        Texto("parceiro.outros", "Outros parceiros", "Título da lista de outros parceiros da mesma categoria", "Outros parceiros em {categoria}", raro=True),
        Texto("parceiro.todos", "Outros parceiros", "Link para a lista completa de parceiros", "Todos os parceiros", raro=True),
    ),
)
