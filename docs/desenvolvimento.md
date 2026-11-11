# Desenvolvimento

Como rodar o projeto na sua máquina e como propor mudanças no código. Para entender como o sistema é organizado, veja [`arquitetura.md`](arquitetura.md). Para publicar e operar o site, veja [`operacao.md`](operacao.md).

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) com o Compose, em execução.
- Git.
- Node.js 20.19 ou mais novo (ou 22.12 ou mais novo), apenas se for rodar lint e build do frontend fora do Docker. É o que o Vite 8 exige.

Todos os comandos `docker compose` devem ser executados na raiz do repositório.

## Subir o ambiente

### 1. Clonar o repositório

```bash
git clone https://github.com/insper-consulting-club/website.git
cd website
```

### 2. Subir os containers

```bash
docker compose up --build
```

Não é preciso criar o `backend/.env`: o `docker-compose.yml` define uma `SECRET_KEY` só para desenvolvimento. Crie o arquivo apenas para variáveis opcionais, como as credenciais de um Cloudinary de testes. A lista completa está em [`backend/.env.example`](../backend/.env.example) e na seção de variáveis de [`arquitetura.md`](arquitetura.md#variáveis-de-ambiente).

Sobem três serviços:

| Serviço | O que é | Porta |
|---|---|---|
| `db` | PostgreSQL 18, acessível só pela própria máquina (`127.0.0.1`) | 5432 |
| `backend` | Django com o servidor de desenvolvimento, que recarrega ao salvar. Aplica as migrations e, se o banco estiver vazio, carrega os dados de exemplo e cria o administrador local | 8000 |
| `frontend` | Vite em modo de desenvolvimento | 5173 |

| Endereço | URL local |
|---|---|
| Site | http://localhost:5173 |
| API | http://localhost:8000/api/ |
| Área administrativa | http://localhost:8000/admin/ (usuário `admin`, senha `admin`) |

As portas 8000 e 5173 só aceitam conexões da própria máquina, por causa da senha simples do administrador local.

### 3. Dados de exemplo e administrador

O `backend` roda o comando `setup_dev` a cada subida, e ele só age em `DEBUG=True`. Se não houver usuários, cria o superusuário `admin`. Se o banco não tiver membros, roda o `seed_mock_data`. Para repetir manualmente:

```bash
docker compose exec backend python manage.py seed_mock_data
```

**O que o `seed_mock_data` cria.** Um conjunto único e completo de dados **fictícios** (exceto os nomes e as descrições dos quatro programas do ICC, que são os reais): 16 membros, 8 parceiros, os programas com blocos de conteúdo, componentes e cases, 7 projetos, 8 artigos (um deles, "Guia de formatação", usa todos os recursos do editor, para testar o site), dois processos seletivos (um antigo e o ativo, com inscrições abertas), a trajetória e os vínculos de diretoria dos membros e dois itens de menu a mais. Pessoas, e-mails e links são inventados e usam `example.com`.

Ele inclui de propósito os casos de borda que o admin e o site tratam, para testar a apresentação: nome e título muito longos, membro sem foto e sem LinkedIn, ex-membros (que somem da Equipe), parceiro sem logo e sem site, programa sem link de inscrição, projeto de um dia só, projeto sem parceiros nem programa, artigo sem slug, artigo só com link externo, rascunho, e itens ocultos ou arquivados (parceiro, programa, case e projeto), que aparecem no admin mas não no site. Fotos, logos, capas e galerias recebem imagens de exemplo geradas na hora; algumas entidades ficam sem imagem de propósito.

**Repetir é seguro.** Por padrão, rodar de novo atualiza os registros de exemplo sem duplicá-los (e remove itens de lista que o seed não descreve mais), mas desfaz edições feitas nesses registros. As imagens são regravadas com o mesmo nome, então não se acumulam. A configuração do site (textos, contatos, menu padrão) não é alterada.

**Começar do zero.** Para recomeçar com um banco limpo (por exemplo, para tirar duplicados de um seed antigo), use o caminho do [guia do ambiente local](guia-ambiente-local.md): `docker compose down -v` e depois `docker compose up --build`. Os dados de exemplo voltam sozinhos.

**Segurança.** O seed só roda com `DEBUG=True`. Com o Cloudinary configurado (armazenamento remoto), ele não envia imagens de exemplo, para não encher o ambiente compartilhado: o resto dos dados é criado normalmente. Nunca rode em produção.

Para criar outro administrador:

```bash
docker compose exec backend python manage.py createsuperuser
```

Quem não é técnico e precisa rodar o site local para testar uma mudança deve seguir o [guia do ambiente local](guia-ambiente-local.md).

## Imagens no ambiente local

Sem as variáveis `CLOUDINARY_*`, os uploads vão para a pasta `backend/images/` da sua máquina (o código é montado no container) e não são compartilhados. Isso é suficiente para desenvolver. Se você preencher as credenciais do Cloudinary no `.env`, os uploads passam a ir para a conta configurada, então use uma conta de testes, nunca a de produção.

## Dados reais do ICC

A pasta `site-data/`, na raiz do repositório, guarda os dados reais usados em cargas iniciais. Ela não é versionada porque contém dados pessoais dos membros. Peça-a ao Diretor Tech. Estrutura esperada:

```
site-data/
├── icc.json      # dados institucionais
├── members/      # fotos, nomeadas com o id da pessoa no icc.json
└── partners/     # logos, nomeados como o parceiro (ex.: bain.png)
```

```bash
docker compose exec backend python manage.py import_icc_data
```

O comando pode ser repetido: atualiza registros em vez de duplicar, e identifica membros pelo LinkedIn. Quem sai de todas as diretorias no `icc.json` é arquivado (desmarcado em "Exibir na equipe") e deixa de aparecer na Equipe. Fotos já cadastradas só são substituídas com `--atualizar-fotos`.

Depois que o site está no ar, a fonte oficial dos dados é a área administrativa de produção. Rodar este comando contra o banco de produção sobrescreve edições feitas lá, então evite.

> Nunca coloque a `DATABASE_URL` de produção no `backend/.env`. Com ela, o ambiente local inteiro passa a ler e gravar no banco do site no ar.

## Comandos úteis

```bash
# Parar os containers
docker compose down

# Logs do backend
docker compose logs -f backend

# Qualquer comando do Django
docker compose exec backend python manage.py <comando>

# Aplicar migrations com os containers já rodando
docker compose exec backend python manage.py migrate

# Recriar o node_modules do container (depois de mudar o package.json)
docker compose up --build -V frontend
```

## Rodar só o frontend contra uma API existente

```bash
cd frontend
npm install
VITE_API_URL=https://api.insperconsultingclub.com.br/api npm run dev
```

O servidor abre em http://localhost:5173. Como a API de produção só libera o domínio do site no CORS, esse atalho só funciona se o backend aceitar a origem `http://localhost:5173`. Para trabalhar com liberdade, use o ambiente completo do Docker.

## Fluxo de mudanças

1. Crie uma branch a partir da `main` atualizada, com um assunto por branch. Nomes usados no projeto: `feat/...`, `fix/...`, `docs/...`.
2. Desenvolva e teste localmente.
3. Antes de abrir o PR, rode as verificações abaixo.
4. Se alterou `models.py`, gere a migration e inclua-a no commit.
5. Abra o PR e peça revisão.
6. Após o merge na `main`, o Render publica backend e frontend sozinho. Acompanhe e confira o site (ver [`operacao.md`](operacao.md#deploy)).

### Verificações antes do PR

```bash
# Backend
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py test

# Frontend
cd frontend
npm run lint
npm run build
```

`npm run build` roda o `tsc` e depois o Vite, então falhas de tipo aparecem aqui. Os dois comandos do frontend precisam passar.

### Migrations

As migrations ficam versionadas em `backend/website/migrations/`. O Docker Compose as aplica ao subir o backend, e em produção o `Dockerfile` as aplica a cada deploy.

- Rode `makemigrations` somente depois de alterar `models.py`, e faça commit do arquivo gerado.
- Se você puxar uma migration nova com os containers já rodando, aplique-a na mão com `migrate`. Sem isso aparecem erros como `column ... does not exist`.
- Nunca edite uma migration que já foi para a `main`. Crie outra.
- Se duas branches criarem migrations com o mesmo número, o Django detecta conflito no `migrate`. Resolva com `makemigrations --merge`.

### Testes

Os testes do backend ficam em `backend/website/tests.py` e usam o `django.test.TestCase` com o `APIClient` do DRF. Hoje cobrem os endpoints públicos: artigos (slug, id e rascunhos), membros atuais e arquivados, parceiros ocultos, projetos arquivados, programas, componentes e cases, processo seletivo e o `/api/health/`. Os artigos têm testes do formulário do admin (autores, faixa "Para publicar", prévia da citação, barra do Markdown e filtros), da migration dos autores e das citações (`CitationTests`). Ao criar ou alterar um endpoint, acrescente testes. O frontend ainda não tem testes automatizados.

### Estilo de código

- O código e os comentários do projeto estão em português, e os nomes de campos e models, em inglês. Siga o padrão do arquivo em que estiver mexendo.
- No frontend, use as variáveis CSS de [`index.css`](../frontend/src/index.css) em vez de valores soltos. Detalhes em [`frontend/README.md`](../frontend/README.md).
- O ESLint é a referência de formatação do frontend.

## Atualizar dependências

Faça em uma branch própria.

- **Backend:** `docker compose exec backend pip list --outdated`. Atualize as versões em `backend/requirements.txt`, rode `docker compose up --build` e teste o site e a área administrativa. Priorize as versões de correção do Django (por exemplo, `6.0.x`).
- **Frontend:** `cd frontend && npm outdated`, depois `npm update` dentro da mesma versão principal, seguido de `npm run lint && npm run build`.
- Ao adicionar ou trocar um pacote, atualize [`dependencias.md`](dependencias.md) com a versão e a licença.

## Problemas comuns no ambiente local

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| O `db` fica `unhealthy` e a imagem reclama de dados em `/var/lib/postgresql/data` | Volume criado com o Postgres 16, de antes da troca para o 18 | `docker compose down -v` e `docker compose up --build` (apaga só os dados locais) |
| `column ... does not exist` | Migration nova não aplicada | `docker compose exec backend python manage.py migrate` |
| `Failed to resolve import "..."` no frontend | Pacote novo no `package.json`; o container guarda o `node_modules` antigo | `docker compose up --build -V frontend` |
| `RuntimeError: SECRET_KEY não definida` | O backend foi iniciado fora do Compose | Subir com `docker compose up`, que define a chave de desenvolvimento |
| O site abre, mas sem dados | Os dados de exemplo não carregaram | Rodar `seed_mock_data` (passo 3) |
| Erro de CORS no navegador | Origem do frontend fora de `CORS_ALLOWED_ORIGINS` | Localmente, o padrão já libera `localhost:5173` e `localhost:3000` |
| Porta 5432, 8000 ou 5173 ocupada | Outro processo usando a porta | Parar o processo ou mudar a porta no `docker-compose.yml` |
