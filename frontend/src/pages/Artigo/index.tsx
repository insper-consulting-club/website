import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { Article } from "../../types"
import ArtigoMarkdown from "../../components/ArtigoMarkdown"
import PageHero from "../../components/PageHero"
import { ArrowLeftIcon, ExternalIcon, LinkedInIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useTextos from "../../hooks/useTextos"
import "./index.css"

function formatDate(date: string) {
  // Mesmo cuidado da lista: ano/mês/dia separados evitam o desvio de um dia do UTC.
  const [ano, mes, dia] = date.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
}

export default function Artigo() {
  const t = useTextos()
  const { slugOrId } = useParams<{ slugOrId: string }>()
  const [artigo, setArtigo] = useState<Article | null>(null)
  const [loadedId, setLoadedId] = useState<string | undefined>()
  const [copiado, setCopiado] = useState(false)
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
  const ano = artigo.date?.slice(0, 4)
  const citacao = `${artigo.authors ? `${artigo.authors}. ` : ""}${artigo.title}. Insper Consulting Club${ano ? `, ${ano}` : ""}. Disponível em: ${url}.`

  function copiarCitacao() {
    navigator.clipboard.writeText(citacao).then(() => {
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2000)
    })
  }

  return (
    <div className="artigo-page">
      <PageHero
        back={{ to: "/artigos", label: t("artigo.voltar") }}
        eyebrow={artigo.date ? formatDate(artigo.date) : undefined}
        title={artigo.title}
        lead={artigo.authors}
      />

      <section className="section">
        <article className="container artigo">
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

          <div className="artigo__rodape">
            <h2>{t("artigo.como_citar")}</h2>
            <p className="artigo__citacao">{citacao}</p>
            <div className="artigo__acoes">
              <button type="button" className="btn btn--secondary" onClick={copiarCitacao}>
                {copiado ? t("artigo.copiado") : t("artigo.copiar")}
              </button>
              <a
                href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn--secondary"
              >
                <LinkedInIcon size={16} />
                {t("artigo.compartilhar")}
              </a>
              {artigo.link && (
                <a href={artigo.link} target="_blank" rel="noopener noreferrer" className="btn btn--secondary">
                  {t("artigo.link_original")}
                  <ExternalIcon />
                </a>
              )}
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}
