# Operação

Como o site roda em produção e como mantê-lo no ar. Para a troca de gestão e os acessos, veja [`passagem-de-gestao.md`](passagem-de-gestao.md). Para as variáveis de ambiente, veja [`arquitetura.md`](arquitetura.md#variáveis-de-ambiente).

## Endereços

| | Endereço |
|---|---|
| Site | https://insperconsultingclub.com.br (o endereço com `www` redireciona para ele) |
| Área administrativa | https://api.insperconsultingclub.com.br/admin/ |
| API | https://api.insperconsultingclub.com.br/api/ |
| Health check | https://api.insperconsultingclub.com.br/api/health/ |

## Serviços

Todos ficam sob a conta de infraestrutura do ICC, descrita em [`passagem-de-gestao.md`](passagem-de-gestao.md#conta-de-infraestrutura).

| Serviço | Para quê | Plano |
|---|---|---|
| [Render](https://render.com), serviço `icc-backend` | Backend Django (API e `/admin`), construído a partir do `backend/Dockerfile` | Gratuito |
| [Render](https://render.com), serviço `insperconsultingclub` | Frontend, site estático gerado pelo Vite | Gratuito |
| [Neon](https://neon.tech) | Banco PostgreSQL | Gratuito |
| [Cloudinary](https://cloudinary.com) | Fotos dos membros, logos dos parceiros e demais imagens enviadas pelo admin | Gratuito |
| [UptimeRobot](https://uptimerobot.com) | Chama `/api/health/` a cada 14 minutos e avisa por e-mail se o backend cair | Gratuito |
| [Registro.br](https://registro.br) | Domínio `insperconsultingclub.com.br` e DNS | Pago (anual) |
| GitHub, organização `insper-consulting-club` | Código-fonte (`insper-consulting-club/website`) | Gratuito |

Nenhuma credencial fica no repositório. Senhas, chaves e a `DATABASE_URL` ficam só no painel de cada serviço. Se encontrar uma credencial no código ou num commit, troque-a no serviço imediatamente: apagar o arquivo não basta, porque o histórico do Git guarda tudo.

## Deploy

O deploy é automático. Os dois serviços do Render estão conectados ao repositório com o Auto-Deploy em "On Commit", então cada merge na `main` publica backend e frontend em poucos minutos.

Para acompanhar, abra o serviço no Render e veja a aba **Events**: o deploy aparece com o commit do merge e termina como **Live**. Se falhar, os **Logs** do deploy mostram o erro, e o site continua na versão anterior até um deploy dar certo.

O backend aplica as migrations a cada deploy, porque isso está no `CMD` do Dockerfile. Em produção, o deploy cuida de tudo sozinho.

Para publicar de novo sem um commit novo, por exemplo depois de mudar uma variável de ambiente, use **Manual Deploy > Deploy latest commit** no serviço.

### Configuração do frontend (`insperconsultingclub`)

Para o caso de o serviço precisar ser recriado:

| Campo | Valor |
|---|---|
| Root Directory | `frontend` |
| Build Filters, Included Paths | `frontend/**` |
| Build Command | `npm run build` |
| Publish Directory | `dist` (relativo ao Root Directory) |
| Variável | `VITE_API_URL=https://api.insperconsultingclub.com.br/api` |
| Redirects/Rewrites | `/*` para `/index.html` (Rewrite) |

O `VITE_API_URL` entra no código no momento do build. Se ele mudar, o frontend precisa de um novo deploy. O link "Área administrativa" do rodapé é derivado dele.

### Marca do site e novo deploy do frontend

O frontend é um site estático: o nome, a descrição, a imagem de compartilhamento, o ícone da aba e o logo de **Configuração do site > Marca e compartilhamento** são gravados no `index.html` **durante o build**, lendo a API. Por isso, mudar um desses campos no admin só aparece depois de um novo deploy do frontend. Só administradores (superusuários) veem essa aba, e quem as altera tem acesso ao Render. Depois de salvar, no Render abra o serviço do frontend (`insperconsultingclub`) e use **Manual Deploy**. O admin lembra disso ao salvar.

Textos, contatos, menu e as demais imagens são lidos pela API a cada visita e aparecem em até um minuto, sem deploy.

O build também falha se a resposta da API não trouxer `home_sections`, o que indica um backend ainda sem as seções da Home: **publique o backend antes do frontend**. Se a API estiver fora do ar durante o build, ele **falha** e avisa no log (`[site-config]`): o site não guarda textos próprios, então o deploy anterior continua no ar em vez de publicar um site sem textos. O backend gratuito pode levar cerca de 30 segundos para acordar, e o build espera por isso. Se acontecer, abra a API no navegador para acordá-la e refaça o deploy. Não há mais `SKIP_SITE_CONFIG`; num build local, deixe o backend rodando.

### Configuração do backend (`icc-backend`)

Para o caso de o serviço precisar ser recriado:

| Campo | Valor |
|---|---|
| Ambiente | Docker |
| Branch | `main` |
| Root Directory | vazio |
| Dockerfile Path | `backend/Dockerfile` |
| Docker Build Context Directory | `backend` |
| Build Filters, Included Paths | `backend/**` |
| Auto-Deploy | On Commit |
| Custom Domain | `api.insperconsultingclub.com.br` |

O Render executa o `CMD` do Dockerfile, que aplica as migrations e inicia o gunicorn, então não há Docker Command nem Pre-Deploy Command configurados. As variáveis de ambiente obrigatórias estão em [`arquitetura.md`](arquitetura.md#variáveis-de-ambiente). Valores de produção:

| Variável | Valor |
|---|---|
| `ALLOWED_HOSTS` | `api.insperconsultingclub.com.br` |
| `CORS_ALLOWED_ORIGINS` | `https://insperconsultingclub.com.br` |
| `CSRF_TRUSTED_ORIGINS` | `https://api.insperconsultingclub.com.br` |
| `BEHIND_PROXY` | `True` |

As demais (`SECRET_KEY`, `DATABASE_URL`, `CLOUDINARY_*`) vêm dos painéis do Neon e do Cloudinary e não são registradas aqui.

Se a conexão do Render com o GitHub se perder, ele para de publicar sozinho. Para reconectar: em **Settings > Build & Deploy > Repository**, escolha o repositório pela conta do GitHub com acesso à organização e confira se o Auto-Deploy está em "On Commit".

### Superusuário em produção

Use o **Shell** do serviço `icc-backend` no Render:

```bash
python manage.py createsuperuser
```

## Domínio e DNS

O domínio é registrado no Registro.br, que também hospeda a zona DNS. O site responde em `insperconsultingclub.com.br` e a API em `api.insperconsultingclub.com.br`.

| Onde | Configuração |
|---|---|
| Render, serviço `insperconsultingclub` (frontend) | Custom Domains: `insperconsultingclub.com.br` e `www.insperconsultingclub.com.br`. O endereço com `www` redireciona para o sem `www` |
| Render, serviço `icc-backend` (backend) | Custom Domain: `api.insperconsultingclub.com.br` |
| Registro.br, zona DNS | Registro `CNAME` do nome `api` para `icc-backend-u0ur.onrender.com` (endereço do serviço do backend no Render), e os registros do domínio raiz e do `www` indicados pelo Render para o frontend |

Para alterar ou recriar um domínio:

1. No Render, no serviço correspondente: **Settings > Custom Domains > Add**. O Render mostra o registro DNS a criar e emite o HTTPS automaticamente.
2. No Registro.br, crie esse registro na zona DNS.
3. Aguarde a verificação no Render. A propagação do DNS pode levar de alguns minutos a horas.
4. Se o endereço do site ou da API mudou, atualize `CORS_ALLOWED_ORIGINS`, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` no backend e o `VITE_API_URL` no frontend, e faça um novo deploy dos dois.

O domínio precisa ser renovado todo ano, antes do vencimento que aparece no painel do Registro.br. Se ele expirar, o site e a API continuam hospedados no Render, mas deixam de ser acessíveis pelos endereços do domínio próprio.

O ICC não tem CNPJ, então o titular é uma pessoa física (ver [`passagem-de-gestao.md`](passagem-de-gestao.md#titularidade-do-domínio)).

## Monitoramento

Um monitor HTTP(s) no UptimeRobot chama `https://api.insperconsultingclub.com.br/api/health/` a cada 14 minutos. Isso cumpre dois papéis:

- O Render desliga o backend gratuito após 15 minutos sem acesso, e o primeiro acesso depois disso leva cerca de 30 segundos. O monitor evita que isso aconteça.
- Se o backend parar de responder, o monitor manda um e-mail para o contato de alerta.

Para recriar o monitor, em uma conta nova: **+ New Monitor > HTTP(s)**, a URL acima, intervalo de 14 minutos e o e-mail da conta de infraestrutura como contato de alerta. Qualquer serviço que faça uma requisição periódica serve (o cron-job.org é uma alternativa). Não use o agendamento do GitHub Actions para isso: ele atrasa e é desligado depois de 60 dias sem commits.

Para conferir: o monitor aparece verde no UptimeRobot, e os Logs do backend no Render mostram `GET /api/health/` se repetindo.

O endpoint de health não consulta o banco de propósito, para que o Neon continue suspendendo quando ocioso.

## Limitações do plano gratuito

Nenhuma afeta os dados.

- **Horas do Render:** cada workspace tem 750 horas gratuitas de web service por mês, somando todos os serviços dele. Um backend sempre ligado gasta até 744 horas, então ele precisa ficar em um workspace **sem outro web service gratuito**. O frontend é um site estático e não gasta essas horas. Se as horas acabarem, o backend para até o mês seguinte.
- **Backend dormindo:** sem acessos por 15 minutos, o Render o desliga. Se o monitor parar, o site continua funcionando, só fica lento no primeiro acesso.
- **Banco:** o Neon suspende o banco quando ocioso e o acorda sozinho no primeiro acesso, em menos de um segundo.
- **Imagens:** o plano gratuito do Cloudinary tem limite mensal de uso, que é bastante para fotos e logos. O consumo aparece no painel do Cloudinary.

## Rotina de manutenção

| Quando | O quê |
|---|---|
| Todo mês | Olhar o UptimeRobot (algum alerta?) e o uso dos planos gratuitos no Render, no Neon e no Cloudinary |
| A cada semestre | Fazer um backup do banco (abaixo) |
| A cada semestre | Atualizar dependências com correções de segurança ([`desenvolvimento.md`](desenvolvimento.md#atualizar-dependências)) |
| Todo ano | Renovar o domínio no Registro.br antes do vencimento |
| Na troca de gestão | Seguir [`passagem-de-gestao.md`](passagem-de-gestao.md) |

A atualização do conteúdo do site (membros, processo seletivo, artigos) é feita pelo ICC e está no [guia da área administrativa](guia-admin.md#rotina-de-cada-semestre).

## Backup do banco

O Neon guarda um histórico curto para restauração no plano gratuito, mas isso não substitui um backup. Para exportar o banco inteiro, com o Docker em execução:

```bash
docker run --rm postgres:18 pg_dump "COLE_AQUI_A_DATABASE_URL" > backup-icc-AAAA-MM-DD.sql
```

- A `DATABASE_URL` está em *Environment* do serviço `icc-backend` no Render, ou no painel do Neon (*Connection string*). O Postgres do Neon está na versão 18, e o `pg_dump` precisa ser da mesma versão ou mais nova. Se o projeto do Neon for recriado em outra versão, ajuste o `postgres:18`. Para ver a versão: painel *Overview* do projeto, ou `SELECT version();` no SQL Editor.
- O arquivo contém dados pessoais dos membros. Guarde-o em um lugar restrito do ICC e **nunca** o inclua em um commit.
- As imagens não entram nesse backup. Elas ficam no Cloudinary, que tem a própria exportação.

## Resolução de problemas

O primeiro lugar para investigar qualquer erro em produção são os **Logs** do serviço `icc-backend` no Render.

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Mudança com merge não aparece no site | O deploy falhou ou o Render perdeu a conexão com o GitHub | Ver **Events** e os Logs do deploy. Se nenhum deploy começou, reconectar o repositório |
| Deploy do frontend falha com "Publish directory ... does not exist" | Build Command vazio ou Publish Directory errado | Build Command `npm run build` e Publish Directory `dist` |
| Site ou admin demoram cerca de 30 s para abrir | O backend dormiu | Conferir o UptimeRobot e as horas do workspace no Render |
| O site abre, mas sem membros, parceiros etc. | Backend fora do ar ou bloqueado por CORS | Abrir `/api/health/`. Se responder, conferir `CORS_ALLOWED_ORIGINS` no Render |
| Erro 403 ou CSRF ao entrar no `/admin` | Domínio do backend fora de `CSRF_TRUSTED_ORIGINS` | Corrigir a variável e fazer novo deploy |
| Recarregar `/equipe` (ou outra página) dá 404 | Falta a regra de rewrite no frontend | No `insperconsultingclub`, em *Redirects/Rewrites*: `/*` para `/index.html` (Rewrite) |
| Imagens somem depois de um deploy | Variáveis `CLOUDINARY_*` ausentes ou erradas | Conferir no Render e reenviar as imagens |
| Logo pequeno no carrossel | Imagem com muita margem em volta | Reenviar o PNG recortado rente ao logo ([guia do admin](guia-admin.md#parceiros)) |
| Backend parou no fim do mês | Acabaram as 750 horas do workspace | Tirar outros web services gratuitos do workspace ou mudar de plano |
| Site e API fora do ar de uma vez, certificado inválido | Domínio expirado ou registro DNS alterado | Conferir o Registro.br e os Custom Domains no Render |
| Redirecionamento em loop ao abrir o admin | `BEHIND_PROXY` não está `True` | Corrigir a variável e fazer novo deploy |
