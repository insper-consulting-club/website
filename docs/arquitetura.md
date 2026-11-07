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
│   │   └── urls.py
│   └── website/                  # app com toda a lógica
│       ├── models.py
│       ├── admin.py
│       ├── serializers.py
│       ├── api_views.py
│       ├── urls.py
│       ├── tests.py
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

### Modelos de dados

| Grupo | Modelos | Observações |
|---|---|---|
| Equipe | `Member`, `Position`, `Directorate`, `DirectorateMembership` | Uma pessoa pode estar em mais de uma diretoria, com cargo diferente em cada. `Position.power` define a ordem e a presença na liderança da Home (valores até 2). Membro com `exit_date` é considerado arquivado |
| Parceiros | `Partner`, `PartnerCategory` | `is_active` esconde o parceiro sem apagá-lo |
| Programas | `Program`, `ProgramComponent` | `Program` representa cada programa do ICC, e seu `slug` é usado na URL `/projetos/<slug>`. `ProgramComponent` guarda os componentes de um programa (título e descrição), exibidos em "Como funciona" na página dele. No admin, os nomes são **Programas** e **Componentes dos programas** |
| Projetos | `Project`, `ProjectContentBlock`, `ProjectImage`, `ProjectTimelineEvent` | `is_active=False` arquiva. Um projeto sem programa (`program` vazio) aparece em "Outros projetos". Um projeto com `end_date` conta como projeto concluído do parceiro |
| Cases | `ProgramCase`, `ProgramCaseParticipant` | Case resolvido por um grupo de membros dentro de um programa. Os participantes ligam o case a membros, como integrantes ou mentores |
| Artigos | `Article`, `ArticleImage` | O texto é Markdown e as imagens são chamadas por número. `published=False` é rascunho |
| Processo seletivo | `SelectionProcess`, `SelectionProcessStage`, `SelectionProcessStep`, `SelectionProcessRequirement`, `PreparationMaterial`, `PreparationMaterialItem` | Só um processo fica ativo por vez; ativar um desativa os outros. O admin não deixa abrir inscrições sem o link do formulário, e a API só informa inscrições abertas quando há link |
| Home | `Statistic` | Números da faixa de estatísticas |

#### Arquivar em vez de apagar

| Entidade | Como esconder do site |
|---|---|
| Membro | Preencher `exit_date` (ações "Arquivar" e "Reativar" na lista) |
| Projeto | Desmarcar `is_active` (mesmas ações) |
| Parceiro, programa e case | Desmarcar `is_active`, exibido como "Exibir no site" |
| Artigo | Desmarcar `published` |

Os registros arquivados ou ocultos continuam no banco e fora da API pública. A exceção é o perfil de um membro arquivado, que continua acessível por link direto, porque pode ser referenciado pela equipe de um projeto ou por um case antigo.

#### Artigos

- O campo `slug` é opcional. A API aceita o slug ou o id na mesma rota, e o frontend usa o slug quando existe. Slug vazio significa que a URL usa o id.
- As imagens do texto são chamadas por número, como `![](imagem-1)`, e não pelo endereço. Isso permite escrever o texto e enviar as imagens no mesmo formulário, sem salvar antes para descobrir a URL do Cloudinary. O frontend troca o número pelo endereço.
- Fórmulas usam `$$`. Um cifrão sozinho continua sendo texto, para que valores em reais não virem fórmula.

### API

Todos os endpoints são públicos e somente leitura. Itens ocultos ou arquivados não aparecem. Base: `https://api.insperconsultingclub.com.br/api/`.

| Método | Rota | Descrição |
|---|---|---|
| GET | `/members/` | Membros atuais (sem data de saída), ordenados por diretoria, cargo e nome |
| GET | `/members/<id>/` | Detalhe de um membro, inclusive ex-membro |
| GET | `/directorates/` | Diretorias, com `slug` derivado do nome |
| GET | `/partners/` | Parceiros visíveis. Aceita `?category=<id>` |
| GET | `/partners/<id>/` | Detalhe de um parceiro, com seus projetos concluídos |
| GET | `/programs/` | Programas visíveis |
| GET | `/components/` | Componentes dos programas. Aceita `?program=<slug>` |
| GET | `/projects/` | Projetos ativos. Aceita `?program=<slug>` |
| GET | `/projects/<id>/` | Detalhe de um projeto ativo; arquivado responde 404 |
| GET | `/program-cases/` | Cases dos programas visíveis. Aceita `?program=<slug>` |
| GET | `/articles/` | Artigos publicados, do mais recente para o mais antigo |
| GET | `/articles/<slug ou id>/` | Detalhe de um artigo publicado; rascunho responde 404 |
| GET | `/statistics/` | Números da Home |
| GET | `/selection-process/` | Processo seletivo ativo, com etapas, requisitos, materiais e estado das inscrições; 404 se não houver |
| GET | `/health/` | `{"status": "ok"}`, sem consultar o banco |

O `/health/` não acessa o banco de propósito: o monitor de uptime o chama a cada 14 minutos, e consultar o banco impediria que o Neon suspendesse quando ocioso.

### Configuração (`config/settings.py`)

- `SECRET_KEY` é obrigatória. O projeto não sobe sem ela. No ambiente local, o `docker-compose.yml` define uma chave de desenvolvimento, então o `.env` é opcional. Como essa chave é pública, o backend se recusa a subir com ela quando `DEBUG=False`.
- Com `DEBUG=False`, o backend exige HTTPS, define cookies seguros e ativa o HSTS.
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
- **Links de redes sociais e e-mail** ficam em `src/redes.ts`, num lugar só, e aparecem no header, no rodapé, no Contato e no Processo Seletivo.
- **Artigos** são exibidos com `react-markdown`, `remark-gfm` e KaTeX. A biblioteca não executa HTML, então marcação digitada no admin aparece como texto. O CSS e as fontes do KaTeX só carregam na página de artigo.
- **Aplicação de página única:** o serviço de hospedagem precisa de uma regra que reescreva `/*` para `/index.html`. Sem ela, recarregar uma página interna dá 404.

## Fluxo de dados de ponta a ponta

1. Uma pessoa do ICC cadastra ou edita algo no admin.
2. O Django grava no PostgreSQL. Imagens enviadas vão para o Cloudinary, e o banco guarda o caminho.
3. O frontend chama a API, que lê o banco, aplica os filtros (ativo, publicado, sem data de saída) e devolve JSON com URLs absolutas das imagens.
4. A mudança aparece no site ao recarregar a página. Não há cache entre o banco e a API.
