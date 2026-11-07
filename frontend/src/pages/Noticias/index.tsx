import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { NewsItem } from "../../types"
import PageHero from "../../components/PageHero"
import { ArrowRightIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import "./index.css"

function formatDate(date: string) {
  // new Date(date) leria "AAAA-MM-DD" como meia-noite UTC, que em horário de
  // Brasília já é o dia anterior; construindo com ano/mês/dia separados, a
  // data é interpretada no fuso local, sem esse desvio de um dia.
  const [ano, mes, dia] = date.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
}

export default function Noticias() {
  usePageTitle("Artigos")
  const [news, setNews] = useState<NewsItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getNews()
      .then((data) => setNews(data || []))
      .catch(() => setNews([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="news-page">
      <PageHero
        title="Artigos"
        lead="Artigos e publicações produzidos por membros do ICC"
      />

      <section className="section">
        <div className="container">
          {loading ? (
            <p className="loading">Carregando...</p>
          ) : news.length === 0 ? (
            <p className="state-message">Nenhum artigo cadastrado no momento.</p>
          ) : (
            <div className="grid grid--3">
              {news.map((item) => (
                <Link key={item.id} to={`/artigos/${item.slug || item.id}`} className="news-card">
                  <div className="news-card__image">
                    {item.image_url ? <img src={item.image_url} alt="" loading="lazy" /> : <span>{item.source || "ICC"}</span>}
                  </div>
                  <div className="news-card__body">
                    {(item.source || item.date) && (
                      <p className="news-card__meta">
                        {item.source}
                        {item.source && item.date && " · "}
                        {item.date && formatDate(item.date)}
                      </p>
                    )}
                    <h2 className="news-card__title">{item.title}</h2>
                    {item.authors && <p className="news-card__authors">{item.authors}</p>}
                    {item.description && <p className="news-card__desc">{item.description}</p>}
                    <span className="link-arrow news-card__cta">
                      Ler artigo
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
