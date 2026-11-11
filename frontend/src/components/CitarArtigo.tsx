import { useRef, useState, type KeyboardEvent } from "react"
import type { ArticleCitation } from "../types"
import useTextos from "../hooks/useTextos"
import { CheckIcon, CloseIcon, CopyIcon } from "./Icons"

// O backend entrega as citações com estes marcadores no lugar da data de acesso, que é a de quem copia.
const ISO = "__DATA_DE_ACESSO__"
const ABNT = "__DATA_DE_ACESSO_ABNT__"
const RIS = "__DATA_DE_ACESSO_RIS__"
const MESES_ABNT = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]

function trocaDatas(texto: string, hoje: Date) {
  const ano = hoje.getFullYear()
  const mes = String(hoje.getMonth() + 1).padStart(2, "0")
  const dia = String(hoje.getDate()).padStart(2, "0")
  return texto
    .split(ABNT).join(`${hoje.getDate()} ${MESES_ABNT[hoje.getMonth()]} ${ano}`)
    .split(RIS).join(`${ano}/${mes}/${dia}`)
    .split(ISO).join(`${ano}-${mes}-${dia}`)
}

const escapaHtml = (texto: string) =>
  texto.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

// A citação em texto como HTML, para colar no Word ou no Google Docs com o negrito e o itálico.
function emHtml(citacao: ArticleCitation, hoje: Date) {
  return (citacao.partes ?? [])
    .map(({ t, e }) => {
      const texto = escapaHtml(trocaDatas(t, hoje))
      return e === "b" ? `<strong>${texto}</strong>` : e === "i" ? `<em>${texto}</em>` : texto
    })
    .join("")
}

type Props = { citacoes: ArticleCitation[] }

// Botão "Citar": abre uma janela com uma aba por forma de citação (ABNT, APA, BibTeX...) e o botão de copiar,
// como nos sites de periódicos. A janela é um <dialog> nativo, que já cuida do foco e do ESC.
export default function CitarArtigo({ citacoes }: Props) {
  const t = useTextos()
  const janela = useRef<HTMLDialogElement>(null)
  const [ativa, setAtiva] = useState(citacoes[0]?.id ?? "")
  const [hoje, setHoje] = useState(() => new Date())
  const [copiado, setCopiado] = useState(false)

  if (citacoes.length === 0) return null
  const citacao = citacoes.find((c) => c.id === ativa) ?? citacoes[0]

  function abre() {
    setHoje(new Date()) // a data de acesso é a de agora, e não a de quando a página abriu
    setCopiado(false)
    janela.current?.showModal()
  }

  function escolhe(id: string) {
    setAtiva(id)
    setCopiado(false)
  }

  function teclado(e: KeyboardEvent<HTMLButtonElement>, indice: number) {
    const passo = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0
    if (!passo) return
    e.preventDefault()
    const proxima = citacoes[(indice + passo + citacoes.length) % citacoes.length]
    escolhe(proxima.id)
    document.getElementById(`aba-${proxima.id}`)?.focus()
  }

  async function copia() {
    const texto = trocaDatas(citacao.texto, hoje)
    try {
      if (citacao.kind === "texto" && typeof ClipboardItem !== "undefined") {
        await navigator.clipboard.write([
          new ClipboardItem({
            "text/plain": new Blob([texto], { type: "text/plain" }),
            "text/html": new Blob([emHtml(citacao, hoje)], { type: "text/html" }),
          }),
        ])
      } else {
        await navigator.clipboard.writeText(texto)
      }
    } catch {
      await navigator.clipboard.writeText(texto)
    }
    setCopiado(true)
    setTimeout(() => setCopiado(false), 2000)
  }

  return (
    <>
      <button type="button" className="btn btn--secondary btn--sm" onClick={abre}>
        {t("artigo.citar")}
      </button>
      <dialog
        ref={janela}
        className="citar"
        aria-labelledby="citar-titulo"
        // Clicar fora da caixa (no fundo escurecido) fecha a janela.
        onClick={(e) => e.target === janela.current && janela.current?.close()}
      >
        <div className="citar__caixa">
          <div className="citar__topo">
            <h2 id="citar-titulo">{t("artigo.citar_titulo")}</h2>
            <button type="button" className="citar__fechar" aria-label={t("artigo.fechar")} onClick={() => janela.current?.close()}>
              <CloseIcon size={20} />
            </button>
          </div>

          <div className="citar__abas" role="tablist">
            {citacoes.map((c, i) => (
              <button
                key={c.id}
                id={`aba-${c.id}`}
                type="button"
                role="tab"
                aria-selected={c.id === citacao.id}
                aria-controls="citar-painel"
                tabIndex={c.id === citacao.id ? 0 : -1}
                className={c.id === citacao.id ? "is-ativa" : undefined}
                onClick={() => escolhe(c.id)}
                onKeyDown={(e) => teclado(e, i)}
              >
                {c.label}
              </button>
            ))}
          </div>

          <div className="citar__bloco">
            <button
              type="button"
              className={`citar__copiar${copiado ? " is-copiado" : ""}`}
              onClick={copia}
              aria-label={copiado ? t("artigo.copiado") : t("artigo.copiar")}
              title={copiado ? t("artigo.copiado") : t("artigo.copiar")}
            >
              {copiado ? <CheckIcon /> : <CopyIcon />}
            </button>
            <div id="citar-painel" role="tabpanel" aria-labelledby={`aba-${citacao.id}`} className="citar__painel">
              {citacao.kind === "codigo" ? (
                <pre tabIndex={0}>
                  <code>{trocaDatas(citacao.texto, hoje)}</code>
                </pre>
              ) : (
                <p tabIndex={0} className="citar__texto">
                  {(citacao.partes ?? []).map(({ t: trecho, e }, i) => {
                    const texto = trocaDatas(trecho, hoje)
                    return e === "b" ? <strong key={i}>{texto}</strong> : e === "i" ? <em key={i}>{texto}</em> : texto
                  })}
                </p>
              )}
            </div>
          </div>
        </div>
      </dialog>
    </>
  )
}
