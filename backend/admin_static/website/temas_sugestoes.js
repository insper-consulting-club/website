/*
 * Campo "Temas" do artigo (ver CampoDeTemas em website/admin.py): temas separados por vírgula.
 * Enquanto se digita o tema atual (o trecho depois da última vírgula), sugere os temas já usados em outros artigos,
 * sem contar acento nem maiúscula. Escolher um troca o trecho digitado pelo tema. Um tema novo é só digitado.
 */
(function () {
  "use strict";
  if (window.__temasSugestoes) return;
  window.__temasSugestoes = true;

  var CLASSE = "temas-sugestoes__input";
  var lista = null;
  var campo = null;
  var opcoes = [];
  var indice = 0;

  function normaliza(texto) {
    return (texto || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
  }

  function ehCampo(alvo) {
    return alvo && alvo.classList && alvo.classList.contains(CLASSE);
  }

  // O tema que está sendo digitado: do começo do trecho (depois da vírgula anterior) até o cursor.
  function trechoAtual(input) {
    var fim = input.selectionStart;
    var ini = input.value.lastIndexOf(",", fim - 1) + 1;
    return { ini: ini, fim: fim, texto: input.value.slice(ini, fim) };
  }

  function sugestoes(input) {
    var busca = normaliza(trechoAtual(input).texto);
    if (!busca) return [];
    var temas = [];
    try {
      temas = JSON.parse(input.dataset.temas || "[]");
    } catch (erro) {
      temas = [];
    }
    var usados = input.value.split(",").map(normaliza);
    return temas
      .filter(function (t) { return normaliza(t).indexOf(busca) !== -1 && usados.filter(function (u) { return u === normaliza(t); }).length === 0; })
      .slice(0, 8);
  }

  function fecha() {
    if (lista) {
      lista.remove();
      lista = null;
    }
    campo = null;
    opcoes = [];
  }

  function posiciona() {
    if (!lista || !campo) return;
    var caixa = campo.getBoundingClientRect();
    lista.style.left = caixa.left + "px";
    lista.style.top = caixa.bottom + 2 + "px";
    lista.style.minWidth = caixa.width / 2 + "px";
  }

  function desenha() {
    lista.textContent = "";
    opcoes.forEach(function (tema, i) {
      var item = document.createElement("div");
      item.className = "autor-combobox__opcao" + (i === indice ? " autor-combobox__opcao--ativa" : "");
      item.setAttribute("role", "option");
      item.dataset.indice = String(i);
      item.textContent = tema;
      lista.appendChild(item);
    });
  }

  function abre(input) {
    var novas = sugestoes(input);
    if (!novas.length) {
      fecha();
      return;
    }
    campo = input;
    opcoes = novas;
    indice = 0;
    if (!lista) {
      lista = document.createElement("div");
      lista.className = "autor-combobox__lista";
      lista.setAttribute("role", "listbox");
      // mousedown: escolher sem tirar o foco do campo.
      lista.addEventListener("mousedown", function (evento) {
        evento.preventDefault();
        var item = evento.target.closest(".autor-combobox__opcao");
        if (item) escolhe(Number(item.dataset.indice));
      });
      document.body.appendChild(lista);
    }
    desenha();
    posiciona();
  }

  function escolhe(i) {
    var tema = opcoes[i];
    var input = campo;
    if (!tema || !input) return;
    var t = trechoAtual(input);
    var antes = input.value.slice(0, t.ini);
    var depois = input.value.slice(t.fim);
    var espaco = antes === "" || /\s$/.test(antes) ? "" : " ";
    var texto = espaco + tema + (depois.trim() === "" ? ", " : "");
    input.value = antes + texto + (depois.trim() === "" ? "" : depois);
    var cursor = (antes + texto).length;
    input.setSelectionRange(cursor, cursor);
    input.dispatchEvent(new Event("input", { bubbles: true }));
    fecha();
  }

  document.addEventListener("input", function (evento) {
    if (ehCampo(evento.target)) abre(evento.target);
  });

  document.addEventListener("focusout", function (evento) {
    if (ehCampo(evento.target)) fecha();
  });

  document.addEventListener("keydown", function (evento) {
    var input = evento.target;
    if (!ehCampo(input) || !lista) return;
    if (evento.key === "ArrowDown" || evento.key === "ArrowUp") {
      evento.preventDefault();
      indice = (indice + (evento.key === "ArrowDown" ? 1 : -1) + opcoes.length) % opcoes.length;
      desenha();
    } else if (evento.key === "Enter") {
      evento.preventDefault(); // não envia o formulário
      escolhe(indice);
    } else if (evento.key === "Escape") {
      evento.preventDefault();
      evento.stopPropagation();
      fecha();
    }
  });

  window.addEventListener("resize", posiciona);
  window.addEventListener("scroll", posiciona, true);
})();
