from ..base import Pagina, Texto

PAGINA = Pagina(
    slug="home", titulo="Home", caminho="/",
    textos=(
        Texto("home.hero_botao_principal", "Apresentação", "Botão principal, logo abaixo da frase de apresentação", "Seja membro"),
        Texto("home.hero_botao_secundario", "Apresentação", "Botão secundário, ao lado do principal", "Conheça os projetos"),
        Texto("home.sobre_eyebrow", "Quem somos", "Palavra pequena acima do título de “Quem somos”", "Quem somos"),
        Texto("home.missao_eyebrow", "Missão", "Palavra pequena acima da frase da missão", "Missão"),
        Texto("home.missao_como_titulo", "Missão", "Título do primeiro bloco da missão (“como preparamos”)", "Como preparamos"),
        Texto("home.missao_meta_titulo", "Missão", "Título do segundo bloco da missão (“onde queremos chegar”)", "Onde queremos chegar"),
        Texto("home.programas_eyebrow", "Programas", "Palavra pequena acima do título da seção", "Projetos"),
        Texto("home.programas_titulo", "Programas", "Título da seção", "Nossos programas e cases"),
        Texto("home.programas_link", "Programas", "Link para a lista completa de projetos", "Ver todos os projetos"),
        Texto("home.programa_card_link", "Programas", "Link no fim de cada cartão de programa", "Saiba mais"),
        Texto("home.membros_eyebrow", "Equipe", "Palavra pequena acima do título da seção", "Membros"),
        Texto("home.membros_titulo", "Equipe", "Título da seção", "Quem constrói o clube"),
        Texto("home.membros_link", "Equipe", "Link para a equipe completa", "Ver equipe completa"),
        Texto("home.parceiros_eyebrow", "Parceiros", "Palavra pequena acima do título da seção", "Parceiros"),
        Texto("home.parceiros_titulo", "Parceiros", "Título da seção", "Empresas que confiam no nosso trabalho"),
        Texto("home.parceiros_link", "Parceiros", "Link para todos os parceiros", "Ver todos os parceiros"),
        Texto("home.cta_botao_principal", "Chamada final", "Botão principal", "Faça parte do ICC"),
        Texto("home.cta_botao_secundario", "Chamada final", "Botão secundário", "Fale com a gente"),
    ),
)
