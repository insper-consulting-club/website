# Guia de artigos

Este guia é para quem escreve e quem publica artigos no site do ICC. Ele não exige conhecimento técnico. Para o restante da área administrativa (membros, parceiros, processo seletivo etc.), veja o [guia da área administrativa](guia-admin.md).

Há dois papéis, que podem ser da mesma pessoa:

- **Quem escreve** entrega o texto, as imagens e os dados do artigo.
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

1. **Escreva** o artigo no formato que preferir, inclusive direto em Markdown (`.md`). Use os estilos de título do editor para seções, subseções e subsubseções (no Google Docs, `Ctrl+Alt+2`, `Ctrl+Alt+3` e `Ctrl+Alt+4`). Deixe as imagens em arquivos separados.
2. **Converta** o texto para Markdown (ver [Converter o texto para Markdown](#converter-o-texto-para-markdown)).
3. **Revise** o artigo como ele ficará no site (ver [Revisar antes de publicar](#revisar-antes-de-publicar)).
4. No admin, abra **Artigos > Adicionar artigo** e preencha os campos (ver [Campo a campo](#campo-a-campo)).
5. **Cole** o texto convertido em **Texto do artigo**.
6. **Envie as imagens** em **Imagens do artigo** e coloque-as no texto pelo número (ver [Imagens no meio do texto](#imagens-no-meio-do-texto)).
7. **Salve** com **Publicado** desmarcado. O artigo fica guardado como rascunho e não aparece no site.
8. Marque **Publicado**, salve e abra a página no site para conferir. Se algo estiver errado, desmarque **Publicado** e corrija.

Dica: antes de abrir o admin, prepare numa ficha o título, os autores, os temas, o resumo, o slug, a data e a lista das imagens (número, arquivo e legenda), respeitando os limites de [Campo a campo](#campo-a-campo).

---

## Campo a campo

| Campo | Obrigatório | Limite | O que escrever |
| --- | --- | --- | --- |
| **Título** | Sim | 200 caracteres | O título do artigo |
| **Slug da URL** | Não | 200 caracteres | O trecho final do endereço, em letras minúsculas, sem acento nem espaço, com palavras separadas por hífen. Por exemplo, `analise-do-setor-de-varejo` gera `/artigos/analise-do-setor-de-varejo`. Deve ser único. Se ficar em branco, o endereço usa o número do artigo |
| **Autores** | Não | 300 caracteres | Nomes separados por vírgula, por exemplo `Ana Silva, João Souza`. O texto aparece igual no card, no topo da página e na citação |
| **Temas** | Não | 200 caracteres no total | Palavras-chave separadas por vírgula, por exemplo `Estratégia, Varejo`. Viram etiquetas no topo do artigo |
| **Resumo** | Sim | - | Duas ou três frases. Aparece no card da lista e no quadro "Resumo" do artigo |
| **Texto do artigo** | Não, mas é o conteúdo | - | O texto completo, em Markdown |
| **Link externo** | Não | 200 caracteres | Endereço de outra publicação do mesmo artigo (revista, LinkedIn ou um PDF em uma pasta do ICC com acesso "Qualquer pessoa com o link"). Cria o botão "Ver publicação original" |
| **Publicação** | Não | 200 caracteres | Nome da revista ou do evento, quando o artigo também saiu fora do site. Aparece no card |
| **Data de publicação** | Recomendado | - | A data que aparece no card e no topo do artigo. Preencha sempre: um artigo sem data pode aparecer no topo da lista, antes dos mais recentes |
| **Imagem de capa** | Não | Nome do arquivo: 100 caracteres | Imagem horizontal, de preferência na proporção 16:9 (por exemplo, 1600 por 900 pixels). No card ela é cortada nessa proporção, e na página aparece inteira |
| **Ordem de exibição** | Não | - | Só desempata artigos com a mesma data: o menor número aparece primeiro |
| **Publicado** | Começa desmarcado | - | Desmarcado, o artigo é rascunho e fica invisível no site |

**Licença das imagens.** Na capa e nas demais imagens, use só imagens de licença livre, como as do [Unsplash](https://unsplash.com/license), ou criadas pelo ICC, e cite o autor e a fonte no fim do artigo.

Dica sobre o slug: depois de compartilhar o link do artigo, evite mudar o slug, porque o link antigo deixa de funcionar. Use só letras minúsculas.

---

## Escrever o texto em Markdown

O texto do artigo é escrito em **Markdown**, um jeito simples de marcar a formatação com símbolos. O site converte os símbolos em títulos, listas, negrito e o resto. O título do artigo já aparece como título da página, então **comece as seções pelo nível `##`**.

### Referência rápida

| Para ter | Escreva |
|---|---|
| Parágrafo novo | uma linha em branco entre os parágrafos |
| Seção | `## Título da seção` |
| Subseção | `### Título da subseção` |
| Subsubseção | `#### Título da subsubseção` |
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

**Tabelas.** Uma linha de cabeçalho, uma linha de traços e uma linha por registro, com as colunas separadas por `|`. No celular, tabelas largas rolam na horizontal, então prefira poucas colunas.

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
- **Títulos de nível 1, 5 e 6** (`#`, `#####` e `######`). O texto tem três níveis de título, `##` a `####`, e o título do artigo é colocado pelo site.
- **Cores, tamanho de letra e alinhamento do texto.** O visual segue o padrão do site, igual em todos os artigos.
- **Notas de rodapé** (`[^1]`). Funcionam, mas saem sem o estilo do site, em uma lista simples no fim do texto. Prefira citar a fonte no próprio texto, com um link, ou em uma seção "Referências" no fim do artigo.

---

## Imagens no meio do texto

As imagens são cadastradas no mesmo formulário do artigo, sem precisar salvar antes.

1. Desça até **Imagens do artigo**. Em cada linha, preencha:
   - **Número:** 1, 2, 3, na ordem que você preferir. Cada número só pode ser usado uma vez no artigo;
   - **Imagem:** um arquivo JPG ou PNG (SVG é recusado), com nome de até 100 caracteres, de preferência com 1400 px ou mais de largura e até cerca de 2 MB. Textos e números dentro da imagem precisam ser legíveis no celular;
   - **Legenda:** o texto que aparece embaixo da imagem, com até 300 caracteres. Fonte e notas longas ficam melhor no texto do artigo.
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

As fórmulas são escritas em LaTeX, uma linguagem para matemática. Use sempre **dois cifrões** (`$$`).

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
| Multiplicação | `\times` ou `\cdot` |
| Vírgula decimal | `0{,}10` |
| Texto dentro da fórmula | `\text{receita líquida}` |

Em números dentro da fórmula, escreva a vírgula decimal entre chaves (`0{,}10`); sem elas, aparece um espaço depois da vírgula.

Se a fórmula tiver erro de digitação, ela aparece **em vermelho** no artigo e o resto do texto continua normal. Confira antes de publicar. A [lista de funções aceitas](https://katex.org/docs/supported.html) mostra tudo o que o site consegue desenhar; para algo fora dela, use uma imagem. Para aprender a escrever fórmulas em LaTeX, há o [guia de matemática do Wikibooks](https://en.wikibooks.org/wiki/LaTeX/Mathematics), em inglês.


---

## Converter o texto para Markdown

Quem escreve não precisa aprender Markdown. Um texto do Google Docs é convertido por quem publica:

1. Abra o texto no Google Docs.
2. Use **Arquivo > Fazer download > Markdown (.md)**.
3. Abra o arquivo `.md` em um editor de texto simples (Bloco de Notas, por exemplo), copie tudo e cole em **Texto do artigo**.

Depois da conversão, confira:

- **Títulos, listas, negritos, itálicos e links** costumam vir certos. Título 2, 3 e 4 viram `##`, `###` e `####`.
- **Imagens vêm quebradas.** Apague do texto o que aparecer no lugar delas (um trecho longo que começa com `![`) e use **Imagens do artigo**, como explicado acima.
- **Equações:** as inseridas pelo ambiente de equação do Google Docs saem em LaTeX no `.md`, mas não no formato do site. Troque os delimitadores por `$$...$$` (no meio da frase) ou por `$$` em linhas separadas (em destaque).
- **Tabelas** convertem melhor quando são simples. Confira o resultado.
- **Linhas em branco:** verifique se cada parágrafo está separado dos outros por uma linha em branco.

Outros formatos: `.docx` e `.odt` abrem no Google Docs, e um `.md` só precisa seguir as regras deste guia. Para `.tex`, `.txt` e textos longos com tabelas ou fórmulas, use a [Conversão com IA](#conversão-com-ia), no fim do guia.

---

## Revisar antes de publicar

O admin não tem pré-visualização. Um artigo com **Publicado** desmarcado só aparece para quem edita, como texto cru, e um artigo publicado fica visível para qualquer pessoa. **Quem publica deve revisar o artigo antes de publicá-lo**, de preferência no ambiente local.

### Ambiente local (recomendado)

Mostra o artigo exatamente como o site vai mostrar, com imagens e fórmulas. O [Guia do ambiente local](guia-ambiente-local.md) ensina a montá-lo do zero, sem conhecimento técnico.

1. Atualize o projeto para a `main` e ligue o ambiente local, como explica o guia.
2. No admin local (http://localhost:8000/admin/), cadastre o artigo com **Publicado** marcado. O banco local é separado do de produção, então não há risco de publicar por engano.
3. Envie as imagens em **Imagens do artigo**. Elas ficam só no seu computador.
4. Abra http://localhost:5173/artigos e confira o card e a página do artigo.

O artigo precisa ser cadastrado de novo em produção: o texto se copia e se cola, e as imagens são enviadas outra vez. Depois de publicar, abra a página no site e confira de novo.

### Visualizador de Markdown na internet

Serve só para conferir a estrutura de textos simples: seções, listas, links, negrito e tabelas. Ele **não** reproduz o site, e por isso:

- **Fórmulas.** O site só abre fórmula com `$$`, mas muitos visualizadores usam outra regra. Uns mostram o `$$...$$` como texto cru e outros tratam o `$` simples como fórmula, o que estraga trechos como "R$ 10 mi e R$ 20 mi".
- **Imagens.** `![](imagem-1)` aparece como imagem quebrada, porque o número só é resolvido pelo site.
- **Visual.** Fonte, espaçamentos, largura do texto e tabelas são diferentes, e alguns visualizadores nem desenham tabelas.

### Lista de conferência

- [ ] Título, autores, resumo e data preenchidos, dentro dos limites de caracteres (legenda de imagem: 300).
- [ ] Slug sem acento, sem espaço e sem letra maiúscula (ou em branco).
- [ ] Cada parágrafo separado por uma linha em branco.
- [ ] Títulos com `##`, `###` ou `####`, e um espaço depois dos símbolos.
- [ ] Listas com uma linha em branco antes.
- [ ] Cada `![](imagem-N)` aponta para um número que existe em **Imagens do artigo**, e cada imagem tem legenda.
- [ ] Fórmulas com `$$`, sem trechos em vermelho.
- [ ] Links testados.
- [ ] Imagem de capa na proporção horizontal (16:9), com licença livre e fonte citada.
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
```

---

## Conversão com IA

Uma ferramenta de IA conversacional pode fazer a parte mecânica da conversão: seções, listas, tabelas, fórmulas e marcadores de imagem. O uso é opcional e **não substitui a conferência**: quem publica continua responsável pelo que vai ao ar. O prompt abaixo resume as regras deste guia para a ferramenta aplicá-las.

<!-- Manutenção: ao mudar uma regra deste guia (fórmulas, níveis de título, imagens), atualize o prompt abaixo no mesmo PR. -->

### Antes de usar

- **Confidencialidade.** O texto do artigo é enviado a um serviço externo antes de ser publicado. Não use esse recurso em artigos com dados de clientes, informações não divulgadas de empresas ou qualquer conteúdo que o autor não queira fora do ICC. Na dúvida, pergunte ao autor.
- **Dados pessoais.** Remova do texto o que não for parte do artigo, como e-mails e telefones, antes de enviá-lo.
- **A ferramenta pode errar sem avisar:** frases alteradas, trechos omitidos e fórmulas com sinal ou índice trocado. Confira o resultado.

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
3. Seções com "## Título da seção", subseções com "### Título da subseção" e subsubseções com "#### Título da subsubseção". Não use "#" (nível 1) nem níveis abaixo de "####". Se o original começar os títulos em "#", desça todos os níveis em um. Se tiver mais de três níveis, use "##", "###" e "####" para os três primeiros e aponte nos pontos de atenção o que foi reduzido.
4. Negrito com **texto** e itálico com *texto*. Links como [texto](https://endereço). Citações com "> ". Mantenha os links do original.
5. Listas com "- " (marcadores) ou "1. " (numeradas), sempre com uma linha em branco antes da lista. Escreva um espaço depois do símbolo.
6. Tabelas no formato Markdown, com linha de cabeçalho e linha de traços:
   | Coluna A | Coluna B |
   |---|---|
   | valor | valor |
   Se a tabela original tiver células mescladas ou não couber nesse formato, não invente: aponte nos pontos de atenção.
7. Imagens e gráficos: substitua cada um, no ponto onde aparece, por uma linha sozinha com ![](imagem-N), onde N é o número em ordem de aparição (1, 2, 3...). A legenda NÃO fica no texto: ela vai para a tabela de imagens da resposta. O site aceita legendas de até 300 caracteres: se alguma passar disso, mantenha-a inteira e aponte nos pontos de atenção.
8. Fórmulas em LaTeX, SEMPRE com dois cifrões. No meio de uma frase: $$\frac{a}{b}$$ na mesma linha. Em destaque: uma linha com $$, a fórmula na linha seguinte e outra linha com $$. Nunca use o cifrão simples para fórmulas. Se o original já trouxer fórmulas em LaTeX com outros delimitadores (por exemplo, $...$ ou \(...\), como numa exportação do Google Docs), troque pelos de dois cifrões. O símbolo de reais em "R$ 10 mi" fica como está, sem alteração. Se não tiver certeza de uma fórmula, escreva sua melhor tentativa e aponte nos pontos de atenção.
9. Notas de rodapé não têm estilo próprio no site. Mantenha as notas como estão no original e aponte isso nos pontos de atenção.
10. Não use HTML, cores, tamanhos de fonte nem alinhamento.
11. Se o texto tiver um símbolo que o Markdown interpretaria por engano (por exemplo, um "*" ou um "#" no começo de uma linha que deveria aparecer como texto), coloque uma barra invertida antes: \* ou \#.
12. Se o original for um arquivo LaTeX (.tex), converta \section para "##", \subsection para "###" e \subsubsection para "####", \textbf e \emph para negrito e itálico, e os ambientes de lista e de tabela para Markdown. Fórmulas com $...$, \(...\), \[...\] ou equation passam a usar $$ como na regra 8. Cada \includegraphics segue a regra 7. Citações e notas (\cite, \footnote) seguem a regra 9. Ignore o preâmbulo (\documentclass, \usepackage etc.) e aponte nos pontos de atenção qualquer comando que não tenha equivalente.

FORMATO DA RESPOSTA
Responda exatamente nesta ordem, com estes títulos:

PARTE 1. TEXTO CONVERTIDO
O texto completo e inteiro, dentro de um único bloco de código, com todos os trechos, mesmo que seja longo.

PARTE 2. IMAGENS
Uma tabela com as colunas: Número | Onde aparece (frase antes) | Legenda do original | Caracteres da legenda. Se não houver imagens, escreva "Nenhuma".

PARTE 3. PONTOS DE ATENÇÃO
Lista do que mereceu decisão ou dúvida: título removido, níveis de seção reduzidos, tabelas problemáticas, fórmulas incertas, notas de rodapé movidas, legendas com mais de 300 caracteres, trechos ambíguos, possíveis erros no original. Cada item indica o trecho. Se não houver, escreva "Nenhum".

PARTE 4. SUGESTÕES (o autor aprova ou reescreve)
- Resumo de duas ou três frases, usando apenas informações que estão no texto.
- Temas: de duas a cinco palavras-chave, separadas por vírgula, com até 200 caracteres no total.
- Slug: em letras minúsculas, sem acento nem espaço, com palavras separadas por hífen e até 200 caracteres.
````

### Depois da conversão

A ferramenta entrega um rascunho. Antes de cadastrar o artigo:

1. **Compare com o original.** Percorra o texto convertido ao lado do original e confira se nenhuma frase foi alterada ou omitida. Comparar a quantidade de parágrafos, de seções e de itens de lista ajuda.
2. **Confira cada fórmula** contra o original, principalmente sinais, índices e expoentes.
3. **Confira os tamanhos.** Legenda de imagem com até 300 caracteres, título e slug com até 200, temas com até 200. A contagem da ferramenta pode errar, então conte de novo.
4. **Leia os pontos de atenção** e resolva cada um com o autor, se necessário. O resumo sugerido é do autor: ele aprova ou reescreve.
5. Cadastre o texto e as imagens (a tabela da Parte 2 diz qual arquivo vai em qual número) e faça a revisão obrigatória de [Revisar antes de publicar](#revisar-antes-de-publicar).
