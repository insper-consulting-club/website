from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="artigos", titulo="Artigos", caminho="/artigos",
    textos=(
        Texto("artigos.titulo", "Lista de artigos", "Título da página (também é o nome da aba do navegador)", "Artigos"),
        Texto("artigos.abertura", "Lista de artigos", "Texto logo abaixo do título", "Artigos e publicações produzidos por membros do ICC"),
        Texto("artigos.vazio", "Lista de artigos", "Mensagem quando não há nenhum artigo", "Nenhum artigo cadastrado no momento.", raro=True),
        Texto("artigos.card_link", "Lista de artigos", "Link no fim de cada cartão de artigo", "Ler artigo"),
        Texto("artigo.voltar", "Leitura de um artigo", "Link para voltar à lista de artigos", "Voltar para artigos"),
        Texto("artigo.nao_encontrado_titulo", "Quando o artigo não existe", "Título", "Artigo não encontrado", raro=True),
        Texto("artigo.nao_encontrado_texto", "Quando o artigo não existe", "Texto", "Não foi possível carregar esse artigo.", raro=True),
        Texto("artigo.resumo", "Leitura de um artigo", "Título do resumo", "Resumo"),
        Texto("artigo.como_citar", "Leitura de um artigo", "Título da citação", "Como citar"),
        Texto("artigo.copiar", "Leitura de um artigo", "Botão de copiar a citação", "Copiar citação"),
        Texto("artigo.copiado", "Leitura de um artigo", "Aviso depois de copiar a citação", "Copiado!"),
        Texto("artigo.compartilhar", "Leitura de um artigo", "Botão de compartilhar no LinkedIn", "Compartilhar"),
        Texto("artigo.link_original", "Leitura de um artigo", "Botão para a publicação original", "Ver publicação original"),
    ),
)
