import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { Article } from "../../types"
import ArtigoMarkdown from "../../components/ArtigoMarkdown"
import AutoresDoArtigo from "../../components/AutoresDoArtigo"
import CitarArtigo from "../../components/CitarArtigo"
import CompartilharArtigo from "../../components/CompartilharArtigo"
import PageHero from "../../components/PageHero"
import { ArrowLeftIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useTextos from "../../hooks/useTextos"
import "./index.css"

function formatDate(date: string) {
  // Mesmo cuidado da lista: ano/mês/dia separados evitam o desvio de um dia do UTC.
  const [ano, mes, dia] = date.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "numeric", month: "long", year: "numeric" })
}

export default function Artigo() {
  const t = useTextos()
  const { slugOrId } = useParams<{ slugOrId: string }>()
  const [artigo, setArtigo] = useState<Article | null>(null)
  const [loadedId, setLoadedId] = useState<string | undefined>()
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

  return (
    <div className="artigo-page">
      {/* Um bloco só: título, autores, data e ações, na mesma coluna do texto. */}
      <PageHero
        estreito
        back={{ to: "/artigos", label: t("artigo.voltar") }}
        title={artigo.title}
        lead={<AutoresDoArtigo autores={artigo.authors} links />}
      >
        {artigo.date && <p className="artigo__data">{formatDate(artigo.date)}</p>}
        <div className="artigo__acoes">
          <CompartilharArtigo titulo={artigo.title} url={url} />
          <CitarArtigo citacoes={artigo.citations} />
        </div>
      </PageHero>

      <section className="section">
        <article className="container artigo">
          {artigo.image_url && <img src={artigo.image_url} alt="" className="artigo__capa" />}
          {(artigo.description || temas.length > 0) && (
            <div className="artigo__resumo">
              {artigo.description && (
                <>
                  <h2>{t("artigo.resumo")}</h2>
                  <p>{artigo.description}</p>
                </>
              )}
              {temas.length > 0 && (
                <p className="artigo__palavras">
                  {t("artigo.palavras_chave") && <strong>{t("artigo.palavras_chave")}: </strong>}
                  {temas.join(" · ")}
                </p>
              )}
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
