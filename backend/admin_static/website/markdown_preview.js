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

  document.addEventListener("click", function (evento) {
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
