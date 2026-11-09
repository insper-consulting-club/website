"""Blocos do registro de conteúdo: cada texto editável do site é declarado uma vez, na página onde aparece."""
from dataclasses import dataclass

# Acima deste tamanho (do texto original), o admin mostra uma caixa de várias linhas em vez de uma linha.
LIMITE_DE_TEXTO_LONGO = 80


@dataclass(frozen=True)
class Texto:
    """
    Um texto editável.

    chave    o que o frontend usa para buscá-lo, por exemplo "home.membros_titulo". Não mude uma chave que já existe:
             o valor que o ICC editou está guardado nela.
    secao    o bloco da página onde o texto aparece (agrupa os campos na tela do admin).
    rotulo   onde e como o texto aparece, em linguagem simples (é o nome do campo no admin).
    padrao   o texto original: vale até alguém editá-lo, e "Restaurar o original" volta a ele. Trechos entre chaves,
             como {n} ou {data}, são preenchidos pelo site e precisam ser mantidos pelo editor.
    tipo     "curto" (uma linha) ou "longo" (várias linhas). Sem informar, vale "longo" para textos originais compridos.
    raro     True para mensagens que quase ninguém edita (erros, "não existe", formas no plural): ficam recolhidas.
    opcional True quando o texto pode ficar vazio (o site simplesmente não o mostra).
    """
    chave: str
    secao: str
    rotulo: str
    padrao: str
    tipo: str = ""
    raro: bool = False
    opcional: bool = False

    @property
    def e_longo(self):
        return self.tipo == "longo" or (self.tipo != "curto" and len(self.padrao) > LIMITE_DE_TEXTO_LONGO)


@dataclass(frozen=True)
class Pagina:
    """Uma página do site e os textos que ela tem. A ordem das páginas e dos textos é a da tela do admin."""
    slug: str
    titulo: str
    caminho: str  # endereço no site, para o botão "Ver no site"
    textos: tuple
