from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="artigos", titulo="Artigos", caminho="/artigos",
    textos=(
        Texto("artigos.titulo", "Lista de artigos", "Título da página (também é o nome da aba do navegador)", "Artigos"),
        Texto("artigos.abertura", "Lista de artigos", "Texto logo abaixo do título", "Artigos e publicações produzidos por membros do ICC"),
        Texto("artigos.vazio", "Lista de artigos", "Mensagem quando não há nenhum artigo", "Nenhum artigo cadastrado no momento.", raro=True),
        Texto("artigos.card_link", "Lista de artigos", "Link no fim de cada cartão de artigo", "Ler artigo"),
        Texto("artigos.filtro_autor", "Filtro por autor", "Nome do seletor de autor", "Autor"),
        Texto("artigos.todos_os_autores", "Filtro por autor", "Opção que mostra os artigos de todos os autores", "Todos os autores"),
        Texto("artigos.autor_titulo", "Filtro por autor", "Título quando a lista está filtrada por um autor", "Artigos de {autor}"),
        Texto("artigos.ver_perfil", "Filtro por autor", "Link para o perfil do autor na página Equipe", "Ver perfil"),
        Texto("artigos.ver_todos", "Filtro por autor", "Link para voltar a todos os artigos", "Ver todos os artigos"),
        Texto("artigos.nenhum_do_autor", "Filtro por autor", "Mensagem quando o autor filtrado não tem nenhum artigo", "Nenhum artigo publicado por esse autor.", raro=True),
        Texto("artigo.voltar", "Leitura de um artigo", "Link para voltar à lista de artigos", "Voltar para artigos"),
        Texto("artigo.nao_encontrado_titulo", "Quando o artigo não existe", "Título", "Artigo não encontrado", raro=True),
        Texto("artigo.nao_encontrado_texto", "Quando o artigo não existe", "Texto", "Não foi possível carregar esse artigo.", raro=True),
        Texto("artigo.resumo", "Leitura de um artigo", "Título do resumo", "Resumo"),
        Texto("artigo.palavras_chave", "Leitura de um artigo", "Título dos temas do artigo, dentro do resumo", "Palavras-chave"),
        Texto("artigo.compartilhar", "Leitura de um artigo", "Botão de compartilhar no LinkedIn", "Compartilhar"),
        Texto("artigo.citar", "Leitura de um artigo", "Botão que abre as formas de citar o artigo (ABNT, APA, BibTeX...)", "Citar"),
        Texto("artigo.citar_titulo", "Leitura de um artigo", "Título da janela de citação", "Citar este artigo"),
        Texto("artigo.copiar", "Leitura de um artigo", "Botão de copiar a citação aberta", "Copiar citação"),
        Texto("artigo.copiado", "Leitura de um artigo", "Aviso depois de copiar a citação", "Copiado!"),
        Texto("artigo.fechar", "Leitura de um artigo", "Botão de fechar a janela de citação", "Fechar"),
    ),
)
