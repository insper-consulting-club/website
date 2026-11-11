# Arquitetura

Visão técnica do sistema: como as peças se conectam, quais dados existem, o que a API expõe e como a configuração funciona. Para rodar o projeto, veja [`desenvolvimento.md`](desenvolvimento.md).

## Visão geral

```
Visitante        --> Frontend (React, site estático) --> API (Django + DRF) --> PostgreSQL
Equipe do ICC    --> Área administrativa (Django Admin, no mesmo backend)   --> PostgreSQL
Uploads do admin --> Cloudinary (imagens)
```

- O **frontend** é uma SPA que busca todo o conteúdo na API. O que é fixo no código é a estrutura, os textos institucionais da Home e os links de redes sociais.
- O **backend** é um único projeto Django (`config`) com um app (`website`). Ele serve a API pública e a área administrativa na mesma aplicação.
- A **área administrativa** é o Django Admin personalizado. Não existe painel próprio no frontend, e a API pública não tem rotas de escrita de conteúdo.
- O **banco** é PostgreSQL. As **imagens** enviadas pelo admin vão para o Cloudinary.

Os motivos dessas escolhas estão em [`decisoes.md`](decisoes.md).

## Estrutura do repositório

```
.
├── docker-compose.yml
├── docs/
├── backend/
│   ├── Dockerfile
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── config/                   # configuração do projeto Django
│   │   ├── settings.py
│   │   ├── navigation.py         # menu lateral do admin
│   │   └── urls.py
│   ├── locale/                   # traduções do admin em português (.po e .mo)
│   ├── admin_static/             # CSS e JavaScript do admin (prévia de Markdown)
│   └── website/                  # app com toda a lógica
│       ├── models.py
│       ├── admin.py
│       ├── serializers.py
│       ├── api_views.py
│       ├── urls.py
│       ├── tests.py
│       ├── templates/            # páginas de erro 400, 403, 404 e 500
│       ├── migrations/
│       └── management/commands/  # setup_dev, seed_mock_data, import_icc_data
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.ts
    └── src/                      # ver frontend/README.md
```

## Backend

### Responsabilidades dos arquivos

| Arquivo | Papel |
|---|---|
| `models.py` | Modelos de dados e regras simples (ex.: só um processo seletivo ativo) |
| `admin.py` | Telas da área administrativa: listas, filtros, ações de arquivar, formulários com blocos aninhados |
| `serializers.py` | Formato JSON de cada recurso. Monta as URLs absolutas das imagens |
| `api_views.py` | Views da API (todas de leitura, mais o health check) |
| `urls.py` | Rotas da API |
| `editors_group.py` | Permissões padrão do grupo Editores |
| `conteudo/` | Registro do conteúdo editável: um módulo por página do site em `conteudo/paginas/`, com os textos (chave, seção, descrição, texto original), e `secoes.py`, com as seções da Home |
| `site_texts.py` | Camada de compatibilidade e sincronização do registro com o banco (`SiteText` e `PaginaDoSite`) |
| `conteudo_padrao.py` | Itens de navegação e benefícios padrão de um banco novo |
| `widgets.py` e `fields.py` | Campo de Markdown com prévia e campo de imagem com limite de tamanho, usados no admin |

### Modelos de dados

| Grupo | Modelos | Observações |
|---|---|---|
| Equipe | `Member`, `MemberTrajectory`, `Position`, `Directorate`, `DirectorateMembership` | Uma pessoa pode estar em mais de uma diretoria, com cargo diferente em cada. `Position.power` define a ordem e a presença na liderança da Home (valores até 2). Membro com `is_active` desmarcado (exibido como "Exibir na equipe") é considerado arquivado |
| Parceiros | `Partner`, `PartnerCategory` | `is_active` esconde o parceiro sem apagá-lo |
| Programas | `Program`, `ProgramComponent`, `ProgramContentBlock` | `Program` representa cada programa do ICC, e seu `slug` é usado na URL `/projetos/<slug>`. `ProgramComponent` guarda os componentes de um programa (título e descrição), exibidos em "Como funciona" na página dele; é sempre ligado a um programa e se edita numa aba dentro do **Programa**, sem cadastro próprio. `ProgramContentBlock` guarda os blocos de texto livres (Markdown, com imagem opcional) que descrevem o programa em detalhe, abaixo do topo da página. No admin, o nome é **Programas** |
| Projetos | `Project`, `ProjectContentBlock`, `ProjectImage`, `ProjectTimelineEvent` | `is_active=False` arquiva. Um projeto sem programa (`program` vazio) aparece em "Outros projetos". Um projeto com `end_date` conta como projeto concluído do parceiro. A equipe é a relação `Project.members` (campo **Equipe**, com busca), e o perfil do membro a lê de volta por `Member.projects` |
| Cases | `ProgramCase`, `ProgramCaseParticipant` | Case resolvido por um grupo de membros dentro de um programa. Os participantes ligam o case a membros, como integrantes ou mentores. Saem por papel e, dentro dele, na ordem `order`, que se muda arrastando a linha no admin |
| Artigos | `Article`, `ArticleAuthor`, `ArticleImage` | O texto é Markdown e as imagens são chamadas por número. `published=False` é rascunho. Os autores são linhas (`ArticleAuthor`: nome, ordem e, quando há, o `member`); `Member.citation_name` ajusta como o membro entra nas citações |
| Processo seletivo | `SelectionProcess`, `SelectionProcessStage`, `SelectionProcessStep`, `SelectionProcessRequirement`, `PreparationMaterial`, `PreparationMaterialItem` | Só um processo fica ativo por vez; ativar um desativa os outros. O admin não deixa abrir inscrições sem o link do formulário, e a API só informa inscrições abertas quando há link |
| Home | `Statistic` | Números da faixa de estatísticas |
| Seções da Home | `SecaoDaHome` | Cada seção depois da Apresentação (aviso, quem somos, estatísticas, missão, programas, equipe, parceiros, chamada final), com `visible`, `order` e, só no aviso, o destino do botão (`button_page` da lista fixa `NavItem.PAGINAS` ou `button_url` livre, validados como no menu). As linhas nascem do registro `website/conteudo/secoes.py` pelo `post_migrate`: num banco novo valem a ordem e a visibilidade do registro (aviso primeiro e escondido); depois só o título acompanha o registro, o que o editor definiu fica, e uma seção nova entra no fim. A API devolve em `home_sections` só as visíveis, na ordem (o aviso só quando tem texto). O Topo e a Apresentação são fixos no frontend. O texto do aviso fica em `SiteText` (`home.aviso_*`) |
| Textos do site | `PaginaDoSite`, `SiteText` | Títulos de seção, rótulos, botões e mensagens curtas. O registro `website/conteudo/` declara as páginas e, em cada uma, os textos (chave, seção, descrição e texto original). Um texto pode ser opcional (`opcional=True`, pode ficar vazio). O sinal `post_migrate` cria as páginas e os textos que faltam, remove os que saíram do registro e nunca altera um valor já editado. O admin abre uma página por vez, com os textos agrupados por seção (os raros ficam recolhidos: o `raro=True` do `Texto` marca os rótulos e mensagens curtas, como "Voltar", "Ler artigo" e o rodapé, e deixa à vista só os títulos e as frases de cada página), marca o que foi editado, mostra o original e restaura. Recusa a remoção de trechos como `{n}`. Para acrescentar um texto: declarar em `conteudo/paginas/<pagina>.py`, usar `t("chave")` no frontend (não há arquivo de reserva para atualizar). Para uma página nova: criar o módulo e incluí-lo em `conteudo/__init__.py`. Um teste confere que toda chave usada no frontend existe no registro |
| Configuração do site | `SiteConfig`, `PartnerBenefit` | Registro único (`pk=1`, criado pela migration), sem adicionar nem excluir no admin. Guarda contatos, a foto de "Quem somos" e a descrição dela, a Política de Privacidade (Markdown, só para administradores) e o slug do programa em destaque na página Projetos. Os textos da Home, do rodapé e da abertura das páginas saíram daqui (migration 0030, reversível) e vivem em `SiteText`, declarados em `website/conteudo/`; a API os entrega só em `texts`, e o frontend os lê por `t("chave")`. `PartnerBenefit` é a lista "Por que ser parceiro". Nome, descrição, logo, ícone e imagem de compartilhamento do site também ficam aqui e entram no HTML durante o build. `NavItem` guarda os itens do menu do topo, do rodapé e o botão de destaque: cada um aponta para uma página de uma lista fixa (`NavItem.PAGINAS`) ou para um link livre validado, e os submenus de Projetos e Equipe continuam vindo dos programas e das diretorias. O admin usa o tema django-unfold, com os campos em abas |

#### Arquivar em vez de apagar

| Entidade | Como esconder do site |
|---|---|
| Membro | Desmarcar `is_active`, exibido como "Exibir na equipe" (ações "Arquivar" e "Reativar" na lista) |
| Projeto | Desmarcar `is_active` (mesmas ações) |
| Parceiro, programa e case | Desmarcar `is_active`, exibido como "Exibir no site" |
| Artigo | Desmarcar `published` |

Os registros arquivados ou ocultos continuam no banco e fora da API pública. A exceção é o perfil de um membro arquivado, que continua acessível por link direto, porque pode ser referenciado pela equipe de um projeto ou por um case antigo.

#### Artigos

- O campo `slug` é opcional. A API aceita o slug ou o id na mesma rota, e o frontend usa o slug quando existe. Slug vazio significa que a URL usa o id.
- As imagens do texto são chamadas por número, como `![](imagem-1)`, e não pelo endereço. Isso permite escrever o texto e enviar as imagens no mesmo formulário, sem salvar antes para descobrir a URL do Cloudinary. O frontend troca o número pelo endereço.
- Fórmulas usam `$$`. Um cifrão sozinho continua sendo texto, para que valores em reais não virem fórmula.
- O texto usa só títulos `##`, `###` e `####`. O título do artigo já está no topo da página, então `#`, `#####` e `######` não são formatados: o `ArtigoMarkdown` os mostra como texto comum, com os símbolos à vista (como já ocorre com sete ou mais `#`).
- **Autores.** `ArticleAuthor` guarda o nome como foi escrito, no formato do BibTeX (`Robert {Lucas Jr}`, com chaves no que não se separa), a ordem e o `member`, que fica nulo para quem não é membro e vira nulo se o membro for apagado (`SET_NULL`). O vínculo só nasce da escolha do membro na lista do campo de nome (`CampoDeAutor` e `autor_combobox.js`, que gravam o ID num campo oculto): não há comparação de nomes. `ArticleAuthor.clean()` normaliza o nome para o `citation_name` ou o `name` do membro escolhido e recusa nome em branco ou chaves desparelhadas. Um artigo publicado precisa de ao menos um autor (`AutoresDoArtigoFormSet`, `FormDaListaDeArtigos` e a ação "Publicar selecionados"); não há artigo institucional. Um registro antigo sem autores sai na API e nas citações com o `Article.NOME_INSTITUCIONAL` (Insper Consulting Club) como autor.
- **API dos autores.** `authors` traz, para cada autor, `name` (sem as chaves), `member_id` e `has_profile` (só membros ativos têm perfil na Equipe). O site filtra a lista por `member_id` e liga o nome ao perfil quando `has_profile` é verdadeiro. `ArticleSerializer` entrega também `images` (número, endereço e legenda) e `citations`.
- **Citações.** `website/citacao.py` gera ABNT, APA, BibTeX, BibLaTeX e RIS a partir do artigo. A data de acesso é a de quem copia, e só o navegador a sabe: o backend entrega marcadores (`__DATA_DE_ACESSO__` e variantes) que `CitarArtigo.tsx` troca pela data de hoje ao mostrar e ao copiar. Os nomes são separados por nome e sobrenome pelas regras do BibTeX, e o que a regra errar se resolve com chaves ou com o `citation_name`. O ABNT e o APA foram conferidos com o BibLaTeX (biblatex-abnt e biblatex-apa, com TeX Live) no desenvolvimento; as diferenças deliberadas estão nos testes (`CitationTests`). O admin mostra a mesma saída, com a data de hoje, na seção recolhida "Como será citado".
- **Formulário do admin.** `ArticleAdmin` usa o template `website/admin/artigo_change_form.html` para pôr a lista de autores logo abaixo de título e slug (o Django põe as tabelas depois de todos os campos). A faixa "Para publicar" (`pendencias`) lista o que falta no artigo salvo. A lista tem os filtros `AutorDoArtigoFilter` e `TemaDoArtigoFilter`, em lista suspensa (`unfold.contrib.filters`, em `INSTALLED_APPS`); o de tema junta grafias que só diferem na caixa ("Varejo" e "varejo"). O campo de temas sugere os já usados (`temas_sugestoes.js`), e `avisa_alteracoes.js`, ligado por `UNFOLD['SCRIPTS']`, avisa de alterações não salvas em qualquer formulário.

### API

Todos os endpoints são públicos e somente leitura. Itens ocultos ou arquivados não aparecem. Base: `https://api.insperconsultingclub.com.br/api/`.

| Método | Rota | Descrição |
|---|---|---|
| GET | `/members/` | Membros atuais (com "Exibir na equipe" marcado), ordenados por diretoria, cargo e nome |
| GET | `/members/<id>/` | Detalhe de um membro, inclusive ex-membro |
| GET | `/directorates/` | Diretorias, com `slug` derivado do nome |
| GET | `/partners/` | Parceiros visíveis. Aceita `?category=<id>` |
| GET | `/partners/<id>/` | Detalhe de um parceiro, com seus projetos concluídos |
| GET | `/programs/` | Programas visíveis |
| GET | `/programs/<slug>/` | Detalhe de um programa visível, com os blocos de conteúdo; oculto responde 404. A lista não leva os blocos, porque alimenta o menu, o rodapé e a Home |
| GET | `/components/` | Componentes dos programas. Aceita `?program=<slug>` |
| GET | `/projects/` | Projetos ativos. Aceita `?program=<slug>` |
| GET | `/projects/<id>/` | Detalhe de um projeto ativo; arquivado responde 404 |
| GET | `/program-cases/` | Cases dos programas visíveis. Aceita `?program=<slug>` |
| GET | `/articles/` | Artigos publicados, do mais recente para o mais antigo |
| GET | `/articles/<slug ou id>/` | Detalhe de um artigo publicado; rascunho responde 404 |
| GET | `/statistics/` | Números da Home |
| GET | `/site-config/` | Contatos, textos e imagens do site (Configuração do site e textos das páginas), com os benefícios para parceiros |
| GET | `/selection-process/` | Processo seletivo ativo, com etapas, requisitos, materiais e estado das inscrições; 404 se não houver |
| GET | `/health/` | `{"status": "ok"}`, sem consultar o banco |

O `/health/` não acessa o banco de propósito: o monitor de uptime o chama a cada 14 minutos, e consultar o banco impediria que o Neon suspendesse quando ocioso.

### Configuração (`config/settings.py`)

- `SECRET_KEY` é obrigatória. O projeto não sobe sem ela. No ambiente local, o `docker-compose.yml` define uma chave de desenvolvimento, então o `.env` é opcional. Como essa chave é pública, o backend se recusa a subir com ela quando `DEBUG=False`.
- Com `DEBUG=False`, o backend exige HTTPS, define cookies seguros e ativa o HSTS.
- **Grupo "Editores":** `website/editors_group.py` define as permissões padrão de quem opera o site no dia a dia sem ser superusuário. Só o crítico fica com os administradores: Usuários e Grupos, o menu do site, a marca e a Política de Privacidade, e apagar cadastros com "esconder" (parceiros, projetos, programas, cases, processos, diretorias, cargos). Um **artigo em rascunho** e um **membro sem vínculos** (trajetória, case, projeto ou artigo) podem ser apagados por quem tem a permissão: a regra está em `ArticleAdmin.has_delete_permission` e `MemberAdmin.has_delete_permission` (`membro_tem_historico`). Cargos são alterados pelo editor, inclusive a prioridade. A Atividade recente (`admin.view_logentry`) também é do grupo. As abas Marca e compartilhamento e Política de Privacidade da configuração são escondidas de quem não é superusuário em `SiteConfigAdmin.get_fieldsets`, o que também tira os campos do formulário. O grupo é criado no `post_migrate`, uma vez; ajustes feitos no admin não são desfeitos. Para voltar ao padrão, apague o grupo no admin: o próximo `migrate` o recria. Um modelo novo precisa ser incluído em `PERMISSOES` para entrar no grupo, e uma lista dentro de um formulário (inline) sem permissão fica invisível para o editor: um teste confere isso. Como o grupo já existe em produção, uma permissão nova chega a ele por uma migration de dados feita uma vez (como a `0028` e a `0035`), que não refaz ajustes feitos depois no admin.
- **Barra e prévia de Markdown no admin:** o widget `website/widgets.py` (template `widgets/markdown_preview.html`) desenha, acima do campo, uma barra com os menus **Seção** (títulos) e **Inserir** (imagem, tabela, fórmula, bloco de código, código na frase e linha divisória), os botões de negrito, itálico, link, listas e citação, e, à direita, **Prévia** e **Tela cheia** (com **Salvar e continuar** na tela cheia). A tela cheia abre com a prévia ao lado do texto. O botão de prévia abre `FRONTEND_URL/previa` num iframe e envia o texto por `postMessage` (script em `backend/admin_static/website/markdown_preview.js`). A página `/previa` do frontend desenha o texto com os mesmos componentes do site (`ArtigoMarkdown` e `TextoMarkdown`) e só aceita mensagens vindas da origem do backend (`VITE_API_URL`), então o admin precisa ser aberto pelo endereço do backend. `STATICFILES_DIRS` aponta para `admin_static/`, que não pode ser a pasta de `STATIC_ROOT`.
- **Formulários do admin:** as listas que se repetem (trajetória, vínculos, imagens, blocos, etapas) são abas no alto do formulário (`tab = True` nos inlines; as que se reordenam arrastando herdam de `AbaOrdenavelTabular` ou `AbaOrdenavelEmpilhada`, em `admin.py`); os campos do registro ficam em seções na própria página. `TextoCompactoMixin` (em `admin.py`) define quantas linhas cada caixa de texto tem (`linhas_dos_campos`), e os relacionamentos com muitos registros usam busca com seleção (`autocomplete_fields`) em vez do seletor duplo. `admin_static/website/admin.css`, ligado por `UNFOLD['STYLES']`, mantém o seletor duplo restante (permissões) e os blocos de campos dentro da largura da tela. Todo modelo precisa de `verbose_name` em português no singular, e um teste confere.
- **Menu e navegação do admin:** o menu lateral vem de `config/navigation.py` (`UNFOLD['SIDEBAR']`), que agrupa os modelos por assunto e esconde o que o usuário não tem permissão de ver. Um modelo novo só aparece no menu depois de ser incluído em `GRUPOS`, e o que só existe como aba dentro de outro cadastro (como os componentes do programa) não entra no menu. Os campos `order` são reordenados arrastando (`ordering_field` e `hide_ordering_field` nos admins e inlines do Unfold), exceto onde a ordem vem de outro campo (data do cronograma, data do artigo). Os botões "Ver no site" usam `view_on_site` em cada admin e `FRONTEND_URL`. A página inicial (`admin.site.index_template`, `website/admin/painel.html`) mostra o nível de acesso e um cartão de atalhos por assunto; os cartões e os links vêm de `ATALHOS` em `config/navigation.py` (ligado por `UNFOLD['DASHBOARD_CALLBACK']`) e cada link só aparece se a pessoa tem a permissão. 
- **Tradução do admin:** a tradução em português do Django traz erros de grafia e de gramática (por exemplo, "ordenção" e "Certifique-se que"), e o tema django-unfold não traz português. A pasta `backend/locale/` tem dois catálogos do projeto, ativados por `LOCALE_PATHS` em `settings.py`, que valem antes dos do Django: `django.po` (grafias, mensagens padrão do Django e textos do Unfold) e `djangojs.po` (frases do seletor de duas listas, que o Django monta com o nome do modelo no meio e erravam o gênero, como "todos permissões"). Testes conferem as correções e os trechos como `%(nome)s`. Ao atualizar o `django-unfold`, textos novos dele aparecem em inglês até serem acrescentados ao catálogo. Os `.mo` compilados são versionados (exceção no `backend/.gitignore`), porque o deploy não compila mensagens. Para corrigir outro texto, acrescente a entrada no `.po` e rode, dentro de `backend/`, `msgfmt --check -o locale/pt_BR/LC_MESSAGES/django.mo locale/pt_BR/LC_MESSAGES/django.po` (para o `djangojs`, troque os nomes). Dois textos não passam por catálogo: o nome das permissões, que o Django grava em inglês no banco e o admin traduz só na exibição (`rotulo_da_permissao`, em `admin.py`), e as páginas de erro 400, 403, 404 e 500, que são templates em `website/templates/`.
- `BEHIND_PROXY=True` faz o Django confiar no cabeçalho `X-Forwarded-Proto`. É necessário no Render, que termina o HTTPS na frente do Django. Sem isso, o site entra em loop de redirecionamento.
- O banco vem de `DATABASE_URL`. Sem ela, usa as variáveis `DB_*` do Compose.
- O armazenamento de uploads é o Cloudinary quando `CLOUDINARY_CLOUD_NAME` está definido, e o disco local caso contrário.
- Os arquivos estáticos do admin são servidos pelo WhiteNoise.
- O idioma é `pt-br` e o fuso é `America/Sao_Paulo`.

### Variáveis de ambiente

Modelo comentado em [`backend/.env.example`](../backend/.env.example). Nunca registre valores reais no repositório.

| Variável | Obrigatória em produção | Descrição |
|---|---|---|
| `SECRET_KEY` | Sim | Chave secreta do Django |
| `DEBUG` | Não (padrão `False`) | `True` apenas localmente |
| `ALLOWED_HOSTS` | Sim | Domínios do backend, sem `https://`. Em produção: `api.insperconsultingclub.com.br` |
| `CORS_ALLOWED_ORIGINS` | Sim | Origens do site, com `https://`. Em produção: `https://insperconsultingclub.com.br` |
| `CSRF_TRUSTED_ORIGINS` | Sim | Domínio do backend com `https://`, necessário para o login do admin. Em produção: `https://api.insperconsultingclub.com.br` |
| `BEHIND_PROXY` | Sim | `True` atrás do proxy do Render |
| `FRONTEND_URL` | Não | Endereço público do site, usado pelos botões "Ver no site", pelo link "Voltar ao site" e pela prévia de Markdown do admin. Sem ela, vale a primeira origem de `CORS_ALLOWED_ORIGINS` e, em desenvolvimento, `http://localhost:5173` |
| `MAX_IMAGE_UPLOAD_MB` | Não | Tamanho máximo, em MB, de cada imagem enviada pelo admin (padrão: `5`), para proteger a cota do Cloudinary |
| `API_CACHE_SECONDS` | Não | Segundos que o navegador reaproveita as respostas de leitura da API (`Cache-Control`). Padrão: `60`. `0` desliga |
| `DATABASE_URL` | Sim | Conexão com o Postgres do Neon |
| `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Sim | Armazenamento de imagens. Sem elas, as imagens enviadas se perdem a cada deploy |

Listas (`ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS`) são separadas por vírgula.

### Docker

O `Dockerfile` do backend já está pronto para produção. Seu comando aplica as migrations, executa o `collectstatic` e inicia o gunicorn (`config.wsgi:application`) na porta definida em `PORT`. O `docker-compose.yml` substitui esse comando pelo servidor de desenvolvimento do Django, com `DEBUG=True` e recarga ao salvar, e roda o `setup_dev` antes dele (administrador local e dados de exemplo, só em `DEBUG=True`).

## Frontend

Resumo; os detalhes (rotas, tokens, componentes e como adicionar uma página) estão em [`frontend/README.md`](../frontend/README.md).

- **Rotas** definidas em `src/main.tsx` com `createBrowserRouter`. Cada página carrega sob demanda, exceto a Home, que é a porta de entrada mais comum.
- **Chamadas à API** concentradas em `src/api.ts`, com os tipos em `src/types.ts`. O endereço vem de `VITE_API_URL`.
- **`VITE_API_URL`** entra no código no momento do build. Mudar o valor exige novo build e novo deploy. O link "Área administrativa" do rodapé é derivado dele, trocando o `/api` final por `/admin/`.
- **Build lê a API.** O plugin `plugins/siteConfig.ts` consulta `/api/site-config/` durante o `vite build` e grava no `index.html` o nome, a descrição, a imagem de compartilhamento (`og:image`), o ícone e o logo (preload), porque quem compartilha o link só lê o HTML estático. Ele também embute uma cópia da configuração em `window.__SITE_CONFIG__` (sem a Política de Privacidade), que `useSiteConfig` usa como estado inicial até a API responder, sem piscar. Se a API não responder, o build falha; se ela responder sem `home_sections` (backend antigo, ainda em publicação, já que o Render sobe os dois serviços juntos), o build espera e consulta de novo a cada 20 segundos, por até 10 minutos. Por isso, mudar um desses campos exige publicar o frontend de novo (Manual Deploy no Render), e o admin lembra disso ao salvar. Ver [`operacao.md`](operacao.md).
- **Textos e contatos:** os contatos, a foto de "Quem somos", o programa em destaque e a Política de Privacidade vêm de `GET /api/site-config/`, pelo hook `useSiteConfig`. Todos os textos das páginas (títulos, rótulos, botões, frases de abertura, Home e rodapé) vêm do campo `texts` da mesma resposta, pelo hook `useTextos`: `t("chave")`. As seções da Home vêm do campo `home_sections` (ordem e visibilidade); a Home desenha cada chave com o seu componente e ignora chaves que não conhece. Para criar uma seção nova: declarar em `conteudo/secoes.py`, acrescentar o caso em `pages/Home/index.tsx` e a chave em `CONHECIDAS`. O frontend não guarda cópia desses valores: enquanto a API não responde, vale a cópia gravada no HTML durante o build (`window.__SITE_CONFIG__`), e o build falha se a API não responder, para o deploy anterior continuar no ar. O servidor de desenvolvimento precisa do backend rodando.
- **Artigos** são exibidos com `react-markdown`, `remark-gfm` e KaTeX. O botão **Compartilhar** (`CompartilharArtigo.tsx`) usa a folha de compartilhamento do sistema (`navigator.share`) em aparelhos de toque e, no computador, um menu com LinkedIn, WhatsApp e Copiar link. O cartão que as redes mostram ao compartilhar continua sendo o do site, porque as metas `og:` vêm do `index.html` estático e não mudam por artigo. A biblioteca não executa HTML, então marcação digitada no admin aparece como texto. O CSS e as fontes do KaTeX só carregam na página de artigo.
- **Aplicação de página única:** o serviço de hospedagem precisa de uma regra que reescreva `/*` para `/index.html`. Sem ela, recarregar uma página interna dá 404.

## Fluxo de dados de ponta a ponta

1. Uma pessoa do ICC cadastra ou edita algo no admin.
2. O Django grava no PostgreSQL. Imagens enviadas vão para o Cloudinary, e o banco guarda o caminho.
3. O frontend chama a API, que lê o banco, aplica os filtros (ativo, publicado, exibido) e devolve JSON com URLs absolutas das imagens.
4. A mudança aparece no site ao recarregar a página. Não há cache entre o banco e a API.
