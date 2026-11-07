import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { Project, Activity, ActivityCategory } from "../../types"
import "./index.css"

export default function CategoriaAtividade() {
  const { categoria } = useParams<{ categoria: string }>()
  const [meta, setMeta] = useState<ActivityCategory | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!categoria) return

    Promise.all([
      api.getCategories(),
      api.getProjects(categoria),
      api.getActivities(categoria),
    ]).then(([categoriesData, projectsData, activitiesData]) => {
      const found = categoriesData.find((c: ActivityCategory) => c.slug === categoria)
      if (!found) {
        setNotFound(true)
      } else {
        setMeta(found)
        setProjects(projectsData)
        setActivities(activitiesData)
      }
      setLoading(false)
    })
  }, [categoria])

  if (loading)
    return (
      <div className="cat-loading">
        <div className="cat-loading__spinner" />
        <span>Carregando...</span>
      </div>
    )

  if (notFound || !meta)
    return (
      <div className="cat-notfound">
        <p>Categoria não encontrada.</p>
        <Link to="/atividades">← Voltar para Atividades</Link>
      </div>
    )

  const totalItems = projects.length + activities.length

  return (
    <div className="cat-page">

      {/* Breadcrumb */}
      <div className="cat-breadcrumb">
        <Link to="/atividades" className="cat-breadcrumb__link">Atividades</Link>
        <span className="cat-breadcrumb__sep">›</span>
        <span className="cat-breadcrumb__current">{meta.label}</span>
      </div>

      {/* Header */}
      <header className="cat-header">
        <div className="cat-header__inner">
          {meta.badge && <span className={`cat-badge ${meta.badge_class}`}>{meta.badge}</span>}
          <h1 className="cat-header__title">{meta.label}</h1>
          <p className="cat-header__desc">{meta.description}</p>
        </div>
        <div className="cat-header__bg" aria-hidden="true" />
      </header>

      {/* Conteúdo */}
      <section className="cat-projects">
        {totalItems === 0 ? (
          <div className="cat-empty">
            <p>Nenhum item encontrado para esta categoria.</p>
          </div>
        ) : (
          <>
            <div className="cat-projects__header">
              <h2 className="cat-projects__count">
                {totalItems} {totalItems === 1 ? "item" : "itens"}
              </h2>
            </div>

            {/* Projetos — clicáveis */}
            {projects.length > 0 && (
              <>
                {activities.length > 0 && <h3 className="cat-section-title">Projetos</h3>}
                <div className="cat-grid">
                  {projects.map((p) => (
                    <Link key={p.id} to={`/atividades/${p.id}`} className="cat-card">
                      <div className="cat-card__top">
                        <h3 className="cat-card__title">{p.title}</h3>
                        <svg className="cat-card__arrow" width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M7 17L17 7M17 7H7M17 7v10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <p className="cat-card__desc">{p.description}</p>
                    </Link>
                  ))}
                </div>
              </>
            )}

            {/* Atividades — clicáveis */}
            {activities.length > 0 && (
              <>
                {projects.length > 0 && <h3 className="cat-section-title">Atividades</h3>}
                <div className="cat-grid">
                  {activities.map((a) => (
                    <Link key={a.id} to={`/atividades/item/${a.id}`} className="cat-card">
                      <div className="cat-card__top">
                        <h3 className="cat-card__title">{a.title}</h3>
                        <svg className="cat-card__arrow" width="16" height="16" viewBox="0 0 24 24" fill="none">
                          <path d="M7 17L17 7M17 7H7M17 7v10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                        </svg>
                      </div>
                      <p className="cat-card__desc">{a.description}</p>
                    </Link>
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </section>

      {/* Back */}
      <div className="cat-footer-nav">
        <Link to="/atividades" className="cat-back-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          Todas as Atividades
        </Link>
      </div>
    </div>
  )
}
