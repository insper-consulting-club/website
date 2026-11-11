/*
 * Avisa antes de sair de um formulário de edição com alterações não salvas (o texto de um artigo é longo, e um clique
 * errado em outro link perderia tudo). Compara os campos de agora com os de quando a página abriu; salvar não avisa.
 */
(function () {
  "use strict";

  function foto(form) {
    var partes = [];
    new FormData(form).forEach(function (valor, nome) {
      if (nome === "csrfmiddlewaretoken") return;
      partes.push(nome + "=" + (typeof valor === "string" ? valor : valor.name));
    });
    return partes.join("\n");
  }

  function inicia() {
    var form = document.querySelector('form[id$="_form"]');
    if (!form) return;
    var original = foto(form);
    var salvando = false;
    form.addEventListener("submit", function () { salvando = true; });
    window.addEventListener("beforeunload", function (evento) {
      if (salvando || foto(form) === original) return;
      evento.preventDefault();
      evento.returnValue = "";
    });
  }

  // Os widgets (calendário, campos de texto) acertam seus valores ao carregar: a foto sai depois disso.
  if (document.readyState === "complete") setTimeout(inicia, 300);
  else window.addEventListener("load", function () { setTimeout(inicia, 300); });
})();
