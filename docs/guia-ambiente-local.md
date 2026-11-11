# Guia do ambiente local

Este guia mostra como rodar uma cópia do site no seu computador, para ver como uma mudança ficará antes de ela ir ao ar. Serve para qualquer mudança: um artigo, o cadastro de uma seção do admin (membros, parceiros, programas, processo seletivo) ou uma alteração no visual e no código do site. Não exige conhecimento técnico, só seguir os passos na ordem.

**O que você precisa saber antes:**

- O site local usa **dados de exemplo fictícios**, não os dados reais do ICC. Ele serve para testar como algo novo fica, mas não mostra os cadastros que já existem no site no ar.
- O banco de dados é só seu. Nada do que você cadastrar aqui aparece no site no ar. Para publicar, o conteúdo é cadastrado de novo no admin de produção.
- Dúvidas ou erros que este guia não resolva: fale com o Diretor Tech.

---

## 1. Instalar o que é preciso

### Docker Desktop

O Docker Desktop roda o site em um ambiente isolado, sem instalar banco de dados nem linguagens no seu computador.

1. Baixe em https://www.docker.com/products/docker-desktop/ a versão do seu sistema (Windows, macOS ou Linux) e instale.
2. No Windows, o instalador pode pedir para ativar o **WSL 2**. Aceite e reinicie o computador se ele pedir.
3. Abra o Docker Desktop e aguarde até ele indicar que está em execução (o ícone da baleia fica estável, e o painel mostra **Engine running**). Ele precisa ficar aberto sempre que você for usar o site local.

### GitHub Desktop

O GitHub Desktop baixa o projeto e o mantém atualizado.

1. Baixe em https://desktop.github.com/ e instale.
2. O repositório do ICC é público, então baixar o projeto não exige acesso especial à organização. Se o aplicativo pedir login ao abrir, entre com a sua conta do GitHub (ou crie uma, é gratuito).

---

## 2. Baixar o projeto

1. No GitHub Desktop, abra **File > Clone repository**.
2. Na aba **URL**, cole `https://github.com/insper-consulting-club/website`, escolha uma pasta do seu computador e clique em **Clone**.

Isso é feito uma vez só.

---

## 3. Ligar o site

1. No GitHub Desktop, abra o menu **Repository** e escolha **Open in Command Prompt** (Windows) ou **Open in Terminal** (macOS). Abre-se uma janela de comandos já dentro da pasta do projeto.
2. Digite o comando abaixo e tecle Enter:

   ```
   docker compose up --build
   ```

3. Aguarde. Na primeira vez demora vários minutos, porque o Docker baixa e monta tudo. Quando as mensagens pararem de aparecer com frequência, o site está pronto.

Deixe essa janela aberta enquanto usar o site.

---

## 4. Abrir o site e o admin

| O que | Endereço | Login |
|---|---|---|
| Site | http://localhost:5173 | Não precisa |
| Área administrativa | http://localhost:8000/admin/ | Usuário `admin`, senha `admin` |

Esse login só vale no seu computador. O site local já vem com membros, projetos, parceiros e artigos de exemplo.

---

## 5. Testar uma mudança

### Conteúdo cadastrado no admin

Funciona para qualquer seção do [guia da área administrativa](guia-admin.md): cadastre ou edite no admin local e confira o resultado no site local. Se algo estiver errado, corrija no admin, salve e atualize a página do site. Quando estiver correto, faça o mesmo cadastro no admin de produção.

Lembre que o site local começa com os dados de exemplo. Para testar a edição de algo que já existe no site no ar, cadastre antes um item parecido aqui.

**Exemplo, um artigo:**

1. No admin local, abra **Artigos > Adicionar artigo**.
2. Preencha os campos, cole o texto e envie as imagens, como explica o [guia de artigos](guia-artigos.md#do-texto-ao-site-passo-a-passo).
3. Marque **Publicado**. Aqui isso é seguro, porque o banco local é separado do site no ar.
4. Salve e abra http://localhost:5173/artigos. Confira o card na lista e a página do artigo: seções, tabelas, imagens nos lugares certos e fórmulas sem trechos em vermelho.

Para artigos, esta é a forma de conferir a página inteira (título, capa e card). O texto em si também pode ser revisado com o botão **Prévia** do admin (ver [Revisar antes de publicar](guia-artigos.md#revisar-antes-de-publicar)).

### Mudanças no visual ou no código

Quem altera arquivos do projeto (textos fixos, estilos, componentes) vê o resultado no site local assim que salva o arquivo, sem precisar religar o ambiente. Antes de abrir um PR, siga as verificações de [`desenvolvimento.md`](desenvolvimento.md#verificações-antes-do-pr).

---

## No dia a dia

| Para | Faça |
|---|---|
| **Desligar o site** | Na janela de comandos, tecle `Ctrl + C`. Para liberar tudo, rode também `docker compose down`. Os dados que você cadastrou continuam guardados |
| **Ligar de novo** | Abra o Docker Desktop, abra a janela de comandos pelo GitHub Desktop (passo 3) e rode `docker compose up` |
| **Atualizar o projeto** | No GitHub Desktop, confirme que a branch é a `main`, clique em **Fetch origin** e depois em **Pull origin**. Em seguida, rode `docker compose up --build`. Faça isso antes de revisar um artigo, para o site local ter as mesmas regras do site no ar |
| **Começar do zero** | Rode `docker compose down -v` (apaga os dados locais) e depois `docker compose up --build`. Os dados de exemplo voltam sozinhos |

---

## Problemas comuns

| Sintoma | O que fazer |
|---|---|
| `docker` não é reconhecido, ou aparece erro de conexão com o Docker | O Docker Desktop não está aberto. Abra-o, espere ficar em execução e tente de novo. Se acabou de instalar, feche e abra de novo a janela de comandos |
| O Docker Desktop reclama de virtualização | A virtualização precisa estar ativa na BIOS do computador. A mensagem do Docker Desktop indica como |
| O site abre, mas sem dados, ou dá erro | Na primeira vez, aguarde alguns minutos depois de `docker compose up`. Se continuar, desligue (`Ctrl + C`) e rode `docker compose up --build` de novo |
| Erro dizendo que uma porta (8000, 5173 ou 5432) está em uso | Outro programa usa a porta. Feche o programa, ou desligue um site local anterior com `docker compose down` |
| Depois de atualizar, o site local quebrou | Rode `docker compose down -v` e depois `docker compose up --build` |
| Esqueceu os dados do admin | Usuário `admin`, senha `admin` |

Para o passo a passo técnico (comandos, migrations, testes), veja [`desenvolvimento.md`](desenvolvimento.md).
