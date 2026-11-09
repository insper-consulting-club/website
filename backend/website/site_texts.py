"""
Os textos editáveis do site ficam no registro de conteúdo (`website/conteudo/`), uma página por módulo. Este arquivo
mantém a forma antiga (TEXTOS, PADRAO, GRUPOS) para o restante do código e faz a sincronização com o banco depois de
cada migração. Veja `conteudo/__init__.py` para acrescentar um texto ou uma página.
"""
from .conteudo import PADRAO, PAGINAS, SECOES_DA_HOME

# (chave, grupo, descrição, texto original), na ordem das páginas e dos textos.
TEXTOS = [(texto.chave, pagina.titulo, texto.rotulo, texto.padrao) for pagina in PAGINAS for texto in pagina.textos]
GRUPOS = [pagina.titulo for pagina in PAGINAS]

def sincroniza_textos(model=None):
    """
    Cria no banco os textos do catálogo que ainda não existem. Nunca altera o
    valor de um texto já cadastrado, para não desfazer o que o editor mudou.
    Textos que saíram do catálogo são removidos.
    """
    if model is None:
        from .models import SiteText as model

    existentes = {t.key: t for t in model.objects.all()}
    for ordem, (chave, grupo, descricao, texto) in enumerate(TEXTOS):
        atual = existentes.pop(chave, None)
        if atual is None:
            model.objects.create(key=chave, group=grupo, description=descricao, value=texto, order=ordem)
        elif (atual.group, atual.description, atual.order) != (grupo, descricao, ordem):
            # Só a organização acompanha o catálogo; o valor é do editor.
            model.objects.filter(pk=atual.pk).update(group=grupo, description=descricao, order=ordem)
    if existentes:
        model.objects.filter(key__in=existentes).delete()


def sincroniza_paginas(model=None):
    """Cria as páginas do admin (uma por módulo do registro), mantém título, ordem e endereço, e remove as que saíram."""
    if model is None:
        from .models import PaginaDoSite as model

    existentes = {p.slug: p for p in model.objects.all()}
    for ordem, pagina in enumerate(PAGINAS):
        atual = existentes.pop(pagina.slug, None)
        if atual is None:
            model.objects.create(slug=pagina.slug, title=pagina.titulo, path=pagina.caminho, order=ordem)
        elif (atual.title, atual.path, atual.order) != (pagina.titulo, pagina.caminho, ordem):
            model.objects.filter(pk=atual.pk).update(title=pagina.titulo, path=pagina.caminho, order=ordem)
    if existentes:
        model.objects.filter(slug__in=existentes).delete()


def sincroniza_secoes(model=None):
    """
    Cria as seções da Home que ainda não existem. Num banco novo, valem a ordem e a visibilidade do registro. Depois,
    só o título acompanha o registro: o que o editor definiu (mostrar, esconder, ordem, botão) não se altera, e uma
    seção que nasce depois entra no fim. As que saíram do registro são removidas.
    """
    if model is None:
        from .models import SecaoDaHome as model

    existentes = {s.key: s for s in model.objects.all()}
    banco_novo = not existentes
    proxima = max((s.order for s in existentes.values()), default=-1) + 1
    for ordem, secao in enumerate(SECOES_DA_HOME):
        atual = existentes.pop(secao.chave, None)
        if atual is None:
            model.objects.create(key=secao.chave, title=secao.titulo, visible=secao.visivel,
                                 order=ordem if banco_novo else proxima)
            proxima += 1
        elif atual.title != secao.titulo:
            model.objects.filter(pk=atual.pk).update(title=secao.titulo)
    if existentes:
        model.objects.filter(key__in=existentes).delete()

