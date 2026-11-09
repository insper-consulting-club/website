import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { Article } from "../../types"
import ArtigoMarkdown from "../../components/ArtigoMarkdown"
import AutoresDoArtigo from "../../components/AutoresDoArtigo"
import PageHero from "../../components/PageHero"
import { ArrowLeftIcon, LinkedInIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useTextos from "../../hooks/useTextos"
import "./index.css"

function formatDate(date: string) {
  // Mesmo cuidado da lista: ano/mês/dia separados evitam o desvio de um dia do UTC.
  const [ano, mes, dia] = date.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
}

type Formato = "bibtex" | "biblatex"

// A API entrega as referências com este marcador no lugar da data de acesso, que é a de quem copia.
const DATA_DE_ACESSO = "__DATA_DE_ACESSO__"

function hoje() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`
}

export default function Artigo() {
  const t = useTextos()
  const { slugOrId } = useParams<{ slugOrId: string }>()
  const [artigo, setArtigo] = useState<Article | null>(null)
  const [loadedId, setLoadedId] = useState<string | undefined>()
  const [copiado, setCopiado] = useState(false)
  // A referência aberta, ou nenhuma. Começa fechada: é longa, e quase ninguém precisa dela.
  const [formato, setFormato] = useState<Formato | null>(null)
  const loading = loadedId !== slugOrId
  const artigoDaRota = artigo && (artigo.slug === slugOrId || String(artigo.id) === slugOrId) ? artigo : null
  usePageTitle(loading ? undefined : artigoDaRota?.title, loading ? undefined : artigoDaRota?.description)

  useEffect(() => {
    if (!slugOrId) return
    api
      .getArticle(slugOrId)
      .then((data: Article) => setArtigo(data && data.id ? data : null))
      .catch(() => setArtigo(null))
      .finally(() => setLoadedId(slugOrId))
  }, [slugOrId])

  if (loading) return <p className="loading">Carregando...</p>

  if (!artigo) {
    return (
      <section className="section">
        <div className="container">
          <Link to="/artigos" className="back-link">
            <ArrowLeftIcon size={14} />
            {t("artigo.voltar")}
          </Link>
          <p className="state-message">
            <strong>{t("artigo.nao_encontrado_titulo")}</strong>
            {t("artigo.nao_encontrado_texto")}
          </p>
        </div>
      </section>
    )
  }

  const temas = artigo.topics.split(",").map((t) => t.trim()).filter(Boolean)
  const url = window.location.href
  const referencia = formato ? artigo[formato].split(DATA_DE_ACESSO).join(hoje()) : ""

  function copiarReferencia() {
    navigator.clipboard.writeText(referencia).then(() => {
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2000)
    })
  }

  function alterna(novo: Formato) {
    setCopiado(false)
    setFormato(formato === novo ? null : novo)
  }

  return (
    <div className="artigo-page">
      <PageHero
        back={{ to: "/artigos", label: t("artigo.voltar") }}
        eyebrow={artigo.date ? formatDate(artigo.date) : undefined}
        title={artigo.title}
        lead={<AutoresDoArtigo autores={artigo.authors} links />}
      />

      <section className="section">
        <article className="container artigo">
          {/* As ações ficam no começo: não faz sentido só aparecerem para quem leu o texto inteiro. */}
          <div className="artigo__acoes">
            <a
              href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn--secondary"
            >
              <LinkedInIcon size={16} />
              {t("artigo.compartilhar")}
            </a>
            {(["bibtex", "biblatex"] as const).map((f) => (
              <button
                key={f}
                type="button"
                className={`btn btn--secondary${formato === f ? " is-aberto" : ""}`}
                aria-expanded={formato === f}
                aria-controls="artigo-referencia"
                onClick={() => alterna(f)}
              >
                {t(f === "bibtex" ? "artigo.exportar_bibtex" : "artigo.exportar_biblatex")}
              </button>
            ))}
          </div>
          {formato && (
            <div className="artigo__referencia" id="artigo-referencia">
              <pre tabIndex={0}>
                <code>{referencia}</code>
              </pre>
              <button type="button" className="btn btn--secondary" onClick={copiarReferencia}>
                {copiado ? t("artigo.copiado") : t("artigo.copiar")}
              </button>
            </div>
          )}

          {temas.length > 0 && (
            <ul className="artigo__temas">
              {temas.map((tema) => (
                <li key={tema}>{tema}</li>
              ))}
            </ul>
          )}
          {artigo.image_url && <img src={artigo.image_url} alt="" className="artigo__capa" />}
          {artigo.description && (
            <div className="artigo__resumo">
              <h2>{t("artigo.resumo")}</h2>
              <p>{artigo.description}</p>
            </div>
          )}
          {/* O texto vem em Markdown (ver components/ArtigoMarkdown). */}
          {artigo.content && (
            <div className="artigo__texto">
              <ArtigoMarkdown texto={artigo.content} imagens={artigo.images ?? []} />
            </div>
          )}
        </article>
      </section>
    </div>
  )
}
