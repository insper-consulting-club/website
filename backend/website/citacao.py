"""
Citação de um artigo em BibLaTeX e em BibTeX.

Os nomes dos autores entram como foram escritos: já estão no formato do BibTeX (`Maria da Silva`, `Robert {Lucas Jr}`).
O título é escapado para o LaTeX. A data de acesso é de quem copia, e só o navegador a sabe: as referências saem com
o marcador `DATA_DE_ACESSO`, que o frontend troca pela data de hoje ao mostrar e ao copiar.
"""
import re
import unicodedata

from django.conf import settings

from .models import Article

# O que o frontend troca pela data de hoje (AAAA-MM-DD).
DATA_DE_ACESSO = '__DATA_DE_ACESSO__'

MESES = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']

# Palavras que não servem de "palavra do título" na chave da citação.
PALAVRAS_VAZIAS = {
    'a', 'o', 'as', 'os', 'um', 'uma', 'uns', 'umas', 'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na', 'nos', 'nas',
    'para', 'por', 'com', 'e', 'ou', 'the', 'of', 'and', 'in', 'on', 'for', 'to', 'an',
}

_ESCAPES = {
    '\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
    '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
}


def escapa_latex(texto):
    """Escapa os caracteres que o LaTeX leria como comando, numa só passada (para não escapar o que acabou de entrar)."""
    return re.sub(r'[\\&%$#_{}~^]', lambda m: _ESCAPES[m.group()], texto)


def _escapa_nome(nome):
    # O nome já usa chaves como o BibTeX (e a barra invertida de um acento TeX): só os demais caracteres especiais.
    return nome.replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#').replace('_', r'\_')


def _sem_acento(texto):
    decomposto = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in decomposto if not unicodedata.combining(c))


def _palavras_no_nivel_zero(texto):
    """Divide em palavras por espaço, sem separar o que está entre chaves: `Robert {Lucas Jr}` tem duas palavras."""
    palavras, atual, fundo = [], '', 0
    for letra in texto:
        if letra == '{':
            fundo += 1
        elif letra == '}':
            fundo = max(0, fundo - 1)
        if letra.isspace() and fundo == 0:
            if atual:
                palavras.append(atual)
            atual = ''
        else:
            atual += letra
    if atual:
        palavras.append(atual)
    return palavras


def _comeca_em_minuscula(palavra):
    for letra in palavra.lstrip('{'):
        if letra.isalpha():
            return letra.islower()
    return False


def sobrenome_bibtex(nome):
    """
    O sobrenome como o BibTeX o lê, usado só na chave da citação. Sem vírgula, é a última palavra (o que está entre
    chaves conta como uma palavra só), ou tudo o que vem depois da última palavra em minúscula (da, de, van, von) que
    não seja a primeira: `Maria da Silva Lima` dá `Silva Lima`. Com vírgula, vale a parte antes dela, com a mesma regra
    para o von: `Silva Lima, Maria` dá `Silva Lima`.
    """
    partes = _separa_no_nivel_zero(nome, ',')
    palavras = _palavras_no_nivel_zero(partes[0])
    if not palavras:
        return ''
    # Sem vírgula, a primeira palavra é sempre do nome próprio; com vírgula, a parte já começa no sobrenome.
    inicio = 1 if len(partes) == 1 else 0
    von = [i for i, p in enumerate(palavras[:-1]) if i >= inicio and _comeca_em_minuscula(p)]
    if von:
        resto = palavras[von[-1] + 1:]
    else:
        resto = palavras[-1:] if len(partes) == 1 else palavras
    return ' '.join(resto).replace('{', '').replace('}', '')


def _separa_no_nivel_zero(texto, separador):
    partes, atual, fundo = [], '', 0
    for letra in texto:
        if letra == '{':
            fundo += 1
        elif letra == '}':
            fundo = max(0, fundo - 1)
        if letra == separador and fundo == 0:
            partes.append(atual)
            atual = ''
        else:
            atual += letra
    partes.append(atual)
    return partes


def _so_letras_e_numeros(texto):
    return re.sub(r'[^a-z0-9]', '', _sem_acento(texto).lower())


def _palavra_do_titulo(titulo):
    for palavra in re.findall(r'[^\W_]+', _sem_acento(titulo).lower()):
        if palavra not in PALAVRAS_VAZIAS and len(palavra) > 1 and not palavra.isdigit():
            return palavra
    return 'artigo'


def nomes_dos_autores(artigo):
    """Os nomes na ordem, ou None quando o autor é o próprio clube (institucional, ou sem autores)."""
    if artigo.institutional:
        return None
    nomes = [autor.name for autor in artigo.article_authors.all()]
    return nomes or None


def chave_da_citacao(artigo):
    """Sobrenome do primeiro autor, ano e primeira palavra do título: silva2026precificacao. Institucional: icc2026..."""
    nomes = nomes_dos_autores(artigo)
    quem = _so_letras_e_numeros(sobrenome_bibtex(nomes[0])) if nomes else 'icc'
    ano = str(artigo.date.year) if artigo.date else ''
    return f'{quem or "icc"}{ano}{_palavra_do_titulo(artigo.title)}'


def _url_do_artigo(artigo):
    base = settings.FRONTEND_URL.rstrip('/')
    return f'{base}/artigos/{artigo.slug or artigo.pk}' if base else None


def _campos(pares):
    """Os campos de uma entrada, com os sinais de igual alinhados."""
    pares = [(nome, valor) for nome, valor in pares if valor is not None]
    largura = max(len(nome) for nome, _ in pares)
    return ''.join(f'  {nome.ljust(largura)} = {valor},\n' for nome, valor in pares)


def _autor(artigo):
    nomes = nomes_dos_autores(artigo)
    if nomes is None:
        return '{{' + Article.NOME_INSTITUCIONAL + '}}'  # autor institucional: chaves duplas, para não virar sobrenome
    return '{' + ' and '.join(_escapa_nome(n) for n in nomes) + '}'


def biblatex(artigo):
    """A referência em BibLaTeX (@online), com o marcador da data de acesso."""
    url = _url_do_artigo(artigo)
    corpo = _campos([
        ('author', _autor(artigo)),
        ('title', '{' + escapa_latex(artigo.title.strip()) + '}'),
        ('organization', '{' + Article.NOME_INSTITUCIONAL + '}'),
        ('date', '{' + artigo.date.isoformat() + '}' if artigo.date else None),
        ('url', '{' + url + '}' if url else None),
        ('urldate', '{' + DATA_DE_ACESSO + '}' if url else None),
        ('langid', '{brazilian}'),
    ])
    return f'@online{{{chave_da_citacao(artigo)},\n{corpo}}}'


def bibtex(artigo):
    """A referência em BibTeX clássico (@misc), com o marcador da data de acesso."""
    url = _url_do_artigo(artigo)
    corpo = _campos([
        ('author', _autor(artigo)),
        # Chaves duplas no título: os estilos clássicos passam o título para minúsculas, e isso estragaria siglas.
        ('title', '{{' + escapa_latex(artigo.title.strip()) + '}}'),
        ('organization', '{' + Article.NOME_INSTITUCIONAL + '}'),
        ('year', '{' + str(artigo.date.year) + '}' if artigo.date else None),
        ('month', MESES[artigo.date.month - 1] if artigo.date else None),
        ('howpublished', '{\\url{' + url + '}}' if url else None),
        ('note', '{Acesso em: ' + DATA_DE_ACESSO + '}' if url else None),
    ])
    return f'@misc{{{chave_da_citacao(artigo)},\n{corpo}}}'
