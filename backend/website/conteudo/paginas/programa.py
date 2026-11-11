from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="programa", titulo="Um programa", caminho="/projetos",
    textos=(
        Texto("programa.voltar", "Topo da página", "Link para voltar à lista de projetos", "Todos os projetos", raro=True),
        Texto("programa.botao_inscricao", "Topo da página", "Botão de inscrição do programa", "Formulário de inscrição", raro=True),
        Texto("programa.como_funciona", "Seções da página", "Título da seção dos componentes do programa", "Como funciona", raro=True),
        Texto("programa.beneficios", "Seções da página", "Título da seção de tópicos do programa", "Benefícios", raro=True),
        Texto("programa.projetos_titulo", "Seções da página", "Título da seção de projetos do programa", "Projetos", raro=True),
        Texto("programa.cases_titulo", "Seções da página", "Título da seção de cases do programa", "Cases resolvidos", raro=True),
        Texto("programa.case_banca", "Detalhes de um case", "Rótulo da banca avaliadora", "Banca avaliadora", raro=True),
        Texto("programa.case_grupo", "Detalhes de um case", "Rótulo do grupo vencedor", "Grupo vencedor", raro=True),
        Texto("programa.case_mentor", "Detalhes de um case", "Rótulo do mentor", "Mentor(a)", raro=True),
        Texto("programa.case_premiacao", "Detalhes de um case", "Rótulo da premiação", "Premiação", raro=True),
        Texto("programa.case_link", "Detalhes de um case", "Link para a publicação do case", "Ver post do case", raro=True),
        Texto("programa.outros_eyebrow", "Outros programas", "Palavra pequena acima do título da seção", "Projetos"),
        Texto("programa.outros_titulo", "Outros programas", "Título da seção", "Outros programas"),
        Texto("programa.outros_link", "Outros programas", "Link de cada programa", "Saiba mais", raro=True),
    ),
)
