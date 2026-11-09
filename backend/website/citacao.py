"""
Citação de um artigo em ABNT, APA, BibTeX, BibLaTeX e RIS.

Os nomes dos autores são guardados como foram escritos, no formato do BibTeX (`Maria da Silva`, `Robert {Lucas Jr}`), e
as citações em texto (ABNT, APA) e o RIS separam nome e sobrenome pelas regras do próprio BibTeX: o que vai entre
chaves não se separa, e o que a regra errar se resolve com chaves ou com o "Nome na citação" do membro.
O título é escapado para o LaTeX nos formatos que o usam. A data de acesso é de quem copia, e só o navegador a sabe:
as citações saem com marcadores, que o frontend troca pela data de hoje ao mostrar e ao copiar.

O ABNT e o APA foram conferidos com o BibLaTeX (biblatex-abnt e biblatex-apa) no desenvolvimento, e as diferenças
deliberadas estão nos testes.
"""
import re
import unicodedata
from dataclasses import dataclass

from django.conf import settings

from .models import Article

# O que o frontend troca pela data de hoje: em AAAA-MM-DD, no formato da ABNT (10 nov. 2026) e no do RIS (2026/11/10).
DATA_DE_ACESSO = '__DATA_DE_ACESSO__'
DATA_DE_ACESSO_ABNT = '__DATA_DE_ACESSO_ABNT__'
DATA_DE_ACESSO_RIS = '__DATA_DE_ACESSO_RIS__'

MESES = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']  # macros do BibTeX
MESES_ABNT = ['jan.', 'fev.', 'mar.', 'abr.', 'maio', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.']
MESES_POR_EXTENSO = [
    'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro',
    'dezembro',
]

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


@dataclass(frozen=True)
class NomeBibtex:
    """Um nome separado pelas regras do BibTeX: Nome, partícula (von), Sobrenome e sufixo (Jr)."""
    nome: str
    von: str
    sobrenome: str
    sufixo: str


def _sem_chaves(texto):
    return texto.replace('{', '').replace('}', '').strip()


def _von_e_sobrenome(palavras, tem_nome):
    """Divide em partícula e sobrenome. Com nome antes (sem vírgula), a primeira palavra é do nome."""
    inicio = 1 if tem_nome else 0
    von = [i for i, p in enumerate(palavras[:-1]) if i >= inicio and _comeca_em_minuscula(p)]
    if not von:
        return palavras[:0], (palavras[-1:] if tem_nome else palavras)
    return palavras[von[0]:von[-1] + 1], palavras[von[-1] + 1:]


def analisa_nome(nome):
    """
    Separa um nome como o BibTeX o lê. Sem vírgula (`Maria da Silva Lima`): a última palavra é o sobrenome, a menos que
    haja palavras em minúscula no meio (da, de, van), e aí o sobrenome é tudo o que vem depois delas. Com vírgula
    (`Silva Lima, Maria` ou `Lucas, Jr., Robert`): o que vem antes da primeira vírgula é partícula e sobrenome, e o resto
    é o nome (e o sufixo, quando há três partes). O que está entre chaves conta como uma palavra só.
    """
    partes = _separa_no_nivel_zero(nome, ',')
    if len(partes) == 1:
        palavras = _palavras_no_nivel_zero(nome)
        if len(palavras) <= 1:
            return NomeBibtex('', '', _sem_chaves(nome), '')
        von, sobrenome = _von_e_sobrenome(palavras, tem_nome=True)
        primeiro = palavras.index(von[0]) if von else len(palavras) - len(sobrenome)
        return NomeBibtex(
            _sem_chaves(' '.join(palavras[:primeiro])), _sem_chaves(' '.join(von)), _sem_chaves(' '.join(sobrenome)), '',
        )
    von, sobrenome = _von_e_sobrenome(_palavras_no_nivel_zero(partes[0]), tem_nome=False)
    sufixo = partes[1] if len(partes) >= 3 else ''
    primeiro = partes[-1]
    return NomeBibtex(_sem_chaves(primeiro), _sem_chaves(' '.join(von)), _sem_chaves(' '.join(sobrenome)), _sem_chaves(sufixo))


def sobrenome_bibtex(nome):
    """O sobrenome, sem a partícula, usado na chave da citação."""
    return analisa_nome(nome).sobrenome


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


# ---------------------------------------------------------------------------
# Citações em texto (ABNT e APA) e RIS
# ---------------------------------------------------------------------------

def _autores_analisados(artigo):
    nomes = nomes_dos_autores(artigo)
    return None if nomes is None else [analisa_nome(n) for n in nomes]


def _fecha(texto):
    """Termina com ponto, a menos que o texto já termine em pontuação (um título que acaba em ?)."""
    texto = texto.strip()
    return texto if texto[-1:] in '.?!' else texto + '.'


def _partes(*partes):
    """Junta as partes de uma citação: [(texto, destaque)], destaque sendo None, 'b' (negrito) ou 'i' (itálico)."""
    return [{'t': t, 'e': e} for t, e in partes if t]


def _citacao_em_texto(id_, rotulo, partes):
    return {'id': id_, 'label': rotulo, 'kind': 'texto', 'partes': partes, 'texto': ''.join(p['t'] for p in partes)}


def _data_abnt(data):
    return f'{data.day} {MESES_ABNT[data.month - 1]} {data.year}'


def _autor_abnt(nome):
    sobrenome = nome.sobrenome.upper() + (f' {nome.sufixo.upper().rstrip(".")}' if nome.sufixo else '')
    if not nome.nome:
        return sobrenome
    # Em português, a partícula (da, de) vai depois do nome: SILVA, Maria da.
    return f'{sobrenome}, {nome.nome}' + (f' {nome.von}' if nome.von else '')


def abnt(artigo):
    """
    ABNT (NBR 6023), para uma página de site. Como no biblatex-abnt: o título em negrito, o nome do site e a data depois
    dele, e mais de três autores viram o primeiro seguido de "et al." (em itálico).
    """
    url = _url_do_artigo(artigo)
    analisados = _autores_analisados(artigo)
    if analisados is None:
        autores = [(_fecha(Article.NOME_INSTITUCIONAL.upper()), None)]
    elif len(analisados) > 3:
        autores = [(_autor_abnt(analisados[0]) + ' ', None), ('et al', 'i'), ('.', None)]
    else:
        autores = [(_fecha('; '.join(_autor_abnt(n) for n in analisados)), None)]
    resto = [(' ', None), (_fecha(artigo.title), 'b'), (f' {Article.NOME_INSTITUCIONAL}.', None)]
    if artigo.date:
        resto.append((f' {_data_abnt(artigo.date)}.', None))
    if url:
        resto.append((f' Disponível em: {url}. Acesso em: {DATA_DE_ACESSO_ABNT}.', None))
    return _citacao_em_texto('abnt', 'ABNT', _partes(*autores, *resto))


def _iniciais(nome):
    """Iniciais para o APA: `Ana Paula` dá `A. P.`, e `Jean-Paul` dá `J.-P.`."""
    return ' '.join('-'.join(f'{parte[0].upper()}.' for parte in palavra.split('-') if parte) for palavra in nome.split())


def _autor_apa(nome):
    sobrenome = (f'{nome.von} ' if nome.von else '') + nome.sobrenome
    resultado = sobrenome + (f' {nome.sufixo.rstrip(".")}' if nome.sufixo else '')
    return f'{resultado}, {_iniciais(nome.nome)}' if nome.nome else resultado


def _data_apa(data):
    return f'({data.year}, {data.day} de {MESES_POR_EXTENSO[data.month - 1]})' if data else '(s.d.)'


def apa(artigo):
    """
    APA 7, para uma página de site: autor, (ano, dia de mês), título em itálico, nome do site e endereço. O nome do site
    não se repete quando o autor é o próprio clube. Não leva data de acesso: a APA só a pede em páginas que mudam.
    """
    url = _url_do_artigo(artigo)
    analisados = _autores_analisados(artigo)
    if analisados is None:
        autor = Article.NOME_INSTITUCIONAL
        site = ''
    else:
        nomes = [_autor_apa(n) for n in analisados]
        autor = nomes[0] if len(nomes) == 1 else ', '.join(nomes[:-1]) + ', & ' + nomes[-1]
        site = f' {Article.NOME_INSTITUCIONAL}.'
    return _citacao_em_texto('apa', 'APA', _partes(
        (_fecha(autor), None), (f' {_data_apa(artigo.date)}. ', None), (_fecha(artigo.title), 'i'),
        (site, None), (f' {url}' if url else '', None),
    ))


def ris(artigo):
    """A referência em RIS, o formato que Zotero, Mendeley e EndNote importam."""
    url = _url_do_artigo(artigo)
    analisados = _autores_analisados(artigo)
    if analisados is None:
        autores = [Article.NOME_INSTITUCIONAL]
    else:
        autores = [
            ((f'{n.von} ' if n.von else '') + n.sobrenome + (f', {n.nome}' if n.nome else '') + (f', {n.sufixo}' if n.sufixo else ''))
            for n in analisados
        ]
    linhas = [('TY', 'ELEC')] + [('AU', a) for a in autores] + [
        ('TI', artigo.title.strip()), ('PB', Article.NOME_INSTITUCIONAL),
    ]
    if artigo.date:
        linhas += [('PY', str(artigo.date.year)), ('DA', artigo.date.strftime('%Y/%m/%d'))]
    if url:
        linhas += [('UR', url), ('Y2', DATA_DE_ACESSO_RIS)]
    linhas += [('LA', 'pt'), ('ER', '')]
    return '\n'.join(f'{marca}  - {valor}' for marca, valor in linhas) + '\n'


def citacoes(artigo):
    """As citações que a API entrega, na ordem em que o site as oferece."""
    em_codigo = lambda id_, rotulo, texto: {'id': id_, 'label': rotulo, 'kind': 'codigo', 'texto': texto}  # noqa: E731
    return [
        abnt(artigo),
        apa(artigo),
        em_codigo('bibtex', 'BibTeX', bibtex(artigo)),
        em_codigo('biblatex', 'BibLaTeX', biblatex(artigo)),
        em_codigo('ris', 'RIS', ris(artigo)),
    ]
