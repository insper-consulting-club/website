"""
Registro de conteúdo: os textos editáveis do site, declarados uma vez, por página.

Cada página tem um módulo em `conteudo/paginas/`. Daqui saem, sem repetir nada: a tela "Textos do site" do admin
(páginas, seções, rótulos, o campo certo para cada tipo), os textos que nascem no banco e a conferência dos
trechos obrigatórios. O frontend não guarda cópia: lê tudo da API (e da cópia que o build grava no HTML).

Para acrescentar um texto:
1. Declare-o no módulo da página, em `Texto(chave, seção, rótulo, padrão)`. A chave é a que o frontend usa.
2. Use a chave no componente do frontend, com `t("a.chave")`.
O texto nasce no banco na próxima migração, com o valor padrão, sem mexer no que o ICC já editou.

Para acrescentar uma página, crie o módulo em `paginas/` e inclua-o na lista abaixo, na posição em que ela deve aparecer.
"""
from .paginas import (
    artigos, contato, equipe, home, membro, nao_encontrada, parceiro, parceiros, privacidade, processo, programa,
    projeto, projetos, rodape,
)

# A ordem é a das abas do admin: a das páginas no site.
PAGINAS = (
    home.PAGINA, equipe.PAGINA, membro.PAGINA, parceiros.PAGINA, parceiro.PAGINA, projetos.PAGINA, programa.PAGINA,
    projeto.PAGINA, artigos.PAGINA, processo.PAGINA, privacidade.PAGINA, contato.PAGINA, nao_encontrada.PAGINA,
    rodape.PAGINA,
)

POR_SLUG = {pagina.slug: pagina for pagina in PAGINAS}
POR_CHAVE = {texto.chave: (pagina, texto) for pagina in PAGINAS for texto in pagina.textos}
PADRAO = {chave: texto.padrao for chave, (_pagina, texto) in POR_CHAVE.items()}

