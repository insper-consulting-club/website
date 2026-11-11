"""
Nomes de autor. O nome de um autor é guardado como foi escrito, no formato que o BibTeX lê: `Maria da Silva` serve
como está, e as chaves marcam o que não se separa (`Robert {Lucas Jr}`). Aqui ficam as regras que dependem disso:
comparar nomes, mostrar sem as chaves e conferir se elas fecham.
"""
import re
import unicodedata


def tira_chaves(nome):
    """O nome como aparece no site, sem as chaves do BibTeX."""
    return (nome or '').replace('{', '').replace('}', '').strip()


def normaliza(nome):
    """Para comparar nomes: sem chaves, acentos, maiúsculas nem espaços repetidos."""
    sem_acento = unicodedata.normalize('NFKD', tira_chaves(nome))
    sem_acento = ''.join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r'\s+', ' ', sem_acento).casefold()


def chaves_fecham(nome):
    """Falso se há `}` sem `{` antes, ou `{` que nunca fecha: o BibTeX não leria o nome."""
    aberto = 0
    for letra in nome or '':
        if letra == '{':
            aberto += 1
        elif letra == '}':
            aberto -= 1
            if aberto < 0:
                return False
    return aberto == 0
