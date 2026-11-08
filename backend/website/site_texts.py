"""
Catálogo dos textos do site editáveis no admin (Textos do site).

Cada entrada é (chave, grupo, descrição, texto original):
- a chave é o que o frontend usa para buscar o texto (ex.: "home.membros_titulo");
- o grupo é a página onde o texto aparece, e organiza a tela do admin;
- a descrição diz ao editor onde o texto aparece;
- o texto original vale até alguém editá-lo, e a ação "Restaurar texto original"
  do admin volta a ele.

Trechos entre chaves, como {n} ou {data}, são preenchidos pelo site e precisam
ser mantidos no texto.

Para acrescentar um texto: inclua a linha aqui, rode `python manage.py
export_site_texts` para atualizar o arquivo do frontend (a chave nova nasce no
banco na próxima migração) e use a chave no código do frontend.
"""

TEXTOS = [
    # Home
    ("home.hero_botao_principal", "Home", "Botão principal do topo", "Seja membro"),
    ("home.hero_botao_secundario", "Home", "Botão secundário do topo", "Conheça os projetos"),
    ("home.sobre_eyebrow", "Home", "Rótulo acima de \"Quem somos\"", "Quem somos"),
    ("home.missao_eyebrow", "Home", "Rótulo acima da missão", "Missão"),
    ("home.missao_como_titulo", "Home", "Título de \"como preparamos\"", "Como preparamos"),
    ("home.missao_meta_titulo", "Home", "Título de \"onde queremos chegar\"", "Onde queremos chegar"),
    ("home.programas_eyebrow", "Home", "Rótulo acima dos programas", "Projetos"),
    ("home.programas_titulo", "Home", "Título da seção de programas", "Nossos programas e cases"),
    ("home.programas_link", "Home", "Link da seção de programas", "Ver todos os projetos"),
    ("home.programa_card_link", "Home", "Link de cada card de programa", "Saiba mais"),
    ("home.membros_eyebrow", "Home", "Rótulo acima dos membros", "Membros"),
    ("home.membros_titulo", "Home", "Título da seção de membros", "Quem constrói o clube"),
    ("home.membros_link", "Home", "Link da seção de membros", "Ver equipe completa"),
    ("home.parceiros_eyebrow", "Home", "Rótulo acima dos parceiros", "Parceiros"),
    ("home.parceiros_titulo", "Home", "Título da seção de parceiros", "Empresas que confiam no nosso trabalho"),
    ("home.parceiros_link", "Home", "Link da seção de parceiros", "Ver todos os parceiros"),
    ("home.cta_botao_principal", "Home", "Botão principal da chamada final", "Faça parte do ICC"),
    ("home.cta_botao_secundario", "Home", "Botão secundário da chamada final", "Fale com a gente"),

    # Equipe
    ("equipe.eyebrow", "Equipe", "Rótulo acima do título da página", "Membros"),
    ("equipe.titulo", "Equipe", "Título da página (e da aba do navegador)", "Nossa Equipe"),
    ("equipe.vazio", "Equipe", "Mensagem quando não há membros", "Nenhum membro cadastrado no momento."),
    ("equipe.contagem_um", "Equipe", "Contagem de uma diretoria com 1 membro", "{n} membro"),
    ("equipe.contagem_varios", "Equipe", "Contagem de uma diretoria com mais de 1 membro", "{n} membros"),
    ("equipe.outros", "Equipe", "Nome do grupo de quem não está em nenhuma diretoria", "Outros"),

    # Perfil do membro
    ("membro.voltar", "Perfil do membro", "Link para voltar à Equipe", "Voltar para a equipe"),
    ("membro.nao_encontrado_titulo", "Perfil do membro", "Título quando o perfil não existe", "Membro não encontrado"),
    ("membro.nao_encontrado_texto", "Perfil do membro", "Texto quando o perfil não existe", "O perfil procurado não existe ou foi removido."),
    ("membro.trajetoria", "Perfil do membro", "Título da trajetória", "Trajetória no ICC"),
    ("membro.atual", "Perfil do membro", "Marca da etapa atual na trajetória", "Atual"),

    # Parceiros
    ("parceiros.eyebrow", "Parceiros", "Rótulo acima do título da página (e nome da aba do navegador)", "Parceiros"),
    ("parceiros.titulo", "Parceiros", "Título da página, antes da palavra em destaque", "Quem caminha"),
    ("parceiros.titulo_destaque", "Parceiros", "Palavra em destaque (vermelha) do título", "conosco"),
    ("parceiros.vazio", "Parceiros", "Mensagem quando não há parceiros", "Em breve, novos parceiros."),
    ("parceiros.card_link", "Parceiros", "Link de cada card de parceiro", "Ver detalhes"),
    ("parceiros.beneficios_eyebrow", "Parceiros", "Rótulo acima de \"Por que ser parceiro\"", "Por que ser parceiro"),
    ("parceiros.botao_contato", "Parceiros", "Botão de contato no fim da página", "Fale com a gente"),

    # Perfil do parceiro
    ("parceiro.voltar", "Perfil do parceiro", "Link para voltar a Parceiros", "Voltar para parceiros"),
    ("parceiro.nao_encontrado_titulo", "Perfil do parceiro", "Título quando o parceiro não existe", "Parceiro não encontrado"),
    ("parceiro.nao_encontrado_texto", "Perfil do parceiro", "Texto quando o parceiro não existe", "Não foi possível carregar esse parceiro."),
    ("parceiro.visitar_site", "Perfil do parceiro", "Botão para o site do parceiro", "Visitar site"),
    ("parceiro.casos", "Perfil do parceiro", "Título dos projetos concluídos com o parceiro", "Casos de sucesso"),
    ("parceiro.caso_link", "Perfil do parceiro", "Link de cada caso", "Ver projeto"),
    ("parceiro.outros", "Perfil do parceiro", "Título dos outros parceiros da categoria. Use {categoria}", "Outros parceiros em {categoria}"),
    ("parceiro.todos", "Perfil do parceiro", "Link para a lista de parceiros", "Todos os parceiros"),

    # Projetos
    ("projetos.eyebrow", "Projetos", "Rótulo acima do título da página (e nome da aba do navegador)", "Projetos"),
    ("projetos.titulo", "Projetos", "Título da página, antes da palavra em destaque", "Programas e"),
    ("projetos.titulo_destaque", "Projetos", "Palavra em destaque (vermelha) do título", "cases"),
    ("projetos.outros_eyebrow", "Projetos", "Rótulo acima de \"Outros projetos\"", "Além dos programas"),
    ("projetos.outros_titulo", "Projetos", "Título dos projetos sem programa", "Outros projetos"),
    ("projetos.cases_eyebrow", "Projetos", "Rótulo da seção de cases em destaque", "Cases resolvidos"),
    ("projetos.cases_titulo_um", "Projetos", "Título da seção de cases com 1 case. Use {programa} e {n}", "{programa}: {n} case"),
    ("projetos.cases_titulo_varios", "Projetos", "Título da seção de cases com mais de 1 case. Use {programa} e {n}", "{programa}: {n} cases"),
    ("projetos.cases_botao", "Projetos", "Botão da seção de cases em destaque", "Ver os cases"),

    # Página de um programa
    ("programa.voltar", "Programa", "Link para voltar à lista de projetos", "Todos os projetos"),
    ("programa.botao_inscricao", "Programa", "Botão de inscrição do programa", "Formulário de inscrição"),
    ("programa.como_funciona", "Programa", "Título dos componentes do programa", "Como funciona"),
    ("programa.beneficios", "Programa", "Título dos tópicos do programa", "Benefícios"),
    ("programa.projetos_titulo", "Programa", "Título dos projetos do programa", "Projetos"),
    ("programa.cases_titulo", "Programa", "Título dos cases do programa", "Cases resolvidos"),
    ("programa.case_banca", "Programa", "Rótulo da banca avaliadora de um case", "Banca avaliadora"),
    ("programa.case_grupo", "Programa", "Rótulo do grupo de um case", "Grupo vencedor"),
    ("programa.case_mentor", "Programa", "Rótulo do mentor de um case", "Mentor(a)"),
    ("programa.case_premiacao", "Programa", "Rótulo da premiação de um case", "Premiação"),
    ("programa.case_link", "Programa", "Link da publicação de um case", "Ver post do case"),
    ("programa.outros_eyebrow", "Programa", "Rótulo acima dos outros programas", "Projetos"),
    ("programa.outros_titulo", "Programa", "Título dos outros programas", "Outros programas"),
    ("programa.outros_link", "Programa", "Link de cada outro programa", "Saiba mais"),

    # Página de um projeto
    ("projeto.voltar", "Projeto", "Link para voltar quando o projeto não tem programa", "Todos os projetos"),
    ("projeto.nao_encontrado_titulo", "Projeto", "Título quando o projeto não existe", "Projeto não encontrado"),
    ("projeto.nao_encontrado_texto", "Projeto", "Texto quando o projeto não existe", "Não foi possível carregar esse projeto."),
    ("projeto.rotulo_data", "Projeto", "Rótulo da data de um projeto de um dia só", "Data"),
    ("projeto.rotulo_periodo", "Projeto", "Rótulo do período do projeto", "Período"),
    ("projeto.periodo_desde", "Projeto", "Período de projeto em andamento. Use {inicio}", "Desde {inicio}"),
    ("projeto.periodo_intervalo", "Projeto", "Período de projeto concluído. Use {inicio} e {fim}", "{inicio} a {fim}"),
    ("projeto.rotulo_situacao", "Projeto", "Rótulo da situação do projeto", "Situação"),
    ("projeto.concluido", "Projeto", "Situação de projeto concluído", "Concluído"),
    ("projeto.em_andamento", "Projeto", "Situação de projeto em andamento", "Em andamento"),
    ("projeto.rotulo_parceiro", "Projeto", "Rótulo quando há 1 parceiro", "Parceiro"),
    ("projeto.rotulo_parceiros", "Projeto", "Rótulo quando há mais de 1 parceiro", "Parceiros"),
    ("projeto.linha_do_tempo", "Projeto", "Título do cronograma", "Linha do tempo"),
    ("projeto.imagens", "Projeto", "Título da galeria", "Imagens"),
    ("projeto.equipe", "Projeto", "Título da equipe do projeto", "Equipe"),
    ("projeto_card.concluido_em", "Projeto", "Rodapé do card de projeto concluído. Use {data}", "Concluído em {data}"),
    ("projeto_card.link", "Projeto", "Link do card de projeto", "Ver projeto"),

    # Artigos
    ("artigos.titulo", "Artigos", "Título da página (e da aba do navegador)", "Artigos"),
    ("artigos.vazio", "Artigos", "Mensagem quando não há artigos", "Nenhum artigo cadastrado no momento."),
    ("artigos.card_link", "Artigos", "Link de cada card de artigo", "Ler artigo"),
    ("artigo.voltar", "Artigos", "Link para voltar à lista de artigos", "Voltar para artigos"),
    ("artigo.nao_encontrado_titulo", "Artigos", "Título quando o artigo não existe", "Artigo não encontrado"),
    ("artigo.nao_encontrado_texto", "Artigos", "Texto quando o artigo não existe", "Não foi possível carregar esse artigo."),
    ("artigo.resumo", "Artigos", "Título do resumo do artigo", "Resumo"),
    ("artigo.como_citar", "Artigos", "Título da citação", "Como citar"),
    ("artigo.copiar", "Artigos", "Botão de copiar a citação", "Copiar citação"),
    ("artigo.copiado", "Artigos", "Aviso depois de copiar a citação", "Copiado!"),
    ("artigo.compartilhar", "Artigos", "Botão de compartilhar no LinkedIn", "Compartilhar"),
    ("artigo.link_original", "Artigos", "Botão para a publicação original", "Ver publicação original"),

    # Processo seletivo
    ("processo.eyebrow", "Processo seletivo", "Rótulo acima do título da página", "Seja membro"),
    ("processo.titulo", "Processo seletivo", "Título da página quando não há processo ativo", "Processo Seletivo"),
    ("processo.abertas", "Processo seletivo", "Chamada com inscrições abertas", "Inscrições abertas!"),
    ("processo.botao_inscricao", "Processo seletivo", "Botão de inscrição", "Inscreva-se"),
    ("processo.botao_instagram", "Processo seletivo", "Botão com inscrições encerradas", "Seguir no Instagram"),
    ("processo.sem_processo_titulo", "Processo seletivo", "Título quando não há processo ativo", "Nenhum processo seletivo ativo no momento."),
    ("processo.sem_processo_texto", "Processo seletivo", "Texto quando não há processo ativo", "Assim que abrirmos novas vagas, as inscrições aparecem aqui."),
    ("processo.calendario", "Processo seletivo", "Título do calendário", "Calendário"),
    ("processo.etapas", "Processo seletivo", "Título das etapas", "Etapas do processo"),
    ("processo.requisitos", "Processo seletivo", "Título dos requisitos", "Requisitos"),
    ("processo.materiais", "Processo seletivo", "Título dos materiais de preparação", "Materiais de preparação"),

    # Política de Privacidade (o texto da política fica em Configuração do site)
    ("privacidade.titulo", "Política de Privacidade", "Título da página (e da aba do navegador)", "Política de Privacidade"),
    ("privacidade.erro", "Política de Privacidade", "Aviso quando o texto da política não carrega", "Não foi possível exibir a política agora. Para qualquer dúvida sobre o tratamento dos seus dados, escreva para o e-mail abaixo."),

    # Contato
    ("contato.titulo", "Contato", "Título da página (e da aba do navegador)", "Contato"),
    ("contato.canais_titulo", "Contato", "Título da lista de canais", "Canais oficiais"),

    # Página não encontrada
    ("nao_encontrada.eyebrow", "Página não encontrada", "Rótulo acima do título", "Erro 404"),
    ("nao_encontrada.titulo", "Página não encontrada", "Título", "Página não encontrada"),
    ("nao_encontrada.texto", "Página não encontrada", "Texto de apoio", "O endereço acessado não existe ou foi alterado."),
    ("nao_encontrada.botao", "Página não encontrada", "Botão para voltar", "Voltar para o início"),

    # Rodapé
    ("rodape.navegacao", "Rodapé", "Título da coluna de navegação", "Navegação"),
    ("rodape.programas", "Rodapé", "Título da coluna de programas", "Programas"),
    ("rodape.contato", "Rodapé", "Título da coluna de contato", "Contato"),
    ("rodape.privacidade", "Rodapé", "Link da Política de Privacidade", "Política de Privacidade"),
    ("rodape.admin", "Rodapé", "Link da área administrativa", "Área administrativa"),
]

PADRAO = {chave: texto for chave, _grupo, _descricao, texto in TEXTOS}
GRUPOS = list(dict.fromkeys(grupo for _chave, grupo, _d, _t in TEXTOS))


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
