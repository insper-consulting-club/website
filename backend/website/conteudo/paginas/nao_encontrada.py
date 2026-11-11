from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="nao_encontrada", titulo="Página não encontrada", caminho="/uma-pagina-que-nao-existe",
    textos=(
        Texto("nao_encontrada.eyebrow", "Página", "Palavra pequena acima do título", "Erro 404", raro=True),
        Texto("nao_encontrada.titulo", "Página", "Título", "Página não encontrada", raro=True),
        Texto("nao_encontrada.texto", "Página", "Texto de apoio", "O endereço acessado não existe ou foi alterado.", raro=True),
        Texto("nao_encontrada.botao", "Página", "Botão para voltar ao início", "Voltar para o início", raro=True),
    ),
)
