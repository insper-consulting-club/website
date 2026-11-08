# Decisões técnicas

Registro das escolhas que explicam como o site é hoje e do porquê de cada uma. Serve para quem for manter o projeto entender o que mudar com segurança e o que evitar. A descrição do sistema está em [`arquitetura.md`](arquitetura.md).

## 1. Aproveitar a base existente em vez de reescrever

O primeiro site do ICC nunca foi ao ar: o banco era um arquivo SQL na máquina de um desenvolvedor, então a entidade não tinha acesso aos dados nem como atualizá-los. Os problemas estavam em pontos específicos, não na base inteira, e por isso o projeto foi refatorado:

| Problema | Solução |
|---|---|
| Banco local, inacessível ao ICC | Conexão lida de `DATABASE_URL`, com PostgreSQL na nuvem (Neon) |
| Imagens salvas no disco do servidor | Upload para o Cloudinary, que sobrevive a novos deploys |
| Interface que não representava o ICC | Frontend reconstruído página a página, com design tokens de cores, tipografia e logo |

A estrutura de dados, a API em Django REST Framework e o React com Vite estavam adequados. Reescrever tudo gastaria o tempo refazendo o que já funcionava.

## 2. Django Admin como área administrativa

O ICC precisa de uma área autenticada para cadastrar e editar o conteúdo. Em vez de construir um painel próprio, o projeto usa o **Django Admin**, personalizado:

- **Segurança pronta:** login, sessões, proteção CSRF, senhas com hash e permissões por usuário. Um painel próprio exigiria criar autenticação de API, permissões e validações, aumentando a superfície de ataque.
- **CRUD completo, inclusive dos dados relacionados** (diretorias de um membro, participantes de um case, datas de um processo seletivo), sem escrever telas.
- **Conteúdo novo sem código:** um campo ou model novo aparece no admin com poucas linhas.
- **Adaptado ao ICC:** tudo em português, miniaturas de fotos e logos, busca e filtros, "Exibir no site" para esconder sem apagar e ações de arquivar e reativar.

Um painel próprio no frontend continua possível no futuro e exigiria APIs de escrita com autenticação.

## 3. Arquivar em vez de excluir

Membros que saem do clube são **arquivados** (recebem data de saída): somem do site, mas o histórico de cases e a trajetória continuam guardados. Projetos seguem a mesma ideia com o campo "Ativo". Parceiros, programas e cases têm "Exibir no site", e artigos têm "Publicado" (rascunho).

A **exclusão** continua disponível para cadastros feitos por engano. Um projeto arquivado some da API pública, e a página dele responde 404.

## 4. Hospedagem

| Serviço | Por quê |
|---|---|
| **Render** (backend e frontend) | Roda o backend direto do `Dockerfile` do repositório e publica o frontend como site estático, com HTTPS e deploy automático a cada merge na `main`, no plano gratuito |
| **Neon** (PostgreSQL) | Banco gerenciado e gratuito que sobrevive à falta de uso. O Postgres gratuito do próprio Render tem prazo de validade |
| **Cloudinary** (imagens) | O disco dos serviços do Render é apagado a cada deploy. Sem armazenamento externo, as fotos enviadas pelo admin se perderiam |
| **UptimeRobot** (monitor) | O backend gratuito do Render "dorme" depois de 15 minutos sem acesso, e o primeiro visitante esperaria cerca de 30 segundos. Um acesso a cada 14 minutos em `/api/health/` o mantém acordado, sem custo |
| **Registro.br** (domínio) | Domínio `.com.br` do ICC, com a zona DNS apontando para o Render |

As 750 horas gratuitas mensais do Render cobrem um serviço ligado o mês inteiro (no máximo 744 horas), desde que seja o único web service gratuito do workspace. O endpoint de health não consulta o banco, para o Neon continuar suspendendo quando ocioso.

Alternativas consideradas: trocar a hospedagem do backend (a Vercel roda Django como função serverless, mas exigiria adaptar o projeto; a Cloudflare não roda Django) ou usar um plano pago do Render. O monitor resolveu a lentidão sem mudar a arquitetura, e trocar de hospedagem continua sendo uma opção futura. Os detalhes operacionais estão em [`operacao.md`](operacao.md).

## 5. Segurança e configuração

- Credenciais ficam só em variáveis de ambiente (`backend/.env.example` é o modelo), e o `.env` é ignorado pelo Git. Os valores do `docker-compose.yml` valem só no ambiente local.
- Com `DEBUG=False`, o backend exige HTTPS, ativa o HSTS, usa cookies seguros e libera o CORS só para o domínio do site.
- A API pública é somente leitura. As escritas passam pelo admin, que exige login.
- O site não coleta dados pessoais de visitantes: o contato é feito pelos canais oficiais do ICC (e-mail e redes), e as inscrições do processo seletivo vão para um formulário externo.

## 6. Inscrições do processo seletivo controladas pelo admin

O ICC não tem lista de e-mails para avisar sobre novos processos. Por isso, o site não pede cadastro de interessados. Quem controla a abertura das inscrições é o admin: com **Inscrições abertas** marcado, a página mostra "Inscreva-se" com o link do formulário (Google Forms), e desmarcado mostra "Inscrições encerradas".

Só um processo fica ativo por vez, e o último continua visível, com as inscrições fechadas, até o próximo ser cadastrado. Assim as datas e etapas do processo anterior servem de referência.

## 7. Artigos em Markdown, com imagens enviadas pelo admin

Os artigos são escritos pelos membros do ICC, e o texto precisava de formatação e imagens no meio. Entre as opções (Markdown no texto ou o artigo em PDF exibido na página), o ICC escolheu o **Markdown**: o conteúdo fica na própria página, com o mesmo padrão visual em todas as publicações e boa leitura no celular. O PDF fica como possibilidade futura.

Como foi feito:

- **Renderização segura.** O texto é escrito em Markdown no admin e exibido pelo `react-markdown`, com `remark-gfm` para tabelas. A biblioteca não executa HTML: um `<script>` colado no texto aparece como texto, e links `javascript:` são descartados. Isso evita guardar HTML ou limpá-lo.
- **Imagens por número.** As imagens são enviadas em **Imagens do artigo**, no próprio admin, e vão para o Cloudinary. O texto as chama pelo número (`![](imagem-1)`) e não pelo endereço. Assim, texto e imagens são preenchidos no mesmo formulário e salvos de uma vez, sem esperar o Cloudinary gerar a URL, e quem publica não depende do time de desenvolvimento nem precisa de conta no Cloudinary.
- **Rascunho por padrão.** Um artigo novo nasce com "Publicado" desmarcado e só aparece no site e na API depois de publicado. Dá para salvar um artigo pela metade sem exibi-lo incompleto.
- **Slug opcional.** O artigo pode ter um endereço legível, digitado à mão. Sem slug, o endereço usa o número do artigo.
- **Fórmulas.** São escritas em LaTeX e desenhadas pelo KaTeX, e só o `$$` abre fórmula. Com o cifrão simples, valores em reais ("R$ 10 mi e R$ 20 mi") virariam fórmula. O KaTeX bloqueia comandos perigosos, e uma fórmula com erro aparece em vermelho sem quebrar o resto do artigo. O peso extra (cerca de 130 kB comprimidos) só é carregado na página do artigo.
- **Texto do Word.** Quem escreve no Word dispensa aprender Markdown: o ICC converte na publicação pelo Google Docs, como explica o [guia de artigos](guia-artigos.md#converter-o-texto-para-markdown).

## 8. Nomes alinhados ao vocabulário do ICC

Os models e as rotas da API usam os termos que o ICC usa: `Program`, `ProgramComponent`, `ProgramCase`, `Article` e `Member`, com rotas como `/programs/` e `/articles/`. O objetivo é que quem lê o código ou a API encontre os mesmos nomes que vê no site e no admin.

O app Django continua se chamando `website`. Renomeá-lo mudaria os nomes das tabelas e exigiria migrar o banco, por um ganho só visual.

## 10. Login do `/admin` sem limite de tentativas

O `/admin` é a única parte do site com escrita, mas o que ele protege é o conteúdo público de um clube estudantil, sem dados pessoais nem financeiros. Por isso o projeto **não** usa limite de tentativas de senha nem segundo fator. A defesa fica em medidas que não custam manutenção:

- **Senhas longas:** mínimo de **12 caracteres**, e o Django recusa as comuns e as só numéricas.
- **HTTPS**, cookies seguros e **sessão de 12 horas sem uso**, em vez dos 14 dias do padrão.
- **Grupo Editores:** quem só edita conteúdo não é superusuário, então uma conta invadida não cria logins nem apaga cadastros.
- **Sem a conta `admin/admin` em produção:** ela só existe no ambiente local (`setup_dev` recusa rodar com banco externo ou `DEBUG=False`). Em produção, cada pessoa tem o próprio login.
- **Desativar quem sai** da gestão (veja o [guia do admin](guia-admin.md)).

**O que foi considerado e descartado.** Um limite de tentativas (testado com o django-axes) exigia uma dependência, tabelas e um middleware, mais uma decisão delicada: contar só por usuário deixa qualquer pessoa de fora trancar a conta de um editor, e contar por IP depende de o IP real chegar corretamente atrás do Cloudflare e do proxy do Render, que não foi possível testar em produção (e o `X-Forwarded-For`, que o Render não filtra, pode ser forjado). A manutenção não compensava o risco.

**Quando reavaliar:** se o ICC passar a guardar dados pessoais ou sensíveis no admin, ou se houver sinal de tentativas de invasão nos logs do Render. Nesse caso, o caminho é um limite de tentativas por usuário e IP (lendo `CF-Connecting-IP`) e, se possível, segundo fator para os superusuários.

## 9. Contas e acessos ligados a uma conta de e-mail do ICC

A infraestrutura (Render, Neon, Cloudinary e UptimeRobot) fica em uma conta de e-mail do ICC, passada de um Diretor Tech para o seguinte. Assim, o acesso pertence à entidade e não a uma pessoa. As exceções são o GitHub, em que cada pessoa usa a própria conta, e o domínio, que no Registro.br fica em nome de uma pessoa física porque o ICC não tem CNPJ. As consequências de cada caso estão em [`passagem-de-gestao.md`](passagem-de-gestao.md).
