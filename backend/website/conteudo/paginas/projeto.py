from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="projeto", titulo="Um projeto", caminho="/projetos",
    textos=(
        Texto("projeto.voltar", "Topo da página", "Link para voltar quando o projeto não é de nenhum programa", "Todos os projetos", raro=True),
        Texto("projeto.nao_encontrado_titulo", "Quando o projeto não existe", "Título", "Projeto não encontrado", raro=True),
        Texto("projeto.nao_encontrado_texto", "Quando o projeto não existe", "Texto", "Não foi possível carregar esse projeto.", raro=True),
        Texto("projeto.rotulo_data", "Dados do projeto", "Rótulo da data, quando o projeto dura um dia só", "Data", raro=True),
        Texto("projeto.rotulo_periodo", "Dados do projeto", "Rótulo do período do projeto", "Período", raro=True),
        Texto("projeto.periodo_desde", "Dados do projeto", "Período de um projeto em andamento", "Desde {inicio}", raro=True),
        Texto("projeto.periodo_intervalo", "Dados do projeto", "Período de um projeto concluído", "{inicio} a {fim}", raro=True),
        Texto("projeto.rotulo_situacao", "Dados do projeto", "Rótulo da situação do projeto", "Situação", raro=True),
        Texto("projeto.concluido", "Dados do projeto", "Situação: projeto concluído", "Concluído", raro=True),
        Texto("projeto.em_andamento", "Dados do projeto", "Situação: projeto em andamento", "Em andamento", raro=True),
        Texto("projeto.rotulo_parceiro", "Dados do projeto", "Rótulo quando há 1 parceiro", "Parceiro", raro=True),
        Texto("projeto.rotulo_parceiros", "Dados do projeto", "Rótulo quando há mais de 1 parceiro", "Parceiros", raro=True),
        Texto("projeto.linha_do_tempo", "Seções da página", "Título do cronograma", "Linha do tempo", raro=True),
        Texto("projeto.imagens", "Seções da página", "Título da galeria de imagens", "Imagens", raro=True),
        Texto("projeto.equipe", "Seções da página", "Título da equipe do projeto", "Equipe", raro=True),
        Texto("projeto_card.concluido_em", "Cartão do projeto (aparece em listas)", "Rodapé de um projeto concluído", "Concluído em {data}", raro=True),
        Texto("projeto_card.link", "Cartão do projeto (aparece em listas)", "Link no fim do cartão", "Ver projeto", raro=True),
    ),
)
