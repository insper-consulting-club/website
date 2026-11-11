/*
 * Prévia de textos em Markdown no admin.
 *
 * Cada campo com prévia (ver website/widgets.py) tem um botão "Mostrar prévia".
 * Ao abrir, a página /previa do site é carregada num iframe e recebe o texto por
 * postMessage, então o resultado é desenhado pelos mesmos componentes e estilos
 * do site publicado. Os eventos ficam no document porque os formulários dentro
 * de um registro (blocos de programa) são criados depois que a página carrega.
 */
(function () {
  "use strict";
  if (window.__previaMarkdown) return;
  window.__previaMarkdown = true;

  var ESTILO =
    ".md-previa{margin-top:.5rem}" +
    ".md-previa__botao{cursor:pointer;background:transparent;color:inherit;border:1px solid rgba(127,127,127,.5);border-radius:6px;padding:.25rem .75rem;font-size:.875rem}" +
    ".md-previa__botao:hover{border-color:currentColor}" +
    ".md-previa__quadro{display:block;width:100%;height:520px;margin-top:.5rem;border:1px solid rgba(127,127,127,.4);border-radius:6px;background:#fff;resize:vertical}" +
    ".md-previa__nota{margin-top:.25rem;font-size:.75rem;opacity:.7}";
  var estilo = document.createElement("style");
  estilo.textContent = ESTILO;
  document.head.appendChild(estilo);

  function campo(previa) {
    var caixa = previa.closest(".md-campo");
    return caixa ? caixa.querySelector("textarea") : null;
  }

  function enviar(previa) {
    var quadro = previa.querySelector("iframe");
    var texto = campo(previa);
    if (!quadro || !quadro.contentWindow || !texto) return;
    var imagens = [];
    try {
      imagens = JSON.parse(previa.dataset.imagens || "[]");
    } catch (erro) {
      imagens = [];
    }
    var origem = new URL(previa.dataset.url, window.location.href).origin;
    quadro.contentWindow.postMessage(
      { tipo: "markdown", texto: texto.value, modo: previa.dataset.modo, imagens: imagens },
      origem
    );
  }

  // ---- Barra de formatação e inserção de imagens ----

  // Troca o trecho [ini, fim) por "texto" sem perder o desfazer (Ctrl+Z) do navegador, e avisa a prévia.
  function troca(area, ini, fim, texto, selIni, selFim) {
    area.focus();
    area.setSelectionRange(ini, fim);
    var feito = false;
    try {
      feito = document.execCommand("insertText", false, texto);
    } catch (erro) {
      feito = false;
    }
    if (!feito) {
      area.setRangeText(texto, ini, fim, "end");
      area.dispatchEvent(new Event("input", { bubbles: true }));
    }
    area.setSelectionRange(selIni, selFim);
  }

  // Marcações que valem para linhas inteiras: o que já existe no começo da linha (tira), o que vai no lugar (poe) e
  // como saber que a linha já está assim (igual), para o mesmo botão desfazer a marcação.
  var POR_LINHA = {
    secao: { tira: /^#{1,6}\s+/, igual: /^## (?!#)/, poe: function () { return "## "; } },
    subsecao: { tira: /^#{1,6}\s+/, igual: /^### (?!#)/, poe: function () { return "### "; } },
    subsubsecao: { tira: /^#{1,6}\s+/, igual: /^#### (?!#)/, poe: function () { return "#### "; } },
    lista: { tira: /^(?:[-*+]|\d+\.)\s+/, igual: /^[-*+]\s+/, poe: function () { return "- "; } },
    numerada: { tira: /^(?:[-*+]|\d+\.)\s+/, igual: /^\d+\.\s+/, poe: function (n) { return n + ". "; } },
    citacao: { tira: /^>\s?/, igual: /^>\s?/, poe: function () { return "> "; } }
  };

  function formata(area, acao) {
    var v = area.value, ini = area.selectionStart, fim = area.selectionEnd, sel = v.slice(ini, fim);
    if (acao === "negrito" || acao === "italico") {
      var marca = acao === "negrito" ? "**" : "*";
      var miolo = sel || (acao === "negrito" ? "negrito" : "itálico");
      troca(area, ini, fim, marca + miolo + marca, ini + marca.length, ini + marca.length + miolo.length);
    } else if (acao === "codigo") {
      var codigo = sel || "código";
      troca(area, ini, fim, "`" + codigo + "`", ini + 1, ini + 1 + codigo.length);
    } else if (acao === "bloco") {
      // Bloco de várias linhas: três crases sozinhas em cada ponta. A seleção, se houver, vira o conteúdo.
      var conteudo = sel || "código";
      var comSelecao = area._tocado && sel;
      insereBloco(area, "```\n" + conteudo + "\n```", [4, 4 + conteudo.length], comSelecao ? fim : undefined);
    } else if (acao === "divisoria") {
      insereBloco(area, "---");
    } else if (acao === "formula") {
      var formula = sel || "x^2";
      troca(area, ini, fim, "$$" + formula + "$$", ini + 2, ini + 2 + formula.length);
    } else if (acao === "link") {
      var texto = sel || "texto do link";
      troca(area, ini, fim, "[" + texto + "](https://)", ini + texto.length + 3, ini + texto.length + 11);
    } else if (POR_LINHA[acao]) {
      // Vale para as linhas inteiras que a seleção toca; linhas em branco ficam como estão.
      var regra = POR_LINHA[acao];
      var comeco = v.lastIndexOf("\n", ini - 1) + 1;
      var fimLinha = v.indexOf("\n", fim);
      if (fimLinha === -1) fimLinha = v.length;
      var linhas = v.slice(comeco, fimLinha).split("\n");
      var cheias = linhas.filter(function (l) { return l.trim() !== ""; });
      var jaEsta = cheias.length > 0 && cheias.every(function (l) { return regra.igual.test(l); });
      var numero = 0;
      var novas = linhas.map(function (l) {
        if (l.trim() === "") return l;
        var limpa = l.replace(regra.tira, "");
        if (jaEsta) return limpa;
        numero += 1;
        return regra.poe(numero) + limpa;
      }).join("\n");
      troca(area, comeco, fimLinha, novas, comeco, comeco + novas.length);
    }
  }

  // Tela cheia: o campo (barra, texto e prévia) ocupa a janela. O restante da página não rola enquanto isso.
  function alternaTelaCheia(caixa, ligar) {
    var botao = caixa.querySelector('[data-md="tela"]');
    var ativa = typeof ligar === "boolean" ? ligar : !caixa.classList.contains("md-campo--tela-cheia");
    caixa.classList.toggle("md-campo--tela-cheia", ativa);
    document.documentElement.classList.toggle("md-sem-rolagem", ativa);
    botao.setAttribute("aria-pressed", String(ativa));
    botao.textContent = ativa ? "Sair da tela cheia" : "Tela cheia";
    var area = caixa.querySelector("textarea");
    if (area) area.focus();
  }

  // Tabela: um quadro pergunta quantas colunas e linhas; a primeira linha é o cabeçalho.
  function limita(campo, padrao) {
    var n = parseInt(campo.value, 10);
    if (isNaN(n)) n = padrao;
    return Math.max(Number(campo.min), Math.min(Number(campo.max), n));
  }

  function insereTabela(caixa) {
    var area = caixa.querySelector("textarea");
    var quadro = caixa.querySelector(".md-tabela");
    if (!area || !quadro) return;
    var colunas = limita(quadro.querySelector(".md-tabela__colunas"), 2);
    var linhas = limita(quadro.querySelector(".md-tabela__linhas"), 2);
    var repete = function (texto) { return "| " + new Array(colunas + 1).join(texto + " | ").trim(); };
    var cabecalho = [];
    for (var i = 1; i <= colunas; i++) cabecalho.push("Coluna " + i);
    var corpo = [];
    for (var j = 0; j < linhas; j++) corpo.push(repete("Valor"));
    var tabela = ["| " + cabecalho.join(" | ") + " |", "|" + new Array(colunas + 1).join("---|")].concat(corpo).join("\n");
    insereBloco(area, tabela, [2, 10]);
    quadro.hidden = true;
    caixa.querySelector('[data-md="tabela"]').setAttribute("aria-expanded", "false");
  }

  document.addEventListener("keydown", function (evento) {
    if (evento.key !== "Enter" || !evento.target.closest || !evento.target.closest(".md-tabela")) return;
    evento.preventDefault(); // não envia o formulário
    insereTabela(evento.target.closest(".md-campo"));
  });

  // Fecha os quadros abertos (tabela, imagens), menos o que contém "exceto".
  function fechaQuadros(exceto) {
    document.querySelectorAll(".md-tabela:not([hidden]), .md-imagens:not([hidden])").forEach(function (quadro) {
      if (quadro === exceto) return;
      quadro.hidden = true;
      var tipo = quadro.classList.contains("md-tabela") ? "tabela" : "imagem";
      var botao = quadro.closest(".md-barra").querySelector('[data-md="' + tipo + '"]');
      if (botao) botao.setAttribute("aria-expanded", "false");
    });
  }

  document.addEventListener("mousedown", function (evento) {
    if (evento.target.closest(".md-tabela, .md-imagens, [data-md=\"tabela\"], [data-md=\"imagem\"]")) return;
    fechaQuadros();
  });

  // Imagens do artigo já salvas: cada uma é um botão que insere ![](imagem-N) no texto. As que o texto já usa são marcadas.
  function desenhaImagens(quadro, area) {
    var imagens = [];
    try {
      imagens = JSON.parse(quadro.dataset.imagens || "[]");
    } catch (erro) {
      imagens = [];
    }
    quadro.textContent = "";
    if (!imagens.length) {
      var aviso = document.createElement("p");
      aviso.className = "md-imagens__aviso";
      aviso.textContent = "Nenhuma imagem salva neste artigo. Envie as imagens na aba “Imagens do artigo” e salve: elas aparecem aqui.";
      quadro.appendChild(aviso);
      return;
    }
    var usadas = {};
    var achado;
    var padrao = /!\[[^\]]*\]\(imagem-(\d+)\)/g;
    while ((achado = padrao.exec(area.value)) !== null) usadas[achado[1]] = true;
    imagens.forEach(function (img) {
      var botao = document.createElement("button");
      botao.type = "button";
      botao.className = "md-imagens__item";
      botao.dataset.numero = String(img.number);
      var miniatura = document.createElement("img");
      miniatura.src = img.image_url;
      miniatura.alt = "";
      var texto = document.createElement("span");
      var titulo = document.createElement("strong");
      titulo.textContent = "Imagem " + img.number;
      texto.appendChild(titulo);
      if (img.caption) texto.appendChild(document.createTextNode(" " + img.caption));
      var estado = document.createElement("small");
      estado.textContent = usadas[String(img.number)] ? "já usada no texto" : "ainda não usada";
      texto.appendChild(estado);
      botao.appendChild(miniatura);
      botao.appendChild(texto);
      quadro.appendChild(botao);
    });
  }

  document.addEventListener("click", function (evento) {
    var item = evento.target.closest(".md-imagens__item");
    if (!item) return;
    var caixa = item.closest(".md-campo");
    var area = caixa.querySelector("textarea");
    insereBloco(area, "![](imagem-" + item.dataset.numero + ")");
    fechaQuadros();
  });

  // Salvar sem sair da tela cheia: usa o botão "Salvar e continuar editando" do formulário e, quando a página volta,
  // reabre a tela cheia no mesmo ponto do texto (a menos que haja erro no formulário, que o editor precisa ver).
  var CHAVE_TELA = "md-tela-cheia";

  function salvaEContinua(caixa) {
    var area = caixa.querySelector("textarea");
    var enviar = document.querySelector('[name="_continue"]');
    if (!area || !enviar) return;
    // Um campo obrigatório vazio fica escondido atrás da tela cheia: sai dela para o navegador apontá-lo.
    var formulario = enviar.form;
    if (formulario && !formulario.checkValidity()) {
      alternaTelaCheia(caixa, false);
      formulario.reportValidity();
      return;
    }
    try {
      sessionStorage.setItem(CHAVE_TELA, JSON.stringify({ id: area.id, pos: area.selectionStart, rolagem: area.scrollTop }));
    } catch (erro) { /* sem armazenamento: só não reabre a tela cheia */ }
    enviar.click();
  }

  function reabreTelaCheia() {
    var guardado = null;
    try {
      guardado = JSON.parse(sessionStorage.getItem(CHAVE_TELA) || "null");
      sessionStorage.removeItem(CHAVE_TELA);
    } catch (erro) {
      guardado = null;
    }
    if (!guardado || document.querySelector(".errorlist, .errornote")) return;
    var area = document.getElementById(guardado.id);
    var caixa = area && area.closest(".md-campo");
    if (!caixa) return;
    alternaTelaCheia(caixa, true);
    area.setSelectionRange(guardado.pos, guardado.pos);
    area.scrollTop = guardado.rolagem;
    var botao = caixa.querySelector('[data-md="salvar"]');
    botao.textContent = "Salvo";
    setTimeout(function () { botao.textContent = "Salvar e continuar"; }, 2500);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", reabreTelaCheia);
  else reabreTelaCheia();

  // Um campo que ainda não recebeu o cursor não tem posição escolhida: nesse caso a imagem vai para o fim do texto.
  document.addEventListener("focusin", function (evento) {
    if (evento.target.matches && evento.target.matches(".md-campo textarea")) evento.target._tocado = true;
  });

  // Insere um bloco (imagem, tabela, linha divisória) num parágrafo só dele, com uma linha em branco de cada lado.
  // Sem cursor escolhido, vai para o fim do texto. "marca" é o trecho [início, fim) do bloco a deixar selecionado.
  function insereBloco(area, trecho, marca, ate) {
    var posicao = area._tocado ? area.selectionStart : area.value.length;
    var antes = area.value.slice(0, posicao), depois = area.value.slice(typeof ate === "number" ? ate : posicao);
    var comeco = antes === "" || /\n\n$/.test(antes) ? "" : /\n$/.test(antes) ? "\n" : "\n\n";
    var fim = depois === "" || /^\n\n/.test(depois) ? "" : /^\n/.test(depois) ? "\n" : "\n\n";
    var base = posicao + comeco.length;
    var selecao = marca ? [base + marca[0], base + marca[1]] : [base, base + trecho.length];
    troca(area, posicao, typeof ate === "number" ? ate : posicao, comeco + trecho + fim, selecao[0], selecao[1]);
  }

  document.addEventListener("click", function (evento) {
    var formato = evento.target.closest(".md-barra button");
    if (formato) {
      if (formato.dataset.md === "tela") {
        alternaTelaCheia(formato.closest(".md-campo"));
        return;
      }
      if (formato.dataset.md === "tabela" || formato.dataset.md === "imagem") {
        var barra = formato.closest(".md-barra");
        var quadro = barra.querySelector(formato.dataset.md === "tabela" ? ".md-tabela" : ".md-imagens");
        var abrir = quadro.hidden;
        fechaQuadros();
        quadro.hidden = !abrir;
        formato.setAttribute("aria-expanded", String(abrir));
        if (abrir && formato.dataset.md === "imagem") desenhaImagens(quadro, formato.closest(".md-campo").querySelector("textarea"));
        return;
      }
      if (formato.dataset.md === "salvar") {
        salvaEContinua(formato.closest(".md-campo"));
        return;
      }
      if (formato.dataset.md === "tabela-inserir") {
        insereTabela(formato.closest(".md-campo"));
        return;
      }
      var campo = formato.closest(".md-campo").querySelector("textarea");
      if (campo) formata(campo, formato.dataset.md);
      return;
    }
    var botao = evento.target.closest(".md-previa__botao");
    if (!botao) return;
    var previa = botao.closest(".md-previa");
    var caixa = previa.querySelector(".md-previa__caixa");
    var aberta = !caixa.hidden;
    caixa.hidden = aberta;
    botao.setAttribute("aria-expanded", String(!aberta));
    botao.textContent = aberta ? "Mostrar prévia" : "Ocultar prévia";
    if (!aberta) {
      var quadro = previa.querySelector("iframe");
      if (!quadro.getAttribute("src")) {
        quadro.addEventListener("load", function () { enviar(previa); });
        quadro.setAttribute("src", previa.dataset.url);
      } else {
        enviar(previa);
      }
    }
  });

  var espera = null;
  document.addEventListener("input", function (evento) {
    var previa = evento.target.closest && evento.target.closest(".md-campo") &&
      evento.target.closest(".md-campo").querySelector(".md-previa");
    if (!previa || previa.querySelector(".md-previa__caixa").hidden) return;
    clearTimeout(espera);
    espera = setTimeout(function () { enviar(previa); }, 250);
  });

  // O site avisa quando termina de carregar; só então o texto é enviado.
  window.addEventListener("message", function (evento) {
    if (!evento.data || evento.data.tipo !== "previa-pronta") return;
    document.querySelectorAll(".md-previa").forEach(function (previa) {
      var quadro = previa.querySelector("iframe");
      if (quadro && quadro.contentWindow === evento.source) enviar(previa);
    });
  });
})();
