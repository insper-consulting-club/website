from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="parceiros", titulo="Parceiros", caminho="/parceiros",
    textos=(
        Texto("parceiros.eyebrow", "Cabeçalho da página", "Palavra pequena acima do título (também é o nome da aba do navegador)", "Parceiros"),
        Texto("parceiros.titulo", "Cabeçalho da página", "Título, antes da palavra em destaque", "Quem caminha"),
        Texto("parceiros.titulo_destaque", "Cabeçalho da página", "Palavra em destaque (em vermelho) no fim do título", "conosco"),
        Texto("parceiros.abertura", "Cabeçalho da página", "Texto logo abaixo do título", "Conheça as empresas que apoiam o Insper Consulting Club e contribuem para a formação dos futuros líderes em consultoria."),
        Texto("parceiros.vazio", "Lista de parceiros", "Mensagem quando não há nenhum parceiro", "Em breve, novos parceiros.", raro=True),
        Texto("parceiros.card_link", "Lista de parceiros", "Link no fim de cada cartão de parceiro", "Ver detalhes", raro=True),
        Texto("parceiros.beneficios_titulo", "Por que ser parceiro", "Título da seção", "O que sua empresa ganha ao apoiar o Insper Consulting Club"),
        Texto("parceiros.beneficios_eyebrow", "Por que ser parceiro", "Palavra pequena acima do título da seção", "Por que ser parceiro"),
        Texto("parceiros.botao_contato", "Por que ser parceiro", "Botão de contato no fim da página", "Fale com a gente", raro=True),
    ),
)
