from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="projeto", titulo="Um projeto", caminho="/projetos",
    textos=(
        Texto("projeto.voltar", "Topo da página", "Link para voltar quando o projeto não é de nenhum programa", "Todos os projetos"),
        Texto("projeto.nao_encontrado_titulo", "Quando o projeto não existe", "Título", "Projeto não encontrado", raro=True),
        Texto("projeto.nao_encontrado_texto", "Quando o projeto não existe", "Texto", "Não foi possível carregar esse projeto.", raro=True),
        Texto("projeto.rotulo_data", "Dados do projeto", "Rótulo da data, quando o projeto dura um dia só", "Data"),
        Texto("projeto.rotulo_periodo", "Dados do projeto", "Rótulo do período do projeto", "Período"),
        Texto("projeto.periodo_desde", "Dados do projeto", "Período de um projeto em andamento", "Desde {inicio}"),
        Texto("projeto.periodo_intervalo", "Dados do projeto", "Período de um projeto concluído", "{inicio} a {fim}"),
        Texto("projeto.rotulo_situacao", "Dados do projeto", "Rótulo da situação do projeto", "Situação"),
        Texto("projeto.concluido", "Dados do projeto", "Situação: projeto concluído", "Concluído"),
        Texto("projeto.em_andamento", "Dados do projeto", "Situação: projeto em andamento", "Em andamento"),
        Texto("projeto.rotulo_parceiro", "Dados do projeto", "Rótulo quando há 1 parceiro", "Parceiro", raro=True),
        Texto("projeto.rotulo_parceiros", "Dados do projeto", "Rótulo quando há mais de 1 parceiro", "Parceiros"),
        Texto("projeto.linha_do_tempo", "Seções da página", "Título do cronograma", "Linha do tempo"),
        Texto("projeto.imagens", "Seções da página", "Título da galeria de imagens", "Imagens"),
        Texto("projeto.equipe", "Seções da página", "Título da equipe do projeto", "Equipe"),
        Texto("projeto_card.concluido_em", "Cartão do projeto (aparece em listas)", "Rodapé de um projeto concluído", "Concluído em {data}"),
        Texto("projeto_card.link", "Cartão do projeto (aparece em listas)", "Link no fim do cartão", "Ver projeto"),
    ),
)
