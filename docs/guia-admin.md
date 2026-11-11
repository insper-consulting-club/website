# Guia da área administrativa

Este guia é para quem cuida do conteúdo do site no ICC. Nada aqui exige mexer em código.

**Endereço:** https://api.insperconsultingclub.com.br/admin/ (ou o link **"Área administrativa"** no rodapé de qualquer página do site)

Entre com o seu usuário e a sua senha. Tudo o que você salva aparece no site ao recarregar a página, em até 1 minuto. Se o admin demorar cerca de 30 segundos para abrir, o site continua funcionando, mas avise o responsável técnico: provavelmente o monitor do servidor parou.

**Testar antes de salvar no site:** como tudo aparece no site assim que é salvo, qualquer cadastro, de um artigo a um novo programa, pode ser ensaiado antes em uma cópia do site no seu computador, que não afeta o site no ar. O [guia do ambiente local](guia-ambiente-local.md) explica como montá-la.

**Atalho:** a [rotina de cada semestre](#rotina-de-cada-semestre), no fim deste guia, resume o que atualizar a cada troca de semestre.

---

## Como a tela está organizada

O **menu à esquerda** agrupa o conteúdo por assunto: **Site**, **Equipe**, **Parceiros**, **Programas e projetos**, **Artigos**, **Processo seletivo** e **Acesso** (usuários, grupos e, só para administradores, a atividade recente). Quem tem um login limitado vê só os grupos que pode usar. A busca no topo do menu acha qualquer tela pelo nome. Na página inicial, o conteúdo também aparece no quadro **"Conteúdo do site"**. Em todas as telas o padrão é o mesmo:

- **Adicionar** (botão no canto superior direito da lista) cria um registro novo.
- Clicar no nome de um registro abre a edição.
- **Salvar** grava e volta para a lista. **Salvar e continuar editando** grava e fica na mesma tela.
- Na lista, a caixa de busca e os filtros da direita ajudam a achar o que você procura.
- **Alterações não salvas:** se você alterar um formulário e tentar sair da página sem salvar, o navegador pergunta antes de descartar.
- **Ver no site:** na edição de um artigo, programa, projeto, membro, parceiro, processo seletivo e da configuração do site, o botão **Ver no site** abre a página pública correspondente, para conferir o resultado. Ele não aparece para o que está escondido do site (rascunho de artigo, projeto arquivado, parceiro ou programa oculto). O site pode levar até um minuto para mostrar uma mudança recém-salva.
- **Menu lateral:** vem com o que se edita com mais frequência primeiro (Artigos, Equipe, Parceiros, Programas e projetos, Processo seletivo), e deixa **Site** (configuração, textos e estatísticas) e **Acesso** (usuários, grupos e atividade recente) no fim.
- **Seção Avançado:** nos formulários de artigo, parceiro, programa e case, os campos que quase nunca mudam (a ordem de exibição, por exemplo) ficam numa seção recolhida chamada **Avançado**, no fim da página. Clique nela para abrir. Se um desses campos tiver erro ao salvar, ela abre sozinha.
- **Reordenar arrastando:** onde existe ordem de exibição, arraste a linha pela alça para mudar a posição e salve. Vale para as listas de Diretorias, Parceiros, Programas, Estatísticas e Materiais de preparação, e para as tabelas dentro de um registro (blocos de conteúdo, imagens do projeto, itens de navegação, benefícios para parceiros, etapas e requisitos do processo, vínculos com diretorias). O número de ordem fica escondido e é preenchido sozinho. Duas exceções: o cronograma de um projeto segue a data de cada evento, e os artigos seguem a data de publicação.

| Quero cadastrar ou editar | Linha do admin |
|---|---|
| Pessoas da equipe | Membros, Cargos, Diretorias |
| Empresas parceiras | Parceiros, Categorias dos parceiros |
| Programas do ICC e o que os compõe | Programas (os componentes ficam numa aba dentro do programa) |
| Trabalhos feitos com parceiros | Projetos |
| Cases dos programas | Cases dos programas |
| Textos publicados pelos membros | Artigos |
| Próximo processo seletivo | Processos seletivos, Materiais de preparação |
| Números da Home | Estatísticas |

### Prévia dos textos em Markdown

Nos campos escritos em Markdown (o texto de um **artigo**, a **Política de Privacidade** e o texto dos **blocos de conteúdo dos programas**), o botão **Prévia**, na barra acima do campo, abre o texto desenhado pelo próprio site, com os mesmos estilos, fórmulas e imagens do artigo publicado. A prévia acompanha o que você digita. Nada é publicado até clicar em **Salvar**. As imagens de um artigo novo só aparecem na prévia depois que o artigo e as imagens forem salvos uma vez. Se o botão **Prévia** não aparecer, o endereço do site não está configurado (veja `FRONTEND_URL`, em [`arquitetura.md`](arquitetura.md)).

### Depois de salvar e ao enviar imagens

- **Aviso depois de salvar:** o admin mostra "A mudança aparece no site em até 1 minuto". É o tempo que o navegador de quem visita guarda as respostas do site. Se a mudança ainda não apareceu, espere um pouco e recarregue a página.
- **Tamanho das imagens:** cada imagem enviada pode ter até **5 MB**. Acima disso, o admin recusa e mostra o tamanho real. Fotos de celular costumam ser maiores: reduza ou comprima a imagem antes de enviar (qualquer editor de imagens ou site de compressão serve).

### Esconder ou apagar

Parceiros, programas e cases têm o campo **"Exibir no site"**. Projetos têm o campo **"Ativo"**. Artigos têm o campo **"Publicado"**. Desmarcado, o item some do site, mas continua guardado e pode voltar quando você quiser. Membros que saem são arquivados com a caixa **"Exibir na equipe"** (ver [Membros](#membros)).

**Prefira esconder ou arquivar a apagar**: apagar é definitivo.

### Logins para outras pessoas do ICC

Cada pessoa que mexe no site deve ter o próprio login. Compartilhar senha impede saber quem fez cada alteração.

**Para dar acesso:** no quadro **Autenticação e Autorização**, abra **Usuários > Adicionar usuário**.

1. Crie o nome de usuário e a senha.
2. Na tela seguinte, marque **"Membro da equipe"**. Sem isso, a pessoa não consegue entrar no admin.
3. Escolha o nível de acesso. Existem dois:
   - **Editor (o caso comum):** deixe "Status de superusuário" desmarcado e, em **Grupos**, escolha **Editores**. O grupo já traz as permissões certas, sem precisar escolher uma a uma.
   - **Administrador:** marque "Status de superusuário". Dá acesso total, incluindo criar outros logins, apagar qualquer registro e mexer na estrutura do site. Deixe isso para duas pessoas (por exemplo, o Diretor Tech e alguém da presidência), para nunca depender de uma só.

**O que o grupo Editores pode e não pode:**
- Pode criar e editar membros, parceiros, programas, projetos, cases, artigos, processos seletivos, e os textos e contatos do site (**Textos do site**, **Seções da Home** e **Configuração do site**), e mexer nas listas dentro de cada registro (blocos, imagens, etapas), inclusive removendo linhas.
- **Não** vê as abas **Marca e compartilhamento** e **Política de Privacidade** da configuração, nem o menu do site e os benefícios para parceiros. Isso fica com os administradores.
- **Não** vê Usuários nem Grupos, e **não** apaga membros, parceiros, projetos, programas, cases, artigos nem processos. Para tirar algo do ar, use as opções de esconder (veja "Esconder ou apagar"). Pode **criar um cargo novo** (pelo botão ao lado do campo **Cargo principal** do membro), que entra como membro comum; não escolhe a prioridade nem altera os cargos existentes, porque a prioridade define quem é liderança na Home. Um administrador ajusta isso em **Cargos**.
- O menu mostra só o que a pessoa pode usar.

O grupo é criado sozinho na primeira publicação. Se for preciso liberar algo a mais (por exemplo, apagar artigos), ajuste em **Grupos > Editores**: o ajuste fica e não é desfeito nas próximas publicações. Para voltar ao padrão, apague o grupo **Editores** em **Grupos**: ele é recriado com as permissões originais no próximo deploy (as pessoas que estavam nele precisam ser colocadas de novo). As permissões aparecem agrupadas por assunto, como "Pode ver", "Pode alterar", "Pode adicionar" e "Pode excluir".

**Quem mudou o quê:** em **Acesso > Atividade recente** (só administradores) fica a lista das alterações feitas no admin, com data, usuário, cadastro, registro e o que mudou. Cada registro também tem o botão **Histórico**.

**Quando alguém sai da gestão:** abra o usuário dela e desmarque **"Ativo"**. Ela perde o acesso na hora.

**Senhas:** o admin exige pelo menos **12 caracteres** e recusa senhas comuns ou só de números. Cada pessoa deve ter uma senha longa e só dela, de preferência guardada num gerenciador de senhas (assim ninguém precisa decorar nem reaproveitar a de outro serviço). O login do admin não bloqueia depois de várias tentativas erradas, então a senha longa é a principal proteção. A sessão expira depois de 12 horas sem uso, e aí é preciso entrar de novo. O admin não tem "esqueci minha senha", porque não envia e-mail: quem perder a senha pede a um administrador, que abre o usuário em **Usuários** e usa o link de alterar a senha, ao lado do campo **Senha**.

---

## Membros

### Cadastrar uma pessoa

**Membros > Adicionar membro**

1. **Nome**, **Foto** (JPG ou PNG, de preferência quadrada), **Cargo principal** e **LinkedIn**.
2. **Exibir na equipe** fica marcada; desmarque quando a pessoa deixa o clube (veja "Quando alguém sai do clube"). Os projetos de que a pessoa participou são ligados pelo cadastro do **projeto**, no campo **Equipe**.
3. Nas abas **Trajetória** e **Vínculos com diretorias**, no alto do formulário, ficam as listas da pessoa:
   - **Trajetória** (opcional): uma linha por semestre, com o **Semestre** no formato `AAAA.S` (por exemplo, `2026.1`) e o **Cargo nesse semestre**. O perfil público mostra as etapas em ordem de semestre, e o admin recusa um semestre fora do formato.
   - **Vínculos com diretorias:** uma linha por diretoria da pessoa, com o cargo nela. Arraste a linha para mudar a ordem dentro da diretoria.
4. Salvar.

O **Cargo principal** define a ordem da pessoa no site e se ela aparece na Home. Os cargos ficam em **Cargos**, e cada um tem uma **Prioridade para exibição**: 0 = Presidência, 1 = Vice, 2 = Diretoria, 3 = Coordenação, 4 = Membro/Mentor, 5 = Trainee. Quem tem prioridade até 2 aparece na Home como liderança. Um cargo criado por um editor entra com prioridade 4 (membro comum); só administradores veem e mudam a prioridade.

### Quando alguém sai do clube

Em vez de apagar, **arquive**:

- na lista de Membros, marque a pessoa, escolha a ação **"Arquivar selecionados"** e clique em **Ir**;
- na própria lista, desmarque a caixa **Exibir na equipe** da pessoa e salve; ou
- abra a pessoa e desmarque **Exibir na equipe**.

A pessoa some da página Equipe, mas o histórico (cases, trajetória) continua guardado. Para trazê-la de volta, use **"Reativar selecionados"**. O filtro **Situação**, à direita, separa membros atuais de ex-membros.

**Excluir** fica só para cadastros feitos por engano.

### Diretorias

Em **Diretorias** você cria, renomeia e reordena as diretorias. A ordem das linhas (arraste para mudar) define a ordem das seções na página Equipe e no menu "Nossa Equipe".

---

## Parceiros

**Parceiros > Adicionar parceiro** (ou clique em um existente para editar)

1. **Nome**, **Categoria**, **Site do parceiro** e **Descrição**. As categorias ficam em **Categorias dos parceiros**.
2. **Logo:**
   - use **PNG com fundo transparente**, de preferência recortado rente ao logo, sem margem vazia em volta. Assim ele fica do tamanho certo no carrossel da Home e na página de parceiros;
   - **SVG é recusado** pelo admin.
3. **Ordem de exibição:** na lista de parceiros, arraste a linha para mudar a posição.
4. Salvar. A miniatura na lista mostra o logo atual.

Para tirar um parceiro do site sem apagar, desmarque **"Exibir no site"**. Dá para fazer isso direto na lista.

---

## Programas e cases

### Programas

**Programas > Adicionar programa.** Cada programa aparece no menu "Projetos" e tem página própria. Campos principais:

- **Nome**, **Subtítulo** e **Descrição**.
- **Slug:** o identificador usado no endereço da página (`/projetos/<slug>`). Ele é preenchido a partir do nome. Depois de publicado, evite mudá-lo, porque os links antigos deixam de funcionar.
- **Tópicos:** um por linha.
- **Ícone do card.**
- **Link de inscrição:** só para programas com formulário próprio.
- **Exibir no site.** A **Ordem de exibição** fica em **Avançado**, mas o mais simples é arrastar a linha na lista.
- **Blocos de conteúdo:** no fim do formulário, na aba **Blocos de conteúdo do programa**, você escreve a descrição detalhada da página, no formato que fizer sentido para aquele programa. Clique em adicionar bloco e preencha:
  - **Título** (opcional), como "Para quem é", "Como funciona" ou "Requisitos".
  - **Texto**, em Markdown: `## Seção`, `**negrito**`, `- item de lista` e `[link](https://...)`. Separe os parágrafos com uma linha em branco.
  - **Imagem** (opcional), com **Legenda** e **Posição da imagem** (à direita, à esquerda ou centralizada, abaixo do texto).
  - **Ordem:** os blocos aparecem na página nessa ordem, logo abaixo do topo e antes de "Como funciona".

  Não há estrutura obrigatória: cada programa pode ter os blocos que precisar. A **Descrição** continua sendo o resumo curto que aparece nos cards e no topo da página.

### Componentes dos programas

Na aba **Componentes dos programas**, dentro do próprio programa, ficam as partes dele (por exemplo, as atividades que o compõem). Cada componente tem **Título** e **Descrição**, e aparece na seção "Como funciona" da página do programa.

### Cases dos programas

**Cases dos programas > Adicionar:**

1. **Programa** a que o case pertence, **Semestre** (no formato `2025.1`), **Área**, **Tema**, **Banca avaliadora** (uma firma por linha), **Premiação** e **Link da publicação**, se houver. O **Título** só é necessário quando o semestre tem mais de um case, por exemplo "1º Case".
2. Embaixo, em **Participantes do Case**, adicione os membros e o papel de cada um (integrante ou mentor). Comece a digitar o nome para buscar. Arraste a linha para mudar a ordem em que as pessoas aparecem no case; o site mostra primeiro os integrantes e depois os mentores.
3. Salvar.

A página **Projetos** do site mostra os programas, e a página de cada programa mostra os cases dele.

---

## Projetos

**Projetos** são trabalhos feitos com um parceiro, como challenges, visitas e capacitações.

**Projetos > Adicionar projeto**

1. **Título**, **Descrição**, **Programa** e **Data de início**.
2. **Data de conclusão**, quando o projeto terminar.
3. **Parceiros envolvidos:** escolha na caixa da esquerda e passe para a direita.
4. Embaixo, se quiser, o conteúdo da página do projeto:
   - **Blocos de conteúdo do projeto:** título, texto e, se quiser, uma imagem com legenda e posição (à direita, à esquerda ou centralizada). Arraste para mudar a sequência. Para separar parágrafos, quebre a linha.
   - **Imagens do Projeto:** a galeria, com uma **Legenda** para cada imagem. Arraste para reordenar.
   - **Eventos do Cronograma:** data, título e descrição de cada etapa.
5. Salvar.

**Onde o projeto aparece no site:**

- **Página do projeto** (`/projetos/projeto/<número>`): descrição, data ou período, parceiros, blocos, imagens, linha do tempo e equipe. Quando a data de início e a de conclusão são iguais (uma visita, uma competição), a página mostra só "Data: 20 de março de 2026".
- **Página do programa**, na seção "Projetos", quando o projeto tem **Programa**.
- **Página Projetos**, na seção **"Outros projetos"**, quando o projeto está sem programa. Use isso para visitas, capacitações e competições que pertencem a vários programas ou a nenhum.
- **Página do parceiro**, em "Casos de sucesso", quando o projeto tem **Data de conclusão** e um parceiro.

Os membros que participaram são escolhidos no campo **Equipe** do próprio projeto: digite parte do nome para buscar e escolha; os escolhidos aparecem como etiquetas, e o "x" tira cada um. A equipe aparece na página do projeto e no perfil de cada pessoa.

Um projeto com **Data de conclusão** preenchida também conta nos números do parceiro.

**Arquivar um projeto** (em vez de apagar):

- na lista de Projetos, marque os projetos, escolha a ação **"Arquivar selecionados (somem do site)"** e clique em **Ir**; ou
- desmarque **"Ativo"** direto na lista, ou dentro do projeto, e salve.

O projeto arquivado some do site (de todas as páginas acima e do perfil dos membros), mas continua guardado. Para trazê-lo de volta, use **"Reativar selecionados"** ou marque **"Ativo"** de novo. O filtro **Ativo**, à direita da lista, separa os ativos dos arquivados.

---

## Artigos

Os artigos são escritos pelos membros do ICC e ficam **dentro do site**: cada um tem a própria página, com resumo, temas, o texto completo e os botões **Compartilhar** e **Citar** (citação em ABNT, APA, BibTeX, BibLaTeX e RIS).

O passo a passo completo, com a referência de Markdown, imagens, fórmulas, conversão de documentos e solução de problemas, está no **[guia de artigos](guia-artigos.md)**. Em resumo:

1. **Artigos > Adicionar artigo.** Preencha título e slug, os **autores** (lista logo abaixo, com os membros sugeridos ao digitar), temas, resumo, data e, se quiser, a imagem de capa. A faixa **Para publicar**, no alto, mostra o que falta.
2. Escreva o **Texto do artigo** em Markdown, com uma linha em branco entre os parágrafos.
3. Envie as imagens do texto em **Imagens do artigo** e chame cada uma no texto por `![](imagem-1)`.
4. Revise o artigo antes de publicar, de preferência no ambiente local (ver o [guia do ambiente local](guia-ambiente-local.md)).
5. Salve com **Publicado** desmarcado (rascunho). Quando estiver pronto, marque **Publicado**, salve e confira a página no site.

Na lista de artigos, a busca e os filtros **Autor** e **Tema** ajudam a achar um artigo, e as ações **Publicar selecionados** e **Despublicar selecionados** mudam vários de uma vez (despublicar devolve o artigo a rascunho, sem apagar o texto). Artigos sem autor não são publicados pela ação (o admin avisa quais são), e, ao publicar, ele avisa se algum está sem data de publicação, porque a ordem no site depende dela.

---

## Processo seletivo

O site mostra **um processo seletivo por vez**: o que estiver marcado como **Ativo**. Ativar um processo desativa os outros sozinho.

### Duplicar o processo anterior

Para o próximo semestre, em vez de recadastrar tudo: abra o processo anterior e clique em **Duplicar este processo**, no alto da página (ou marque o processo na lista e use a ação **Duplicar selecionados**). A cópia traz as datas, as etapas detalhadas, os requisitos e os materiais de preparação, e nasce **inativa, com as inscrições fechadas e sem o link do formulário**, com o título "... (cópia)". Depois é só ajustar as datas, escrever o novo título, preencher o link do formulário e marcar **Ativo** quando for a hora. O processo original não muda.

### Cadastrar um processo

**Processos seletivos > Adicionar**

1. **Título** (por exemplo, `Processo Seletivo 2027.1`) e **Ativo** marcado.
2. **Datas do Processo:** uma linha por fase, com nome, data ou período e ordem.
3. **Etapas Detalhadas** (opcional): descrição, duração e dicas de cada fase.
4. **Requisitos:** uma linha por requisito.
5. Salvar.

Os **materiais de preparação** (opcional) ficam em **Materiais de preparação > Adicionar**: escolha o processo, dê um título e liste os itens.

### Abrir e fechar as inscrições

- **Para abrir:** no processo ativo, marque **"Inscrições abertas"** e cole o link do formulário (Google Forms) em **"Link de inscrição"**. O site passa a mostrar o botão **"Inscreva-se"**. O admin recusa o salvamento com as inscrições abertas e sem link.
- **Para fechar:** desmarque **"Inscrições abertas"**. O site mostra **"Inscrições encerradas"** e um convite para seguir o Instagram.

**Entre um processo e outro:** deixe o último processo **ativo e com as inscrições fechadas**. Assim, quem visita o site vê as datas e etapas do último processo, que servem de referência. Quando o próximo começar, cadastre o novo processo: ele substitui o anterior ao ser ativado.

---

## Estatísticas da Home

**Estatísticas > Adicionar**: um **Valor/Número** (por exemplo, `120+`) e uma **Descrição** (por exemplo, `membros formados`). A faixa de números da Home só aparece quando existe pelo menos uma estatística.

---

## Configuração do site

**Configuração do site** abre direto na edição, porque existe um único registro. Não há botão de adicionar nem de excluir. A tela tem abas:

- **Marca e compartilhamento:** o **Nome do site** (aba do navegador, rodapé e prévia dos links), a **Descrição do site** e três imagens opcionais: o **Logo** em versão clara (usado no topo, no rodapé e na Home), o **Ícone da aba** (PNG quadrado, de preferência 256 x 256) e a **Imagem de compartilhamento** (1200 x 630, a que aparece no WhatsApp e no LinkedIn). Sem imagem enviada, o site usa a original. O admin confere o formato ao enviar: o **ícone** precisa ser **quadrado** (pelo menos 32 x 32), e a **imagem de compartilhamento** precisa ter pelo menos 600 pixels de largura e proporção parecida com 1200 x 630, senão o WhatsApp e o LinkedIn a cortariam. O logo não tem exigência de tamanho. Só administradores veem esta aba. Como o site é estático, essas mudanças só aparecem depois que o frontend é publicado de novo: no Render, serviço do frontend, **Manual Deploy** (o admin avisa ao salvar).
- **Contatos:** e-mail e links do Instagram, do LinkedIn e do GitHub, cada um com o nome que aparece no site. Trocar aqui atualiza o topo, o rodapé, a página Contato, o botão de inscrições encerradas e a Política de Privacidade.
- **Home:** a foto de "Quem somos" (opcional) e a descrição dela, lida por leitores de tela. Os textos da Home (título do topo, frase de destaque, "Quem somos", missão, chamada final) ficam em **Textos do site**, na página Home.
- **Páginas:** o campo **"Programa dos cases em destaque"** é uma lista dos programas cadastrados e define para onde o botão "Ver os cases" da página Projetos leva. Deixe vazio para esconder essa seção. O texto que aparece logo abaixo do título de cada página, a frase do rodapé e a mensagem de inscrições encerradas também ficam em **Textos do site**.
- **Política de Privacidade:** a data de atualização e o texto, em Markdown (`## Seção`, `**negrito**`, `- item`, `[link](https://...)`). Separe os parágrafos com uma linha em branco.
- **Itens de navegação:** o menu do topo, o menu do rodapé e o botão de destaque do topo (hoje, "Seja membro"). Cada item tem:
  - **Texto exibido**. A ordem é a das linhas (arraste para mudar).
  - **Onde aparece:** menu (topo e rodapé), só no topo, só no rodapé ou botão de destaque do topo.
  - **Página do site**, escolhida numa lista (Equipe, Parceiros, Projetos, Artigos, Processo seletivo, Contato, Política de Privacidade, Página inicial). Prefira esta opção: o link não quebra.
  - **Link livre**, só quando não houver página na lista: um endereço completo (`https://...`) ou um caminho do site (`/equipe`). Preencha a página **ou** o link livre, nunca os dois. Links externos abrem em outra aba.
  - **Exibir no site:** desmarque para esconder um item sem apagá-lo.

  Os submenus de **Projetos** (programas) e **Equipe** (diretorias) aparecem sozinhos nos itens que apontam para essas páginas. Cuidado para não esconder todos os itens do menu.
- **Benefícios para parceiros:** a lista de "Por que ser parceiro" da página Parceiros, com título, descrição e ordem.

As mudanças podem levar até um minuto para aparecer no site.

---

## Textos do site

Os títulos de seção, rótulos, botões e mensagens curtas (por exemplo, "Quem constrói o clube", "Calendário", "Nenhum artigo cadastrado no momento") ficam em **Textos do site**. A lista mostra uma linha por página do site, na ordem em que as páginas aparecem. Abra a página que quer ajustar.

- Dentro da página, os textos vêm agrupados por seção (Apresentação, Quem somos, Missão e assim por diante), cada um com uma descrição de onde aparece. Edite e clique em **Salvar**.
- Mensagens raras (por exemplo, "página não encontrada" ou "lista vazia") ficam num bloco recolhido no fim da página.
- Um texto alterado fica marcado como **Editado**, com o original logo abaixo e o botão **Restaurar o original**.
- A busca na lista procura pelo que o texto diz, pela descrição ou pela seção, e mostra os textos encontrados. O filtro **Situação** separa as páginas com textos editados.
- Para voltar uma página inteira ao original, marque a página e use a ação **Restaurar os textos originais das páginas selecionadas**.
- Alguns textos têm trechos entre chaves, como `{n}`, `{data}` ou `{programa}`. O site preenche esses trechos, então eles precisam continuar no texto. O admin avisa se algum for apagado.
- Não há botão para adicionar ou excluir: os textos existentes são os que o site usa.
- Os textos longos (missão, "Quem somos") ficam nas páginas deles, com uma caixa de várias linhas. A Política de Privacidade continua em **Configuração do site**, só para administradores.
- Um texto marcado como opcional (por exemplo, o final do título de "Quem somos", em vermelho) pode ficar vazio. Os demais não.

---

## Seções da Home

**Seções da Home** (menu Site) controla o que aparece na página inicial depois da Apresentação. O Topo e a Apresentação ficam sempre no começo e não aparecem na lista.

- **Mostrar ou esconder:** marque ou desmarque **Mostrar no site** na própria lista e salve. Uma seção escondida some da Home, mas nada é apagado.
- **Mudar a ordem:** arraste as linhas. O fundo das seções alterna entre claro e cinza pela posição, então mover uma seção não deixa duas iguais lado a lado. Estatísticas e Chamada final têm estilo próprio e não entram nessa alternância.
- **Aviso:** é a primeira linha, escondida por padrão. Para usar, escreva o texto em **Textos do site > Home > Aviso** (o título e o texto do botão são opcionais; sem texto, o aviso não aparece, mesmo ligado), depois abra o **Aviso** em Seções da Home, marque **Mostrar no site** e, se quiser um botão, escolha uma página do site ou um link livre. Por padrão ele fica logo depois da Apresentação, mas pode ser arrastado como as outras seções. Não há escolha de cores: o visual segue o guia de marca.
- Estatísticas e parceiros sem nada cadastrado não aparecem, mesmo ligados.
- Não há botão de adicionar nem de excluir: as seções existentes são as que o site sabe desenhar.
- As mudanças levam até um minuto para aparecer, como os textos.

---

## O que fica fora do admin

Pouca coisa fica fora do admin:

- o conteúdo da prévia ao compartilhar **um artigo ou página específica**: o WhatsApp e o LinkedIn sempre mostram a prévia geral do site, porque só leem o HTML estático, e ele é o mesmo para todas as páginas.

---

## Rotina de cada semestre

| Quando | O quê | Onde |
|---|---|---|
| Antes do processo seletivo | **Duplicar** o processo anterior, ajustar datas e etapas e deixar **Ativo** | Processos seletivos |
| Abertura do processo | Marcar **Inscrições abertas** e colar o link do formulário | Processos seletivos |
| Fim das inscrições | Desmarcar **Inscrições abertas** (o processo continua ativo, com as datas visíveis) | Processos seletivos |
| Entrada dos aprovados | Cadastrar os novos membros, com foto e diretoria | Membros |
| Troca de gestão | Arquivar quem saiu; atualizar cargos e diretorias | Membros, Cargos, Diretorias |
| Fim do semestre | Cadastrar os cases e projetos do semestre e atualizar os números da Home | Cases dos programas, Projetos, Estatísticas |
| Quando houver | Novos artigos e parceiros | Artigos, Parceiros |
| Troca de gestão | Dar login a quem entrou e desativar o de quem saiu | Usuários |

Em caso de dúvida técnica (site fora do ar, erro ao salvar, conteúdo que não aparece), procure o responsável técnico do site. As instruções para quem cuida da parte técnica estão no [README](../README.md) do repositório.
