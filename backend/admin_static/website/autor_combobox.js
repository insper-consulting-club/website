/*
 * Campo de nome do autor do artigo (ver CampoDeAutor em website/admin.py).
 *
 * Ao digitar, aparece uma lista com os membros que combinam (sem contar acento nem maiúscula) e, no fim, a opção de
 * usar o texto como autor de fora. Escolher um membro grava o ID dele no campo oculto "Membro"; qualquer outro texto
 * deixa o campo oculto vazio. Embaixo do campo, uma linha diz em que estado o autor está.
 *
 * Os eventos ficam no document porque as linhas novas do formulário são criadas depois que a página carrega.
 * Sem JavaScript, o campo continua sendo um texto livre (autor de fora).
 */
(function () {
  "use strict";
  if (window.__autorCombobox) return;
  window.__autorCombobox = true;

  var CLASSE = "autor-combobox__input";
  var lista = null; // a lista aberta, uma só na página
  var campo = null; // o campo ao qual ela pertence
  var opcoes = [];
  var indice = 0;

  function normaliza(texto) {
    return (texto || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().trim();
  }

  function ehCampo(alvo) {
    return alvo && alvo.classList && alvo.classList.contains(CLASSE) && alvo.name.indexOf("__prefix__") === -1;
  }

  function membrosDe(input) {
    if (!input._membros) {
      try {
        input._membros = JSON.parse(input.dataset.membros || "[]");
      } catch (erro) {
        input._membros = [];
      }
    }
    return input._membros;
  }

  function ocultoDe(input) {
    return document.getElementById(input.id.replace(/name$/, "member"));
  }

  function iniciaCampo(input) {
    if (input._iniciado) return;
    input._iniciado = true;
    var oculto = ocultoDe(input);
    // O texto que corresponde ao membro já escolhido: se o editor mexer nele, o vínculo se desfaz.
    input._escolhido = oculto && oculto.value ? input.value : null;
    atualizaEstado(input);
  }

  function atualizaEstado(input) {
    var oculto = ocultoDe(input);
    var estado = input._estado;
    if (!estado) {
      estado = document.createElement("span");
      estado.className = "autor-combobox__estado";
      estado.setAttribute("aria-live", "polite");
      input.parentNode.insertBefore(estado, input.nextSibling);
      input._estado = estado;
    }
    var texto = input.value.trim();
    estado.classList.remove("autor-combobox__estado--fora", "autor-combobox__estado--membro");
    if (!texto) {
      estado.textContent = "";
    } else if (oculto && oculto.value) {
      var membro = membrosDe(input).filter(function (m) { return String(m.id) === oculto.value; })[0];
      estado.textContent = "Ligado ao perfil de " + (membro ? membro.rotulo : "um membro");
      estado.classList.add("autor-combobox__estado--membro");
    } else {
      estado.textContent = "Autor de fora: sem link para o perfil e fora do filtro por autor.";
      estado.classList.add("autor-combobox__estado--fora");
    }
  }

  function montaOpcoes(input) {
    var busca = normaliza(input.value);
    var achados = [];
    if (busca) {
      membrosDe(input).forEach(function (m) {
        var alvo = normaliza(m.nome);
        var posicao = alvo.indexOf(busca);
        if (posicao !== -1) achados.push({ membro: m, peso: posicao === 0 ? 0 : 1 });
      });
      achados.sort(function (a, b) { return a.peso - b.peso; });
    }
    var resultado = achados.map(function (a) { return { membro: a.membro }; });
    if (input.value.trim()) resultado.push({ livre: input.value.trim() });
    return resultado;
  }

  function fecha() {
    if (lista) {
      lista.remove();
      lista = null;
    }
    if (campo) campo.setAttribute("aria-expanded", "false");
    campo = null;
    opcoes = [];
  }

  function posiciona() {
    if (!lista || !campo) return;
    var caixa = campo.getBoundingClientRect();
    lista.style.left = caixa.left + "px";
    lista.style.top = caixa.bottom + 2 + "px";
    lista.style.minWidth = caixa.width + "px";
  }

  function desenha() {
    if (!lista) return;
    lista.textContent = "";
    opcoes.forEach(function (opcao, i) {
      var item = document.createElement("div");
      item.className = "autor-combobox__opcao" + (i === indice ? " autor-combobox__opcao--ativa" : "");
      item.setAttribute("role", "option");
      item.setAttribute("aria-selected", i === indice ? "true" : "false");
      item.id = "autor-opcao-" + i;
      item.dataset.indice = String(i);
      if (opcao.membro) {
        item.textContent = opcao.membro.rotulo;
        if (opcao.membro.ex) {
          var nota = document.createElement("small");
          nota.textContent = "ex-membro";
          item.appendChild(nota);
        }
      } else {
        item.classList.add("autor-combobox__opcao--fora");
        item.textContent = "Usar “" + opcao.livre + "” como autor de fora (sem perfil)";
      }
      lista.appendChild(item);
    });
    campo.setAttribute("aria-activedescendant", "autor-opcao-" + indice);
  }

  function abre(input) {
    var novas = montaOpcoes(input);
    if (!novas.length) {
      fecha();
      return;
    }
    if (campo !== input) fecha();
    campo = input;
    opcoes = novas;
    indice = 0;
    if (!lista) {
      lista = document.createElement("div");
      lista.className = "autor-combobox__lista";
      lista.setAttribute("role", "listbox");
      lista.id = "autor-lista";
      // mousedown: escolher sem tirar o foco do campo, que fecharia a lista antes do clique.
      lista.addEventListener("mousedown", function (evento) {
        evento.preventDefault();
        var item = evento.target.closest(".autor-combobox__opcao");
        if (item) escolhe(Number(item.dataset.indice));
      });
      document.body.appendChild(lista);
    }
    campo.setAttribute("aria-expanded", "true");
    campo.setAttribute("aria-controls", "autor-lista");
    desenha();
    posiciona();
  }

  function escolhe(i) {
    var opcao = opcoes[i];
    var input = campo;
    if (!opcao || !input) return;
    var oculto = ocultoDe(input);
    if (opcao.membro) {
      input.value = opcao.membro.nome;
      input._escolhido = opcao.membro.nome;
      if (oculto) oculto.value = String(opcao.membro.id);
    } else {
      input._escolhido = null;
      if (oculto) oculto.value = "";
    }
    atualizaEstado(input);
    fecha();
  }

  document.addEventListener("input", function (evento) {
    var input = evento.target;
    if (!ehCampo(input)) return;
    iniciaCampo(input);
    var oculto = ocultoDe(input);
    // Mexeu no texto depois de escolher um membro: deixa de ser aquele membro.
    if (oculto && oculto.value && input.value !== input._escolhido) oculto.value = "";
    atualizaEstado(input);
    abre(input);
  });

  document.addEventListener("focusin", function (evento) {
    if (ehCampo(evento.target)) iniciaCampo(evento.target);
  });

  document.addEventListener("focusout", function (evento) {
    if (ehCampo(evento.target)) fecha();
  });

  document.addEventListener("keydown", function (evento) {
    var input = evento.target;
    if (!ehCampo(input)) return;
    if (evento.key === "ArrowDown" || evento.key === "ArrowUp") {
      evento.preventDefault();
      if (!lista) {
        abre(input);
        return;
      }
      indice = (indice + (evento.key === "ArrowDown" ? 1 : -1) + opcoes.length) % opcoes.length;
      desenha();
    } else if (evento.key === "Enter" && lista) {
      evento.preventDefault(); // não envia o formulário
      escolhe(indice);
    } else if (evento.key === "Escape" && lista) {
      evento.preventDefault();
      evento.stopPropagation();
      fecha();
    }
  });

  window.addEventListener("resize", posiciona);
  window.addEventListener("scroll", posiciona, true);

  function iniciaTodos() {
    document.querySelectorAll("." + CLASSE).forEach(function (input) {
      if (ehCampo(input)) iniciaCampo(input);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciaTodos);
  else iniciaTodos();
})();
