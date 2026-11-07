# Site do Insper Consulting Club

Site oficial do Insper Consulting Club (ICC), desenvolvido em parceria com o Insper Code Jr. Apresenta o clube a alunos e empresas: equipe, programas e cases, projetos, parceiros, artigos e processo seletivo. Todo o conteúdo é mantido pelo próprio ICC em uma área administrativa, sem alterar o código.

| | Endereço |
|---|---|
| Site | https://insperconsultingclub.com.br (o endereço com `www` redireciona para ele) |
| Área administrativa | https://api.insperconsultingclub.com.br/admin/ |
| API | https://api.insperconsultingclub.com.br/api/ |

## Stack

| Parte | Tecnologias |
|---|---|
| Frontend | React 19, TypeScript, Vite, React Router, CSS próprio com design tokens |
| Backend | Python, Django, Django REST Framework, Django Admin, gunicorn, WhiteNoise |
| Banco | PostgreSQL (Neon em produção, container Docker localmente) |
| Imagens | Cloudinary |
| Hospedagem | Render, com deploy automático a cada merge na `main` |
| Monitoramento | UptimeRobot, consultando `/api/health/` |
| Ambiente local | Docker Compose |

As versões exatas estão em [`backend/requirements.txt`](backend/requirements.txt) e [`frontend/package.json`](frontend/package.json).

## Estrutura do repositório

```
.
├── backend/            # Django, API REST e área administrativa
├── frontend/           # React + TypeScript + Vite
├── docs/               # Documentação
└── docker-compose.yml
```

## Início rápido

Com o Docker em execução, na raiz do repositório:

```bash
docker compose up --build
```

O banco sobe com dados de exemplo e um administrador local (usuário `admin`, senha `admin`).

| Serviço | URL local |
|---|---|
| Site | http://localhost:5173 |
| API | http://localhost:8000/api/ |
| Área administrativa | http://localhost:8000/admin/ |

O passo a passo completo está em [`docs/desenvolvimento.md`](docs/desenvolvimento.md). Para quem não é técnico, há o [guia do ambiente local](docs/guia-ambiente-local.md).

## Documentação

| Documento | Para quem | Conteúdo |
|---|---|---|
| [Guia da área administrativa](docs/guia-admin.md) | Membros do ICC | Como cadastrar e atualizar o conteúdo do site e o que fazer a cada semestre |
| [Guia de artigos](docs/guia-artigos.md) | Membros do ICC | Como escrever, converter (inclusive com IA) e publicar artigos, com Markdown, imagens e fórmulas |
| [Guia do ambiente local](docs/guia-ambiente-local.md) | Membros do ICC | Como rodar uma cópia do site no computador, com Docker Desktop, para testar qualquer mudança (conteúdo, artigos ou visual) antes de ir ao ar |
| [Desenvolvimento](docs/desenvolvimento.md) | Desenvolvedores | Ambiente local, comandos, fluxo de mudanças, migrations e testes |
| [Arquitetura](docs/arquitetura.md) | Desenvolvedores | Backend, frontend, modelos de dados, API e variáveis de ambiente |
| [Operação](docs/operacao.md) | Diretor Tech | Produção, deploy, domínio, backup, monitoramento e resolução de problemas |
| [Passagem de gestão](docs/passagem-de-gestao.md) | Diretor Tech | Acessos, troca de credenciais e checklist de transição |
| [Decisões técnicas](docs/decisoes.md) | Desenvolvedores | Por que o projeto é como é |
| [Dependências e licenças](docs/dependencias.md) | Desenvolvedores | Bibliotecas, serviços externos e licenças |
| [Frontend](frontend/README.md) | Desenvolvedores | Estrutura, rotas, design tokens e componentes |
| [`backend/.env.example`](backend/.env.example) | Desenvolvedores | Variáveis de ambiente do backend, explicadas |
