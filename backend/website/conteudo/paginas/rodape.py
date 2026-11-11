from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="rodape", titulo="Rodapé", caminho="/",
    textos=(
        Texto("rodape.frase", "Frase", "Frase abaixo do logo", "Mais do que um clube, somos um ambiente de formação para futuros consultores."),
        Texto("rodape.navegacao", "Colunas", "Título da coluna de navegação", "Navegação", raro=True),
        Texto("rodape.programas", "Colunas", "Título da coluna de programas", "Programas", raro=True),
        Texto("rodape.contato", "Colunas", "Título da coluna de contato", "Contato", raro=True),
        Texto("rodape.privacidade", "Links", "Link da Política de Privacidade", "Política de Privacidade", raro=True),
        Texto("rodape.admin", "Links", "Link da área administrativa", "Área administrativa", raro=True),
    ),
)
