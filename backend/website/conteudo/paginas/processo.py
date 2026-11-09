from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="processo", titulo="Processo seletivo", caminho="/processo",
    textos=(
        Texto("processo.eyebrow", "Cabeçalho da página", "Palavra pequena acima do título", "Seja membro"),
        Texto("processo.titulo", "Cabeçalho da página", "Título quando não há processo ativo", "Processo Seletivo"),
        Texto("processo.abertas", "Inscrições", "Chamada quando as inscrições estão abertas", "Inscrições abertas!"),
        Texto("processo.botao_inscricao", "Inscrições", "Botão de inscrição", "Inscreva-se"),
        Texto("processo.botao_instagram", "Inscrições", "Botão quando as inscrições estão encerradas", "Seguir no Instagram"),
        Texto("processo.sem_processo_titulo", "Quando não há processo ativo", "Título", "Nenhum processo seletivo ativo no momento."),
        Texto("processo.sem_processo_texto", "Quando não há processo ativo", "Texto", "Assim que abrirmos novas vagas, as inscrições aparecem aqui."),
        Texto("processo.calendario", "Seções da página", "Título do calendário", "Calendário"),
        Texto("processo.etapas", "Seções da página", "Título das etapas", "Etapas do processo"),
        Texto("processo.requisitos", "Seções da página", "Título dos requisitos", "Requisitos"),
        Texto("processo.materiais", "Seções da página", "Título dos materiais de preparação", "Materiais de preparação"),
    ),
)
