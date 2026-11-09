import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { ArticleSummary } from "../../types"
import PageHero from "../../components/PageHero"
import { ArrowRightIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useTextos from "../../hooks/useTextos"
import "./index.css"

function formatDate(date: string) {
  // new Date(date) leria "AAAA-MM-DD" como meia-noite UTC, que em horário de
  // Brasília já é o dia anterior; construindo com ano/mês/dia separados, a
  // data é interpretada no fuso local, sem esse desvio de um dia.
  const [ano, mes, dia] = date.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
}

export default function Artigos() {
  const t = useTextos()
  usePageTitle(t("artigos.titulo"))
  const [artigos, setArtigos] = useState<ArticleSummary[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getArticles()
      .then((data) => setArtigos(data || []))
      .catch(() => setArtigos([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="artigos-page">
      <PageHero
        title={t("artigos.titulo")}
        lead={t("artigos.abertura")}
      />

      <section className="section">
        <div className="container">
          {loading ? (
            <p className="loading">Carregando...</p>
          ) : artigos.length === 0 ? (
            <p className="state-message">{t("artigos.vazio")}</p>
          ) : (
            <div className="grid grid--3">
              {artigos.map((item) => (
                <Link key={item.id} to={`/artigos/${item.slug || item.id}`} className="artigos-card">
                  <div className="artigos-card__image">
                    {item.image_url ? <img src={item.image_url} alt="" loading="lazy" /> : <span>{item.source || "ICC"}</span>}
                  </div>
                  <div className="artigos-card__body">
                    {(item.source || item.date) && (
                      <p className="artigos-card__meta">
                        {item.source}
                        {item.source && item.date && " · "}
                        {item.date && formatDate(item.date)}
                      </p>
                    )}
                    <h2 className="artigos-card__title">{item.title}</h2>
                    {item.authors && <p className="artigos-card__authors">{item.authors}</p>}
                    {item.description && <p className="artigos-card__desc">{item.description}</p>}
                    <span className="link-arrow artigos-card__cta">
                      {t("artigos.card_link")}
                      <ArrowRightIcon />
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
