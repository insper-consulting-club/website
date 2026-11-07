# Passagem de gestão

Este documento é para o Diretor Tech que entra e para quem sai. Descreve quais acessos existem, como transferi-los e o que trocar para que a gestão anterior perca acesso. Detalhes de produção estão em [`operacao.md`](operacao.md).

## Conta de infraestrutura

Os serviços de produção pertencem a uma única conta de e-mail do ICC, a conta de infraestrutura. O endereço não é registrado neste repositório porque ele é público e essa conta controla o domínio e toda a infraestrutura. O Diretor Tech que sai passa o endereço e a senha ao que entra, por um canal seguro.

Essa conta é passada de gestão a gestão, de um Diretor Tech para o seguinte. Ela é o login do Render, do Neon, do Cloudinary e do UptimeRobot, recebe os alertas do monitor de uptime e os avisos do Registro.br.

O e-mail de recuperação da conta é o e-mail pessoal de quem ocupa a presidência do ICC na gestão corrente. Ele permite recuperar o acesso se o Diretor Tech perder a senha ou o segundo fator. Por ser pessoal, precisa ser atualizado quando a presidência mudar.

Apenas uma pessoa deve ter acesso à conta por vez. Quem preside o ICC só entra pelo e-mail de recuperação, caso o responsável perca o acesso.

Quem assume a conta deve:

1. Receber o endereço e a senha do Diretor Tech anterior por um canal seguro, nunca por grupo de mensagem nem pelo repositório.
2. Trocar a senha no mesmo dia.
3. Conferir a verificação em duas etapas e vinculá-la ao novo responsável, e gerar novos códigos de recuperação.
4. Não registrar a senha em documentos compartilhados nem no repositório. Os demais serviços estão vinculados a essa conta, então a senha do Gmail é a credencial central.
5. Na troca de presidência, atualizar o e-mail de recuperação para o do novo presidente e remover o do anterior.

## Acessos

| Acesso | Para quê | Como passar |
|---|---|---|
| Conta de infraestrutura (Gmail) | Entrada em todos os serviços abaixo e alertas | Entrega da senha e troca, como acima |
| Render (`icc-backend` e `insperconsultingclub`) | Publicar, ver logs, ver e editar variáveis | Login pela conta de infraestrutura |
| Neon | Banco de dados | Login pela conta de infraestrutura |
| Cloudinary | Imagens | Login pela conta de infraestrutura |
| UptimeRobot | Monitor de uptime | Login pela conta de infraestrutura |
| Registro.br | Domínio e DNS | Login do próprio titular. A conta de infraestrutura recebe os avisos ([Titularidade do domínio](#titularidade-do-domínio)) |
| GitHub, organização `insper-consulting-club` | Código | Conta pessoal de cada um, com papel definido na organização ([Organização do GitHub](#organização-do-github)) |
| Superusuário do `/admin` | Criar logins para o ICC | Ver abaixo |

## Titularidade do domínio

O ICC não tem CNPJ, então o domínio `insperconsultingclub.com.br` está registrado no Registro.br em nome de uma pessoa física. O cadastro usa a conta de infraestrutura como e-mail, mas a titularidade pertence à pessoa cujo nome e CPF constam no registro, e acessar a conta não muda isso.

- Quem é titular pode continuar sendo depois de deixar a gestão. Não há troca obrigatória a cada passagem.
- A titularidade só muda se o titular pedir para deixar de sê-lo ou quando o ICC passar a ter CNPJ. A troca é um procedimento administrativo do Registro.br, feito sem login, a partir de [registro.br/ajuda/procedimentos-administrativos](https://registro.br/ajuda/procedimentos-administrativos/). Gera-se a solicitação no formulário, o titular atual a assina pelo gov.br (conta de nível Prata ou Ouro) e envia um documento com CPF, e o novo titular envia um documento com CPF (pessoa física) ou o comprovante de inscrição e situação cadastral na Receita (CNPJ). O Registro.br analisa em até 2 dias úteis. Confira a página no momento da troca, porque as exigências podem mudar.
- Qualquer troca de titularidade exige a assinatura do titular atual. Por isso, ele precisa continuar contactável e com acesso à própria conta gov.br.
- O cadastro é pessoal e contém dados do titular. Não compartilhe a senha do Registro.br. A conta de infraestrutura é o e-mail de contato e recebe os avisos e a recuperação de senha, por isso o acesso a ela deve ser restrito.
- A renovação é anual e a data aparece no painel. Se o domínio expirar, o site e a API continuam hospedados no Render, mas deixam de ser acessíveis pelos endereços do domínio.

Quando o ICC tiver CNPJ, peça a alteração de titularidade para ele, mantenha a conta de infraestrutura como contato e atualize esta seção.

## Organização do GitHub

O código fica na organização `insper-consulting-club`. Ao contrário dos outros serviços, o GitHub não usa a conta de infraestrutura: cada pessoa entra com a própria conta.

A organização exige verificação em duas etapas de todos os membros, tem permissão base de leitura e um time `tech` com acesso de escrita aos repositórios de quem desenvolve.

- Evite depender de um único owner. Sempre que possível, mantenha mais de uma pessoa com esse papel, para a organização não ficar sem quem a administre.
- Dê acesso de escrita, por meio do time `tech`, a quem desenvolve.
- Na troca de gestão, adicione quem entrou, ajuste os papéis e remova quem saiu (Settings > People).

## Troca de gestão

Faça os itens abaixo quando alguém que tinha acesso a senhas e chaves deixar a função. Toda variável alterada no Render só vale depois de um novo deploy do serviço, que o Render costuma oferecer ao salvar.

### 1. Conta de infraestrutura

Troque a senha e a verificação em duas etapas, como descrito em [Conta de infraestrutura](#conta-de-infraestrutura).

### 2. Banco de dados

No painel do Neon, gere uma nova senha para o usuário do banco. Em seguida, atualize a `DATABASE_URL` no serviço `icc-backend` do Render e faça o deploy.

### 3. Cloudinary

Gere uma nova API secret e atualize `CLOUDINARY_API_SECRET` no Render. Se a chave (`CLOUDINARY_API_KEY`) também foi exposta, gere um novo par.

### 4. Chave do Django

Gere uma nova `SECRET_KEY` (o comando está em [`backend/.env.example`](../backend/.env.example)) e atualize no Render. Isso desloga todos do admin, o que é esperado.

### 5. Logins do admin

No `/admin`, em **Usuários**, desative quem saiu (desmarque "Ativo") e crie os logins de quem entrou, um por pessoa. Veja as regras no [guia do admin](guia-admin.md#logins-para-outras-pessoas-do-icc).

Quem tem **Status de superusuário** pode criar outros logins. Mantenha isso restrito a poucas pessoas.

### 6. Pessoas fora da organização

Remova quem saiu da organização do GitHub. Como os demais serviços usam a conta de infraestrutura, não há convidados a remover neles. Confira, se houver algum, em *Workspace Settings* do Render e na lista de usuários do Cloudinary e do Neon.

### 7. Conexão do Render com o GitHub

O Auto-Deploy usa as credenciais Git de uma conta pessoal de GitHub conectada ao Render. Se essa pessoa sair da organização, os deploys podem parar. Na troca de gestão:

1. Conecte a conta de GitHub do novo responsável ao Render (Account Settings) e desconecte a anterior.
2. Em cada serviço, em **Settings > Build & Deploy > Git Credentials**, selecione a conta do novo responsável.
3. Confirme com um merge de teste ou um **Manual Deploy**.

### 8. Chaves de equipe anterior

Chaves e senhas pessoais do ex-Diretor Tech (por exemplo, a `DATABASE_URL` copiada para o computador dele ou um `.env` local) devem ser consideradas comprometidas depois da saída. Os itens 2, 3 e 4 resolvem isso.

## Checklist de transição

### Para quem sai

- [ ] Entregar a senha da conta de infraestrutura e confirmar que o novo responsável consegue entrar.
- [ ] Entregar a pasta `site-data/` (dados reais e fotos dos membros), se existir, por um canal seguro, e apagar as cópias locais.
- [ ] Apagar de seus computadores qualquer `.env` com credenciais de produção e dumps de banco.
- [ ] Informar o que está pendente (mudanças em andamento, pedidos do ICC, problemas conhecidos).

### Para quem entra

- [ ] Receber a conta de infraestrutura e trocar a senha e a recuperação de conta.
- [ ] Conferir quem é o titular do domínio no Registro.br e a data de vencimento ([Titularidade do domínio](#titularidade-do-domínio)).
- [ ] Entrar no Render, no Neon, no Cloudinary e no UptimeRobot e confirmar que tudo está ativo.
- [ ] Ser adicionado à organização do GitHub e conseguir rodar o projeto seguindo [`desenvolvimento.md`](desenvolvimento.md).
- [ ] Trocar as credenciais conhecidas pela gestão anterior ([Troca de gestão](#troca-de-gestão)).
- [ ] Criar o login de admin próprio e os dos novos membros do ICC.

### Verificação final

- [ ] O site abre e mostra membros, parceiros, artigos e o processo seletivo.
- [ ] O login no `/admin` funciona, e uma edição de teste aparece no site depois de recarregar a página.
- [ ] Uma foto enviada pelo admin continua aparecendo depois de um novo deploy do backend. Isso comprova que o Cloudinary está configurado.
- [ ] O monitor de uptime está verde e o e-mail de alerta é o da conta de infraestrutura.
- [ ] O Auto-Deploy do Render continua em "On Commit": um merge de teste na `main` aparece em **Events** como **Live**.
- [ ] O domínio está em dia e responde com HTTPS, tanto o site quanto a API.
- [ ] Existe um backup recente do banco ([`operacao.md`](operacao.md#backup-do-banco)).

## O que o ICC faz sozinho

Estas tarefas não exigem o Diretor Tech e estão no [guia da área administrativa](guia-admin.md): cadastrar e arquivar membros, parceiros, cases, projetos e artigos, abrir e fechar as inscrições do processo seletivo e atualizar as estatísticas da Home. O Diretor Tech entra quando algo exige mexer no código, em variáveis, em contas ou em domínio.
