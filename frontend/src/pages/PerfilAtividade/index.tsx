import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { ProjectDetail } from "../../types"
import ContentBlockComponent from "../../components/ContentBlock/index"
import "./index.css"

function formatDate(date: string) {
  return new Date(date).toLocaleDateString("pt-BR", { month: "long", year: "numeric" })
}

function formatDateShort(date: string) {
  return new Date(date).toLocaleDateString("pt-BR", { day: "2-digit", month: "short", year: "numeric" })
}

function StatusBadge({ endDate }: { endDate: string | null }) {
  const active = !endDate
  return (
    <span className={`perfil-status ${active ? "perfil-status--active" : "perfil-status--done"}`}>
      <span className="perfil-status__dot" />
      {active ? "Em andamento" : "Concluído"}
    </span>
  )
}

export default function PerfilAtividade() {
  const { id } = useParams()
  const [project, setProject] = useState<ProjectDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeImage, setActiveImage] = useState(0)

  useEffect(() => {
    if (id) {
      api.getProject(Number(id)).then((data) => {
        setProject(data)
        setLoading(false)
      })
    }
  }, [id])

  if (loading)
    return <div className="perfil-loading"><div className="perfil-loading__spinner" /><span>Carregando projeto...</span></div>

  if (!project)
    return <div className="perfil-notfound"><p>Projeto não encontrado.</p><Link to="/atividades" className="perfil-back-link">← Voltar</Link></div>

  const duration = project.end_date
    ? `${formatDate(project.start_date)} – ${formatDate(project.end_date)}`
    : `Desde ${formatDate(project.start_date)}`

  return (
    <div className="perfil-page">

      {/* Breadcrumb */}
      <div className="perfil-breadcrumb">
        <Link to="/atividades" className="perfil-breadcrumb__link">Atividades</Link>
        {project.category && (
          <>
            <span className="perfil-breadcrumb__sep">›</span>
            <Link to={`/atividades/categoria/${project.category.slug}`} className="perfil-breadcrumb__link">
              {project.category.label}
            </Link>
          </>
        )}
        <span className="perfil-breadcrumb__sep">›</span>
        <span className="perfil-breadcrumb__current">{project.title}</span>
      </div>

      {/* Hero */}
      <header className="perfil-hero">
        <div className="perfil-hero__inner">
          <div className="perfil-hero__meta">
            <StatusBadge endDate={project.end_date} />
            {project.category && (
              <span className={`perfil-hero__category cat-badge ${project.category.badge_class}`}>
                {project.category.label}
              </span>
            )}
            <span className="perfil-hero__duration">{duration}</span>
          </div>
          <h1 className="perfil-hero__title">{project.title}</h1>
          <p className="perfil-hero__desc">{project.description}</p>
        </div>
        <div className="perfil-hero__accent" aria-hidden="true">
          <svg viewBox="0 0 400 300" fill="none" preserveAspectRatio="xMidYMid slice">
            <circle cx="350" cy="50" r="180" fill="rgba(200,16,46,0.05)" />
            <circle cx="380" cy="250" r="100" fill="rgba(200,16,46,0.04)" />
          </svg>
        </div>
      </header>

      <div className="perfil-body">

        {/* Stats */}
        <div className="perfil-stats">
          <div className="perfil-stat">
            <span className="perfil-stat__value">{project.members.length}</span>
            <span className="perfil-stat__label">Membros</span>
          </div>
          <div className="perfil-stat">
            <span className="perfil-stat__value">{project.partners.length}</span>
            <span className="perfil-stat__label">Parceiros</span>
          </div>
          <div className="perfil-stat">
            <span className="perfil-stat__value">{project.end_date ? "✓" : "→"}</span>
            <span className="perfil-stat__label">{project.end_date ? "Concluído" : "Ativo"}</span>
          </div>
        </div>

        {/* Galeria */}
        {project.images.length > 0 && (
          <section className="perfil-gallery">
            <div className="perfil-gallery__main">
              <img src={project.images[activeImage].image_url} alt={project.images[activeImage].caption || project.title} />
              {project.images[activeImage].caption && (
                <p className="perfil-gallery__caption">{project.images[activeImage].caption}</p>
              )}
            </div>
            {project.images.length > 1 && (
              <div className="perfil-gallery__thumbs">
                {project.images.map((img, i) => (
                  <button key={img.id} className={`perfil-gallery__thumb ${i === activeImage ? "active" : ""}`} onClick={() => setActiveImage(i)}>
                    <img src={img.image_url} alt={img.caption || `Imagem ${i + 1}`} />
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Parceiros e Membros */}
        <div className="perfil-columns">
          {project.partners.length > 0 && (
            <section className="perfil-section">
              <h2 className="perfil-section__title">
                <span className="perfil-section__icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/><circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="2"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg></span>
                Empresas Parceiras
              </h2>
              <ul className="perfil-list">
                {project.partners.map((p) => (
                  <li key={p.id} className="perfil-list__item">
                    <div className="perfil-list__avatar perfil-list__avatar--partner">{p.name.charAt(0).toUpperCase()}</div>
                    <Link to={`/parceiros/${p.id}`}>{p.name}</Link>
                  </li>
                ))}
              </ul>
            </section>
          )}
          {project.members.length > 0 && (
            <section className="perfil-section">
              <h2 className="perfil-section__title">
                <span className="perfil-section__icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg></span>
                Equipe do Projeto
              </h2>
              <div className="perfil-members-grid">
                {project.members.map((m) => (
                  <Link key={m.id} to={`/equipe/${m.id}`} className="perfil-member-chip">
                    <div className="perfil-member-chip__avatar">{m.name.split(" ").map((n) => n[0]).slice(0, 2).join("").toUpperCase()}</div>
                    <span className="perfil-member-chip__name">{m.name}</span>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Blocos de conteúdo */}
        {project.content_blocks.length > 0 && (
          <section className="perfil-content-blocks">
            {project.content_blocks.map((block) => (
              <ContentBlockComponent key={block.id} block={block} />
            ))}
          </section>
        )}

        {/* Cronograma */}
        <section className="perfil-timeline-card">
          <h2 className="perfil-section__title" style={{ marginBottom: "24px" }}>
            <span className="perfil-section__icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="3" y="4" width="18" height="18" rx="2" stroke="currentColor" strokeWidth="2"/><path d="M16 2v4M8 2v4M3 10h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg></span>
            Cronograma
          </h2>

          {project.timeline_events.length > 0 ? (
            <div className="perfil-timeline-rich">
              <div className="perfil-timeline-rich__item perfil-timeline-rich__item--start">
                <div className="perfil-timeline-rich__dot" />
                <div className="perfil-timeline-rich__content">
                  <span className="perfil-timeline-rich__date">{formatDateShort(project.start_date)}</span>
                  <span className="perfil-timeline-rich__title">Início do projeto</span>
                </div>
              </div>
              {project.timeline_events.map((event) => (
                <div key={event.id} className="perfil-timeline-rich__item">
                  <div className="perfil-timeline-rich__dot perfil-timeline-rich__dot--event" />
                  <div className="perfil-timeline-rich__content">
                    <span className="perfil-timeline-rich__date">{formatDateShort(event.date)}</span>
                    <span className="perfil-timeline-rich__title">{event.title}</span>
                    {event.description && <p className="perfil-timeline-rich__desc">{event.description}</p>}
                  </div>
                </div>
              ))}
              <div className={`perfil-timeline-rich__item ${project.end_date ? "perfil-timeline-rich__item--end" : "perfil-timeline-rich__item--ongoing"}`}>
                <div className="perfil-timeline-rich__dot" />
                <div className="perfil-timeline-rich__content">
                  <span className="perfil-timeline-rich__date">{project.end_date ? formatDateShort(project.end_date) : "Em andamento"}</span>
                  <span className="perfil-timeline-rich__title">{project.end_date ? "Conclusão" : "Projeto ativo"}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="perfil-timeline">
              <div className="perfil-timeline__item perfil-timeline__item--start">
                <div className="perfil-timeline__dot" />
                <div><span className="perfil-timeline__label">Início</span><span className="perfil-timeline__date">{formatDate(project.start_date)}</span></div>
              </div>
              <div className="perfil-timeline__line" />
              <div className={`perfil-timeline__item ${project.end_date ? "perfil-timeline__item--end" : "perfil-timeline__item--ongoing"}`}>
                <div className="perfil-timeline__dot" />
                <div>
                  <span className="perfil-timeline__label">{project.end_date ? "Conclusão" : "Previsão"}</span>
                  <span className="perfil-timeline__date">{project.end_date ? formatDate(project.end_date) : "Em andamento"}</span>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Voltar */}
        <div className="perfil-footer-nav">
          {project.category ? (
            <Link to={`/atividades/categoria/${project.category.slug}`} className="perfil-back-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              Voltar para {project.category.label}
            </Link>
          ) : (
            <Link to="/atividades" className="perfil-back-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              Voltar para Atividades
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
