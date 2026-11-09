from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="projetos", titulo="Projetos (lista)", caminho="/projetos",
    textos=(
        Texto("projetos.eyebrow", "Cabeçalho da página", "Palavra pequena acima do título (também é o nome da aba do navegador)", "Projetos"),
        Texto("projetos.titulo", "Cabeçalho da página", "Título, antes da palavra em destaque", "Programas e"),
        Texto("projetos.titulo_destaque", "Cabeçalho da página", "Palavra em destaque (em vermelho) no fim do título", "cases"),
        Texto("projetos.outros_eyebrow", "Outros projetos", "Palavra pequena acima do título da seção", "Além dos programas"),
        Texto("projetos.outros_titulo", "Outros projetos", "Título da seção (projetos que não são de nenhum programa)", "Outros projetos"),
        Texto("projetos.cases_eyebrow", "Cases em destaque", "Palavra pequena acima do título da seção", "Cases resolvidos"),
        Texto("projetos.cases_titulo_um", "Cases em destaque", "Título quando o programa tem 1 case", "{programa}: {n} case", raro=True),
        Texto("projetos.cases_titulo_varios", "Cases em destaque", "Título quando o programa tem mais de 1 case", "{programa}: {n} cases"),
        Texto("projetos.cases_botao", "Cases em destaque", "Botão da seção", "Ver os cases"),
    ),
)
