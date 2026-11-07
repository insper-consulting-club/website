# Dependências e licenças

Bibliotecas usadas pelo projeto, com a versão e a licença declaradas por cada pacote. As versões do backend vêm de `backend/requirements.txt` (todas fixadas) e as do frontend vêm do `frontend/package-lock.json`. As licenças do backend foram conferidas em 26/10/2026 nos pacotes instalados, e as do frontend foram lidas do `package-lock.json`.

Todas as licenças são permissivas (MIT, BSD, Apache, PSF) ou LGPL. A LGPL permite usar a biblioteca, sem modificá-la, dentro de um projeto com outra licença, que é o caso do ICC. Ao adicionar uma dependência, confira a licença e inclua uma linha aqui. Para atualizar versões, veja [`desenvolvimento.md`](desenvolvimento.md#atualizar-dependências).

## Backend (Python)

| Pacote | Versão | Licença | Para quê |
|---|---|---|---|
| Django | 6.0.8 | BSD-3-Clause | Framework web, ORM e área administrativa |
| djangorestframework | 3.17.2 | BSD-3-Clause | API REST |
| django-cors-headers | 4.7.0 | MIT | Liberar a API só para o domínio do site |
| psycopg2-binary | 2.9.10 | LGPL (com exceções) | Driver do PostgreSQL |
| dj-database-url | 3.1.2 | BSD-3-Clause | Ler a conexão do banco de `DATABASE_URL` |
| gunicorn | 26.2.0 | MIT | Servidor de produção |
| whitenoise | 6.12.0 | MIT | Servir os arquivos estáticos do `/admin` |
| cloudinary | 1.42.1 | MIT | Cliente do Cloudinary |
| django-cloudinary-storage | 0.3.0 | MIT | Salvar os uploads do Django no Cloudinary |
| requests | 2.33.0 | Apache-2.0 | Requisições HTTP. Fixado aqui porque o django-cloudinary-storage depende dele |
| pillow | 12.3.0 | MIT-CMU | Validar e processar imagens |
| python-dotenv | 1.2.2 | BSD-3-Clause | Carregar o `.env` em desenvolvimento |
| asgiref | 3.11.1 | BSD-3-Clause | Dependência do Django |
| sqlparse | 0.6.0 | BSD | Dependência do Django |

## Frontend (JavaScript e TypeScript)

| Pacote | Versão | Licença | Para quê |
|---|---|---|---|
| react | 19.2.5 | MIT | Interface |
| react-dom | 19.2.5 | MIT | Renderização no navegador |
| react-router-dom | 7.14.2 | MIT | Rotas e navegação |
| react-markdown | 10.1.0 | MIT | Exibir o texto dos artigos, escrito em Markdown, sem executar HTML |
| remark-gfm | 4.0.1 | MIT | Tabelas, listas de tarefas e links automáticos no Markdown dos artigos |
| remark-math | 6.0.0 | MIT | Reconhecer fórmulas (`$$...$$`) no Markdown dos artigos |
| rehype-katex | 7.0.1 | MIT | Desenhar essas fórmulas com o KaTeX |
| katex | 0.16.47 | MIT | Biblioteca que desenha fórmulas em LaTeX (inclui o CSS e as fontes delas) |
| vite | 8.0.10 | MIT | Servidor de desenvolvimento e build (dev) |
| @vitejs/plugin-react | 6.0.1 | MIT | Suporte a React no Vite (dev) |
| typescript | 5.9.3 | Apache-2.0 | Tipagem (dev) |
| eslint, @eslint/js | 9.39.4 | MIT | Lint (dev) |
| typescript-eslint | 8.59.1 | MIT | Regras de lint para TypeScript (dev) |
| eslint-plugin-react-hooks | 7.1.1 | MIT | Regras de lint para hooks (dev) |
| eslint-plugin-react-refresh | 0.5.2 | MIT | Regra de lint para recarregamento (dev) |
| globals | 17.6.0 | MIT | Variáveis globais para o lint (dev) |
| @types/node, @types/react, @types/react-dom | 24.12.2, 19.2.14, 19.2.3 | MIT | Tipos (dev) |

As dependências marcadas com "(dev)" só servem para desenvolver e gerar o site. Elas ficam fora do navegador do visitante.

## Imagens Docker

| Imagem | Onde | Observação |
|---|---|---|
| `python:3.12-slim` | `backend/Dockerfile` | Base do backend, em desenvolvimento e em produção |
| `node:20-slim` | `frontend/Dockerfile` | Base do frontend em desenvolvimento |
| `postgres:18` | `docker-compose.yml` | Banco local, na mesma versão do Neon (licença PostgreSQL) |

## Outros recursos

| Recurso | Licença | Onde |
|---|---|---|
| Fonte Poppins (Google Fonts) | SIL Open Font License 1.1 | Tipografia do site |
| Ícones SVG de interface e das redes sociais (GitHub, Instagram e LinkedIn) | Incluídos no próprio código. O desenho do GitHub é do Simple Icons (CC0 1.0), e os demais são desenhos do projeto. Os nomes e logotipos Instagram, LinkedIn e GitHub são marcas das respectivas empresas | `frontend/src/components/Icons.tsx` |
| Logos dos parceiros e do ICC | Pertencem às respectivas empresas e ao ICC | Fornecidos pelo ICC |

## Serviços externos

| Serviço | Uso | Plano |
|---|---|---|
| Render | Hospedagem do backend e do frontend | Gratuito |
| Neon | Banco PostgreSQL | Gratuito |
| Cloudinary | Armazenamento de imagens | Gratuito |
| UptimeRobot | Monitor de uptime (mantém o backend acordado e avisa se cair) | Gratuito |
| GitHub | Código-fonte | Gratuito |
| Registro.br | Domínio `insperconsultingclub.com.br` | Pago (anual) |

Detalhes de acesso, deploy e domínio estão em [`operacao.md`](operacao.md).
