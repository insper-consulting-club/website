import { useEffect, useMemo, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { Partner } from "../../types"
import { ArrowLeftIcon, ArrowRightIcon, ExternalIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useTextos from "../../hooks/useTextos"
import "./index.css"

type PartnerProject = {
  id: number
  title: string
  description?: string
  end_date?: string | null
  program?: string
}

type PartnerDetail = {
  id: number
  name: string
  description: string
  category?: string
  site?: string | null
  logo_url?: string | null
  projects?: PartnerProject[]
}

function formatDateBR(dateString?: string | null) {
  if (!dateString) return ""
  // new Date(dateString) leria "AAAA-MM-DD" como meia-noite UTC, que em
  // horário de Brasília já é o dia anterior; construindo com ano/mês/dia
  // separados, a data é interpretada no fuso local, sem esse desvio de um dia.
  const [ano, mes, dia] = dateString.split("-").map(Number)
  const date = new Date(ano, mes - 1, dia)
  if (Number.isNaN(date.getTime())) return dateString
  return new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "long", year: "numeric" }).format(date)
}

export default function PerfilParceiro() {
  const t = useTextos()
  const { id } = useParams<{ id: string }>()
  const [partner, setPartner] = useState<PartnerDetail | null>(null)
  const [todos, setTodos] = useState<Partner[]>([])
  const [loadedId, setLoadedId] = useState<string | undefined>()
  const loading = loadedId !== id
  usePageTitle(partner?.name, partner?.description)

  useEffect(() => {
    if (!id) return
    Promise.all([api.getPartner(Number(id)), api.getPartners()])
      .then(([data, lista]: [PartnerDetail, Partner[]]) => {
        setPartner(data && data.id ? data : null)
        setTodos(lista || [])
      })
      .catch(() => setPartner(null))
      .finally(() => setLoadedId(id))
  }, [id])

  const casos = useMemo(
    () => (partner?.projects || []).filter((project) => Boolean(project.end_date)),
    [partner]
  )

  if (loading) return <p className="loading">Carregando...</p>

  if (!partner) {
    return (
      <section className="section">
        <div className="container">
          <Link to="/parceiros" className="back-link">
            <ArrowLeftIcon size={14} />
            {t("parceiro.voltar")}
          </Link>
          <p className="state-message">
            <strong>{t("parceiro.nao_encontrado_titulo")}</strong>
            {t("parceiro.nao_encontrado_texto")}
          </p>
        </div>
      </section>
    )
  }

  const mesmaCategoria = todos.filter((p) => p.id !== partner.id && p.category === partner.category)

  return (
    <div className="parceiro-page">
      <section className="section parceiro-page__main">
        <div className="container">
          <Link to="/parceiros" className="back-link">
            <ArrowLeftIcon size={14} />
            {t("parceiro.voltar")}
          </Link>

          <div className="parceiro-detalhe">
            <div className="parceiro-detalhe__logo">
              {partner.logo_url ? (
                <img src={partner.logo_url} alt={partner.name} />
              ) : (
                <span>{partner.name}</span>
              )}
            </div>

            <div className="parceiro-detalhe__info">
              {partner.category && <p className="eyebrow">{partner.category}</p>}
              <h1 className="parceiro-detalhe__nome">{partner.name}</h1>
              {partner.description && <p className="parceiro-detalhe__descricao">{partner.description}</p>}
              {partner.site && (
                <a href={partner.site} target="_blank" rel="noopener noreferrer" className="btn btn--primary parceiro-detalhe__site">
                  {t("parceiro.visitar_site")}
                  <ExternalIcon />
                </a>
              )}
            </div>
          </div>
        </div>
      </section>

      {casos.length > 0 && (
        <section className="section section--muted">
          <div className="container">
            <div className="section-head">
              <h2 className="section-title">{t("parceiro.casos")}</h2>
            </div>
            <div className="grid grid--2">
              {casos.map((project) => (
                <Link to={`/projetos/projeto/${project.id}`} className="card parceiro-caso" key={project.id}>
                  <h3 className="parceiro-caso__titulo">{project.title}</h3>
                  {project.description && <p className="parceiro-caso__descricao">{project.description}</p>}
                  <p className="parceiro-caso__meta">
                    {project.end_date && t("projeto_card.concluido_em", { data: formatDateBR(project.end_date) })}
                    {project.program && ` · ${project.program}`}
                  </p>
                  <span className="link-arrow">
                    {t("parceiro.caso_link")}
                    <ArrowRightIcon />
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {mesmaCategoria.length > 0 && (
        <section className="section section--muted">
          <div className="container">
            <div className="section-head section-head--row">
              <h2 className="section-title">{t("parceiro.outros", { categoria: partner.category ?? "" })}</h2>
              <Link to="/parceiros" className="link-arrow">
                {t("parceiro.todos")}
                <ArrowRightIcon />
              </Link>
            </div>
            <ul className="parceiro-outros">
              {mesmaCategoria.map((p) => (
                <li key={p.id}>
                  <Link to={`/parceiros/${p.id}`} className="parceiro-outros__item">
                    <span className="parceiro-outros__logo">
                      {p.logo_url ? <img src={p.logo_url} alt="" loading="lazy" /> : null}
                    </span>
                    <span className="parceiro-outros__nome">{p.name}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}
    </div>
  )
}
