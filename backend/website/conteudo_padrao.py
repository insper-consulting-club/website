"""
Conteúdo padrão da Configuração do site que não é texto de campo: os itens de navegação e os
benefícios para parceiros que um banco novo recebe.

Um teste confere que os dados que as migrations criam são iguais a esta lista. Os textos de campo
(Home, rodapé, páginas) têm o valor padrão no próprio campo, em `models.py`, e os textos curtos
ficam em `website/conteudo/`.

Para mudar o padrão de um banco novo, mude aqui e crie uma migration; os bancos que já existem
guardam o que o editor escolheu.
"""

# (texto, área, página, ordem)
NAV_ITEMS_PADRAO = [
    ('Nossa Equipe', 'menu', 'equipe', 1),
    ('Parceiros', 'menu', 'parceiros', 2),
    ('Projetos', 'menu', 'projetos', 3),
    ('Artigos', 'menu', 'artigos', 4),
    ('Seja membro', 'rodape', 'processo', 5),
    ('Contato', 'menu', 'contato', 6),
    ('Seja membro', 'botao', 'processo', 7),
]

# (título, descrição, ordem)
BENEFICIOS_PADRAO = [
    (
        'Acesso a talentos',
        'Contato direto com alunos de alta performance, treinados em resolução de cases e raciocínio analítico.',
        1,
    ),
    (
        'Visibilidade Institucional',
        'Presença em eventos, capacitações e redes sociais com crescimento consistente de alcance e engajamento.',
        2,
    ),
    (
        'Cases aplicados à realidade',
        'Possibilidade de propor desafios reais de negócio para serem resolvidos pelos nossos grupos de trainees '
        'e do Pedagógico.',
        3,
    ),
]
