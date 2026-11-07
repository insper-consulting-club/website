# Guia de artigos

Este guia é para quem escreve e quem publica artigos no site do ICC. Ele não exige conhecimento técnico. Para o restante da área administrativa (membros, parceiros, processo seletivo etc.), veja o [guia da área administrativa](guia-admin.md).

Há dois papéis, que podem ser da mesma pessoa:

- **Quem escreve** entrega o texto (em Word ou Google Docs), as imagens e os dados do artigo.
- **Quem publica** tem login no admin, cadastra o artigo e o publica.

**Endereço do admin:** https://api.insperconsultingclub.com.br/admin/ (ou o link "Área administrativa" no rodapé do site). Os artigos ficam na linha **Artigos**.

---

## Como o artigo aparece no site

Cada artigo aparece em dois lugares:

**1. Na lista de Artigos** (`/artigos`), como um card, do mais recente para o mais antigo:

- a **imagem de capa**. Sem capa, o card mostra o nome da **Publicação** ou, se estiver vazio, "ICC";
- a linha com a **Publicação** e a **Data**;
- o **Título**, os **Autores** e o **Resumo**.

**2. Na página do artigo** (`/artigos/<slug>`), de cima para baixo:

1. a data, o título e os autores;
2. os **Temas**, como etiquetas;
3. a **Imagem de capa**, na largura inteira;
4. o quadro **Resumo**;
5. o **Texto do artigo**, com as imagens e fórmulas;
6. o bloco **Como citar**, gerado sozinho a partir dos autores, do título e do ano, com os botões **Copiar citação** e **Compartilhar** (LinkedIn);
7. o botão **Ver publicação original**, só quando o artigo tem **Link externo**.

---

## Do texto ao site: passo a passo

1. **Escreva** o artigo no Google Docs ou no Word. Use os estilos de título do editor para as seções (Título 2) e subseções (Título 3) e deixe as imagens em arquivos separados.
2. **Converta** o texto para Markdown (ver [Texto escrito no Word ou no Google Docs](#texto-escrito-no-word-ou-no-google-docs)).
3. **Revise** o artigo como ele ficará no site (ver [Revisar antes de publicar](#revisar-antes-de-publicar)).
4. No admin, abra **Artigos > Adicionar artigo** e preencha os campos (ver [Campo a campo](#campo-a-campo)).
5. **Cole** o texto convertido em **Texto do artigo**.
6. **Envie as imagens** em **Imagens do artigo** e coloque-as no texto pelo número (ver [Imagens no meio do texto](#imagens-no-meio-do-texto)).
7. **Salve** com **Publicado** desmarcado. O artigo fica guardado como rascunho e não aparece no site.
8. Marque **Publicado** e salve. O artigo aparece no site ao recarregar a página. Abra a página e confira. Se algo estiver errado, desmarque **Publicado** e corrija.

---

## Campo a campo

| Campo | Obrigatório | O que escrever |
|---|---|---|
| **Título** | Sim | O título do artigo, até 200 caracteres |
| **Slug da URL** | Não | O trecho final do endereço, em letras minúsculas, sem acento nem espaço, com palavras separadas por hífen. Por exemplo, `analise-do-setor-de-varejo` gera `/artigos/analise-do-setor-de-varejo`. Deve ser único. Se ficar em branco, o endereço usa o número do artigo |
| **Autores** | Não | Nomes separados por vírgula, por exemplo `Ana Silva, João Souza`. O texto aparece igual no card, no topo da página e na citação |
| **Temas** | Não | Palavras-chave separadas por vírgula, por exemplo `Estratégia, Varejo`. Viram etiquetas no topo do artigo |
| **Resumo** | Sim | Duas ou três frases. Aparece no card da lista e no quadro "Resumo" do artigo |
| **Texto do artigo** | Não, mas é o conteúdo | O texto completo, em Markdown |
| **Link externo** | Não | Endereço de outra publicação do mesmo artigo (revista, LinkedIn ou um PDF em uma pasta do ICC com acesso "Qualquer pessoa com o link"). Cria o botão "Ver publicação original" |
| **Publicação** | Não | Nome da revista ou do evento, quando o artigo também saiu fora do site. Aparece no card |
| **Data de publicação** | Recomendado | A data que aparece no card e no topo do artigo. Preencha sempre: um artigo sem data pode aparecer no topo da lista, antes dos mais recentes |
| **Imagem de capa** | Não | Imagem horizontal, de preferência na proporção 16:9 (por exemplo, 1600 por 900 pixels). No card ela é cortada nessa proporção, e na página aparece inteira |
| **Ordem de exibição** | Não | Só desempata artigos com a mesma data: o menor número aparece primeiro |
| **Publicado** | Começa desmarcado | Desmarcado, o artigo é rascunho e fica invisível no site |

Dica sobre o slug: depois que o link do artigo for compartilhado, evite mudar o slug, porque o link antigo deixa de funcionar. O admin recusa um slug repetido ou com acento ou espaço. Letras maiúsculas são aceitas, mas use só minúsculas para os endereços ficarem padronizados.

---

## Escrever o texto em Markdown

O texto do artigo é escrito em **Markdown**, um jeito simples de marcar a formatação com símbolos. O site converte os símbolos em títulos, listas, negrito e o resto. O título do artigo já aparece como título da página, então **comece as seções pelo nível `##`**.

### Referência rápida

| Para ter | Escreva |
|---|---|
| Parágrafo novo | uma linha em branco entre os parágrafos |
| Seção | `## Título da seção` |
| Subseção | `### Título da subseção` |
| **Negrito** | `**negrito**` |
| *Itálico* | `*itálico*` |
| Lista com marcadores | uma linha por item, começando com `- ` |
| Lista numerada | uma linha por item, começando com `1. `, `2. `, `3. ` |
| Link | `[texto do link](https://endereço.com)` |
| Citação | `> texto citado` |
| Linha divisória | `---` em uma linha sozinha |
| Imagem | `![](imagem-1)` em uma linha sozinha |
| Fórmula | `$$...$$` (ver [Fórmulas](#fórmulas)) |

### Exemplos

**Parágrafos e seções**

```
## Contexto do setor

O varejo brasileiro passou por uma transformação relevante na última década.

Este artigo analisa três movimentos principais.

### Primeiro movimento
```

**Listas.** Deixe uma linha em branco antes da lista.

```
Os principais fatores foram:

- digitalização dos canais de venda;
- consolidação de grandes redes;
- mudança no perfil do consumidor.

Passos da análise:

1. Levantamento dos dados.
2. Cálculo dos indicadores.
3. Comparação entre empresas.
```

Para uma lista dentro de outra, recue o item com quatro espaços.

**Links e citações**

```
Os dados vêm do [relatório anual da empresa](https://exemplo.com/relatorio).

> "A frase em destaque que o autor quer citar."
```

Links que começam com `http` abrem em outra aba.

**Tabelas.** Uma linha de cabeçalho, uma linha de traços e uma linha por registro, com as colunas separadas por `|`.

```
| Empresa | Receita (R$ mi) | Margem |
|---|---|---|
| Empresa A | 120 | 12% |
| Empresa B | 95 | 9% |
```

### Cuidados com símbolos

- **Uma quebra de linha simples não vira parágrafo.** Se você teclar Enter uma só vez, as duas linhas se juntam no site. Para separar, deixe uma linha em branco.
- Asteriscos (`*`), sublinhados (`_`), cerquilha (`#`) e o sinal `>` no começo de uma linha têm função própria. Se você quiser mostrá-los como texto comum, coloque uma barra invertida antes, por exemplo `\*` ou `\#`.
- Escreva sempre um espaço depois de `#`, `-`, `1.` e `>`. Sem o espaço, o símbolo aparece como texto.
- O cifrão sozinho é texto comum, então `R$ 10 mi` aparece como dinheiro. Só o cifrão duplo (`$$`) abre uma fórmula.

### O que não funciona ou não é recomendado

- **HTML.** Se você colar marcação HTML, o site a mostra como texto comum. Isso é proposital, por segurança.
- **Título de nível 1 (`# Título`).** Reserve o nível 1 para o título do artigo, que o site coloca sozinho.
- **Cores, tamanho de letra e alinhamento do texto.** O visual segue o padrão do site, igual em todos os artigos.
- **Notas de rodapé.** O site não tem estilo para elas. Cite a fonte no próprio texto, com um link, ou em uma seção "Referências" no fim do artigo.

---

## Imagens no meio do texto

As imagens são cadastradas no mesmo formulário do artigo, sem precisar salvar antes.

1. Desça até **Imagens do artigo**. Em cada linha, preencha:
   - **Número:** 1, 2, 3, na ordem que você preferir. Cada número só pode ser usado uma vez no artigo;
   - **Imagem:** um arquivo JPG ou PNG. Imagens muito pesadas deixam a página lenta, então prefira arquivos de até cerca de 2 MB;
   - **Legenda:** o texto que aparece embaixo da imagem.
2. No **Texto do artigo**, no ponto onde a imagem deve aparecer, escreva em uma linha sozinha:

   ```
   ![](imagem-1)
   ```

   Troque o 1 pelo número da imagem.
3. Salve. No site, a imagem ocupa a largura do texto, com a legenda embaixo.

Para usar uma legenda diferente só naquele ponto, escreva-a entre os colchetes:

```
![Evolução da receita entre 2020 e 2025](imagem-2)
```

Regras importantes:

- Uma imagem cadastrada, mas não chamada no texto, **não aparece** no site.
- Um número chamado no texto, mas sem imagem cadastrada, **fica invisível**. Confira os números antes de publicar.
- Para trocar uma imagem, envie a nova na mesma linha. O texto continua igual.
- Para uma imagem de capa, use o campo **Imagem de capa**, e não **Imagens do artigo**.

---

## Fórmulas

As fórmulas são escritas em LaTeX e desenhadas pelo KaTeX. Use sempre **dois cifrões** (`$$`).

**No meio da frase:**

```
O indicador é calculado por $$\frac{EBITDA}{Receita}$$ em cada período.
```

**Em destaque**, com `$$` em uma linha, a fórmula na linha de baixo e `$$` de novo na seguinte:

```
$$
VPL = \sum_{t=1}^{n} \frac{FC_t}{(1+i)^t}
$$
```

Comandos úteis:

| Para ter | Escreva |
|---|---|
| Fração | `\frac{a}{b}` |
| Potência | `x^{2}` |
| Índice | `x_{t}` |
| Somatório | `\sum_{t=1}^{n}` |
| Raiz quadrada | `\sqrt{x}` |
| Letras gregas | `\alpha`, `\beta`, `\sigma` |
| Percentual | `10\%` |
| Texto dentro da fórmula | `\text{receita líquida}` |

Se a fórmula tiver erro de digitação, ela aparece **em vermelho** no artigo e o resto do texto continua normal. Confira antes de publicar. Para algo que o KaTeX não desenhe, use uma imagem.

---

## Texto escrito no Word ou no Google Docs

Quem escreve não precisa aprender Markdown. O texto pode chegar em Word, e quem publica o converte:

1. Abra o arquivo no Google Docs (um `.docx` também abre lá).
2. Use **Arquivo > Fazer download > Markdown (.md)**.
3. Abra o arquivo `.md` em um editor de texto simples (Bloco de Notas, por exemplo), copie tudo e cole em **Texto do artigo**.

Depois da conversão, confira:

- **Títulos, listas, negritos, itálicos e links** costumam vir certos.
- **Imagens vêm quebradas.** Apague do texto o que aparecer no lugar delas (um trecho longo que começa com `![`) e use **Imagens do artigo**, como explicado acima.
- **Seções:** troque qualquer título de nível 1 (`#`) por `##`, porque o título do artigo já é colocado pelo site.
- **Tabelas** convertem melhor quando são simples. Confira o resultado.
- **Linhas em branco:** verifique se cada parágrafo está separado dos outros por uma linha em branco.

Sem o conversor, também dá para colar o texto puro e acrescentar à mão os `##` das seções e os `**` dos negritos.

Para textos longos, com tabelas ou fórmulas escritas no Word, uma ferramenta de IA pode fazer a conversão inteira (ver [Conversão com IA](#conversão-com-ia)).

---

## Conversão com IA

Uma ferramenta de IA conversacional pode fazer a parte mecânica da conversão: seções, listas, tabelas, fórmulas e marcadores de imagem. O uso é opcional e **não substitui a conferência**: quem publica continua responsável pelo que vai ao ar. O prompt abaixo resume as regras deste guia para a ferramenta aplicá-las, então, quando uma regra mudar (a convenção de fórmulas, o nível das seções, a forma de chamar imagens), atualize o prompt no mesmo PR.

### Antes de usar

- **Confidencialidade.** O texto do artigo é enviado a um serviço externo antes de ser publicado. Não use esse recurso em artigos com dados de clientes, informações não divulgadas de empresas ou qualquer conteúdo que o autor não queira fora do ICC. Na dúvida, pergunte ao autor.
- **Dados pessoais.** Remova do texto o que não for parte do artigo, como e-mails e telefones, antes de enviá-lo.
- **A ferramenta pode errar sem avisar.** Os erros mais comuns são frases alteradas, trechos omitidos em textos longos e fórmulas com sinal ou índice trocado. Uma fórmula com erro de LaTeX aparece em vermelho no site, mas uma fórmula errada que funciona aparece normalmente.
- **Formatos do artigo.** `.md`, `.txt`, `.docx`, `.odt` e `.tex` são adequados. Se a ferramenta não ler o formato, exporte o artigo do Word, do Google Docs ou do LibreOffice para `.md` ou `.txt`.

### Como usar

1. Copie o prompt do quadro abaixo.
2. Substitua o trecho entre colchetes pela referência ao artigo, conforme a ferramenta:
   - **Modelo no computador, com acesso a arquivos:** o caminho do arquivo, por exemplo `/home/ana/artigos/varejo.docx`;
   - **Ferramenta na web:** `o arquivo anexado a esta mensagem`, anexando o arquivo, ou o próprio texto do artigo, colado no lugar.
3. Envie em uma conversa nova. Se o artigo tem imagens, informe a ordem delas e a legenda de cada uma, caso o texto original não deixe isso claro.
4. Leia a resposta, que vem em quatro partes: o texto convertido, a tabela de imagens, os pontos de atenção e as sugestões.

````text
Você vai converter um artigo para o formato de Markdown aceito pelo site do Insper Consulting Club. A tarefa é SÓ de formatação.

ARTIGO A CONVERTER: [SUBSTITUIR ESTE TRECHO PELA REFERÊNCIA AO ARTIGO]

Se o artigo não tiver sido indicado ou não puder ser lido, avise e pare.

REGRA PRINCIPAL
Mantenha todas as palavras do texto exatamente como estão. Não reescreva, não resuma, não corrija estilo, não acrescente informações, não traduza e não "melhore" frases. Se achar um erro de português, de conteúdo ou de dados, não corrija: aponte nos pontos de atenção.

REGRAS DO FORMATO
1. Parágrafos separados por uma linha em branco.
2. O título do artigo NÃO entra no texto, porque o site o coloca sozinho. Se o texto começar pelo título, remova-o do texto e informe-o nos pontos de atenção.
3. Seções com "## Título da seção" e subseções com "### Título da subseção". Não use "#" (nível 1) nem níveis abaixo de "###". Se o original tiver mais de dois níveis, use "##" e "###" para os dois primeiros e aponte nos pontos de atenção o que foi reduzido.
4. Negrito com **texto** e itálico com *texto*. Links como [texto](https://endereço). Citações com "> ". Mantenha os links do original.
5. Listas com "- " (marcadores) ou "1. " (numeradas), sempre com uma linha em branco antes da lista. Escreva um espaço depois do símbolo.
6. Tabelas no formato Markdown, com linha de cabeçalho e linha de traços:
   | Coluna A | Coluna B |
   |---|---|
   | valor | valor |
   Se a tabela original tiver células mescladas ou não couber nesse formato, não invente: aponte nos pontos de atenção.
7. Imagens e gráficos: substitua cada um, no ponto onde aparece, por uma linha sozinha com ![](imagem-N), onde N é o número em ordem de aparição (1, 2, 3...). A legenda NÃO fica no texto: ela vai para a tabela de imagens da resposta.
8. Fórmulas em LaTeX, SEMPRE com dois cifrões. No meio de uma frase: $$\frac{a}{b}$$ na mesma linha. Em destaque: uma linha com $$, a fórmula na linha seguinte e outra linha com $$. Nunca use o cifrão simples para fórmulas. O símbolo de reais em "R$ 10 mi" fica como está, sem alteração. Se não tiver certeza de uma fórmula, escreva sua melhor tentativa e aponte nos pontos de atenção.
9. Notas de rodapé não existem no site. Mantenha a marcação [1], [2] no ponto da nota e coloque o texto das notas em uma seção final "## Referências", em lista numerada. Aponte isso nos pontos de atenção.
10. Não use HTML, cores, tamanhos de fonte nem alinhamento.
11. Se o texto tiver um símbolo que o Markdown interpretaria por engano (por exemplo, um "*" ou um "#" no começo de uma linha que deveria aparecer como texto), coloque uma barra invertida antes: \* ou \#.
12. Se o original for um arquivo LaTeX (.tex), converta \section para "##" e \subsection para "###", \textbf e \emph para negrito e itálico, e os ambientes de lista e de tabela para Markdown. Fórmulas com $...$, \(...\), \[...\] ou equation passam a usar $$ como na regra 8. Cada \includegraphics segue a regra 7. Citações e notas (\cite, \footnote) seguem a regra 9. Ignore o preâmbulo (\documentclass, \usepackage etc.) e aponte nos pontos de atenção qualquer comando que não tenha equivalente.

FORMATO DA RESPOSTA
Responda exatamente nesta ordem, com estes títulos:

PARTE 1. TEXTO CONVERTIDO
O texto completo e inteiro, dentro de um único bloco de código, com todos os trechos, mesmo que seja longo.

PARTE 2. IMAGENS
Uma tabela com as colunas: Número | Onde aparece (frase antes) | Legenda do original. Se não houver imagens, escreva "Nenhuma".

PARTE 3. PONTOS DE ATENÇÃO
Lista do que mereceu decisão ou dúvida: título removido, níveis de seção reduzidos, tabelas problemáticas, fórmulas incertas, notas de rodapé movidas, trechos ambíguos, possíveis erros no original. Cada item indica o trecho. Se não houver, escreva "Nenhum".

PARTE 4. SUGESTÕES (o autor aprova ou reescreve)
- Resumo de duas ou três frases, usando apenas informações que estão no texto.
- Temas: de duas a cinco palavras-chave, separadas por vírgula.
- Slug: em letras minúsculas, sem acento nem espaço, com palavras separadas por hífen.
````

### Depois da conversão

A ferramenta entrega um rascunho. Antes de cadastrar o artigo:

1. **Compare com o original.** Percorra o texto convertido ao lado do original e confira se nenhuma frase foi alterada ou omitida. Comparar a quantidade de parágrafos, de seções e de itens de lista ajuda.
2. **Confira cada fórmula** contra o original, principalmente sinais, índices e expoentes.
3. **Leia os pontos de atenção** e resolva cada um com o autor, se necessário. O resumo sugerido é do autor: ele aprova ou reescreve.
4. Cadastre o texto e as imagens (a tabela da Parte 2 diz qual arquivo vai em qual número) e faça a revisão obrigatória de [Revisar antes de publicar](#revisar-antes-de-publicar).

---

## Revisar antes de publicar

O admin não tem pré-visualização. Um artigo com **Publicado** desmarcado só pode ser visto por quem edita no admin, como texto cru, e um artigo publicado fica visível para qualquer pessoa. **Quem publica deve revisar o artigo antes de publicá-lo**, de uma das duas formas abaixo.

### Visualizador de Markdown na internet

Serve para conferir a estrutura do texto: seções, listas, links, negrito e tabelas. Para muitos artigos, só com texto, isso basta. Ele **não** reproduz o site, e por isso:

- **Fórmulas.** O site só abre fórmula com `$$`, mas muitos visualizadores usam outra regra. Uns mostram o `$$...$$` como texto cru e outros tratam o `$` simples como fórmula, o que estraga trechos como "R$ 10 mi e R$ 20 mi". Nenhum dos dois mostra o que o site vai mostrar.
- **Imagens.** `![](imagem-1)` aparece como imagem quebrada, porque o número só é resolvido pelo site.
- **Visual.** Fonte, espaçamentos, largura do texto e tabelas são diferentes, e alguns visualizadores nem desenham tabelas.

Se o artigo tem fórmulas ou imagens, use o ambiente local.

### Ambiente local

Mostra o artigo exatamente como o site vai mostrar, com imagens e fórmulas. Exige o ambiente local no seu computador, que o [Guia do ambiente local](guia-ambiente-local.md) ensina a montar do zero, sem conhecimento técnico.

1. Atualize o projeto para a `main` e ligue o ambiente local, como explica o guia.
2. No admin local (http://localhost:8000/admin/), cadastre o artigo com **Publicado** marcado. O banco local é separado do de produção, então não há risco de publicar por engano.
3. Envie as imagens em **Imagens do artigo**. Elas ficam só no seu computador.
4. Abra http://localhost:5173/artigos e confira o card e a página do artigo.

O artigo precisa ser cadastrado de novo em produção: o texto se copia e se cola, e as imagens são enviadas outra vez.

Depois de publicar em produção, abra a página no site e confira de novo. O ambiente local não reproduz o Cloudinary nem a hospedagem.

### Lista de conferência

- [ ] Título, autores, resumo e data preenchidos.
- [ ] Slug sem acento, sem espaço e sem letra maiúscula (ou em branco).
- [ ] Cada parágrafo separado por uma linha em branco.
- [ ] Seções com `##` e subseções com `###`, e um espaço depois dos símbolos.
- [ ] Listas com uma linha em branco antes.
- [ ] Cada `![](imagem-N)` aponta para um número que existe em **Imagens do artigo**, e cada imagem tem legenda.
- [ ] Fórmulas com `$$`, sem trechos em vermelho.
- [ ] Links testados.
- [ ] Imagem de capa na proporção horizontal (16:9).
- [ ] Ortografia revisada.

---

## Publicar, editar e despublicar

- **Publicar:** marque **Publicado** e salve. Dá para marcar direto na lista de Artigos, na coluna **Publicado**.
- **Editar:** abra o artigo, altere e salve. A mudança aparece ao recarregar a página.
- **Despublicar:** desmarque **Publicado**. O artigo sai do site e continua guardado.
- **Apagar:** use só para artigos criados por engano, porque é definitivo. Na dúvida, despublique.
- **Reordenar:** os artigos aparecem do mais recente para o mais antigo, pela **Data de publicação**. A **Ordem de exibição** só desempata datas iguais.

---

## Problemas comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| O artigo não aparece no site | **Publicado** está desmarcado | Marcar **Publicado** e salvar |
| A página do artigo dá "Artigo não encontrado" | O link usa um slug antigo, ou o artigo foi despublicado | Conferir o slug atual e o campo **Publicado** |
| O artigo aparece no topo da lista, antes dos mais novos | A **Data de publicação** está vazia | Preencher a data |
| Aparecem asteriscos ou cerquilhas no texto | Faltou o espaço depois do símbolo, ou o símbolo está colado ao texto | Revisar a marcação (por exemplo, `## Título`) |
| Uma lista aparece como um parágrafo corrido | Falta uma linha em branco antes da lista | Deixar uma linha em branco antes do primeiro item |
| Dois parágrafos aparecem juntos | Há só uma quebra de linha entre eles | Deixar uma linha em branco entre eles |
| A imagem não aparece | O número do texto é diferente do cadastrado, ou a linha de imagem tem outro texto junto | Conferir `![](imagem-N)` em uma linha sozinha e o número em **Imagens do artigo** |
| O admin recusa o slug | Slug repetido, ou com acento ou espaço | Escolher outro slug no formato `palavras-separadas-por-hifen` |
| A fórmula aparece em vermelho | Erro de digitação no LaTeX | Conferir chaves `{}` e barras invertidas |
| Aparece `R$` como parte de uma fórmula | Foi usado `$$` por engano | Usar apenas um cifrão em valores em reais |
| O texto copiado do Docs trouxe um bloco enorme de código | São as imagens do Docs | Apagar o bloco e usar **Imagens do artigo** |
| O texto aparece colado, sem formatação | Marcação HTML foi colada no texto | O site mostra HTML como texto comum. Reescreva em Markdown |

Em caso de dúvida técnica (erro ao salvar, página que não carrega), procure o responsável técnico do site.

---

## Exemplo completo

Copie e cole em **Texto do artigo** para ver o resultado. Para a imagem aparecer, cadastre uma imagem de número 1 em **Imagens do artigo**.

```
## Contexto

O varejo brasileiro passou por uma transformação relevante na última década. Este artigo analisa **três movimentos** que explicam essa mudança.

## Principais fatores

Os movimentos mais importantes foram:

- digitalização dos canais de venda;
- consolidação de grandes redes;
- mudança no perfil do consumidor.

![](imagem-1)

## Resultados

O indicador de rentabilidade é dado por $$\frac{EBITDA}{Receita}$$ e variou entre as empresas analisadas:

| Empresa | Receita (R$ mi) | Margem |
|---|---|---|
| Empresa A | 120 | 12% |
| Empresa B | 95 | 9% |

> "A margem é o que separa o crescimento sustentável do crescimento caro."

## Referências

Os dados vêm do [relatório anual da Empresa A](https://exemplo.com/relatorio).
```
