from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="programa", titulo="Um programa", caminho="/projetos",
    textos=(
        Texto("programa.voltar", "Topo da página", "Link para voltar à lista de projetos", "Todos os projetos"),
        Texto("programa.botao_inscricao", "Topo da página", "Botão de inscrição do programa", "Formulário de inscrição"),
        Texto("programa.como_funciona", "Seções da página", "Título da seção dos componentes do programa", "Como funciona"),
        Texto("programa.beneficios", "Seções da página", "Título da seção de tópicos do programa", "Benefícios"),
        Texto("programa.projetos_titulo", "Seções da página", "Título da seção de projetos do programa", "Projetos"),
        Texto("programa.cases_titulo", "Seções da página", "Título da seção de cases do programa", "Cases resolvidos"),
        Texto("programa.case_banca", "Detalhes de um case", "Rótulo da banca avaliadora", "Banca avaliadora"),
        Texto("programa.case_grupo", "Detalhes de um case", "Rótulo do grupo vencedor", "Grupo vencedor"),
        Texto("programa.case_mentor", "Detalhes de um case", "Rótulo do mentor", "Mentor(a)"),
        Texto("programa.case_premiacao", "Detalhes de um case", "Rótulo da premiação", "Premiação"),
        Texto("programa.case_link", "Detalhes de um case", "Link para a publicação do case", "Ver post do case"),
        Texto("programa.outros_eyebrow", "Outros programas", "Palavra pequena acima do título da seção", "Projetos"),
        Texto("programa.outros_titulo", "Outros programas", "Título da seção", "Outros programas"),
        Texto("programa.outros_link", "Outros programas", "Link de cada programa", "Saiba mais"),
    ),
)
