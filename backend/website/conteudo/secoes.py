"""As seções da Home que o editor mostra, esconde e reordena (ver SecaoDaHome no admin)."""
from .base import Secao

# O aviso vem primeiro e escondido: num banco novo, fica logo depois da Apresentação, e só aparece quando alguém o liga.
SECOES_DA_HOME = (
    Secao("aviso", "Aviso", visivel=False),
    Secao("quem_somos", "Quem somos"),
    Secao("estatisticas", "Estatísticas"),
    Secao("missao", "Missão"),
    Secao("programas", "Programas"),
    Secao("equipe", "Equipe"),
    Secao("parceiros", "Parceiros"),
    Secao("chamada_final", "Chamada final"),
)

SECAO_POR_CHAVE = {secao.chave: secao for secao in SECOES_DA_HOME}
