import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { ActivityDetail } from "../../types"
import ContentBlockComponent from "../../components/ContentBlock/index"
import "../PerfilAtividade/index.css"

export default function PerfilAtividadeItem() {
  const { id } = useParams()
  const [activity, setActivity] = useState<ActivityDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeImage, setActiveImage] = useState(0)

  useEffect(() => {
    if (id) {
      api.getActivity(Number(id)).then((data) => {
        setActivity(data)
        setLoading(false)
      })
    }
  }, [id])

  if (loading)
    return <div className="perfil-loading"><div className="perfil-loading__spinner" /><span>Carregando...</span></div>

  if (!activity)
    return <div className="perfil-notfound"><p>Atividade não encontrada.</p><Link to="/atividades" className="perfil-back-link">← Voltar</Link></div>

  return (
    <div className="perfil-page">

      {/* Breadcrumb */}
      <div className="perfil-breadcrumb">
        <Link to="/atividades" className="perfil-breadcrumb__link">Atividades</Link>
        {activity.category && (
          <>
            <span className="perfil-breadcrumb__sep">›</span>
            <Link to={`/atividades/categoria/${activity.category.slug}`} className="perfil-breadcrumb__link">
              {activity.category.label}
            </Link>
          </>
        )}
        <span className="perfil-breadcrumb__sep">›</span>
        <span className="perfil-breadcrumb__current">{activity.title}</span>
      </div>

      {/* Hero */}
      <header className="perfil-hero">
        <div className="perfil-hero__inner">
          <div className="perfil-hero__meta">
            {activity.category && (
              <span className={`cat-badge ${activity.category.badge_class}`}>
                {activity.category.label}
              </span>
            )}
          </div>
          <h1 className="perfil-hero__title">{activity.title}</h1>
          <p className="perfil-hero__desc">{activity.description}</p>
        </div>
        <div className="perfil-hero__accent" aria-hidden="true">
          <svg viewBox="0 0 400 300" fill="none" preserveAspectRatio="xMidYMid slice">
            <circle cx="350" cy="50" r="180" fill="rgba(200,16,46,0.05)" />
            <circle cx="380" cy="250" r="100" fill="rgba(200,16,46,0.04)" />
          </svg>
        </div>
      </header>

      <div className="perfil-body">

        {/* Galeria */}
        {activity.images.length > 0 && (
          <section className="perfil-gallery">
            <div className="perfil-gallery__main">
              <img src={activity.images[activeImage].image_url} alt={activity.images[activeImage].caption || activity.title} />
              {activity.images[activeImage].caption && (
                <p className="perfil-gallery__caption">{activity.images[activeImage].caption}</p>
              )}
            </div>
            {activity.images.length > 1 && (
              <div className="perfil-gallery__thumbs">
                {activity.images.map((img, i) => (
                  <button key={img.id} className={`perfil-gallery__thumb ${i === activeImage ? "active" : ""}`} onClick={() => setActiveImage(i)}>
                    <img src={img.image_url} alt={img.caption || `Imagem ${i + 1}`} />
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Parceiro responsável */}
        {activity.responsible_partner && (
          <section className="perfil-section">
            <h2 className="perfil-section__title">
              <span className="perfil-section__icon"><svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/><circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="2"/></svg></span>
              Empresa Responsável
            </h2>
            <ul className="perfil-list">
              <li className="perfil-list__item">
                <div className="perfil-list__avatar perfil-list__avatar--partner">
                  {activity.responsible_partner.name.charAt(0).toUpperCase()}
                </div>
                <Link to={`/parceiros/${activity.responsible_partner.id}`}>
                  {activity.responsible_partner.name}
                </Link>
              </li>
            </ul>
          </section>
        )}

        {/* Blocos de conteúdo */}
        {activity.content_blocks.length > 0 && (
          <section className="perfil-content-blocks">
            {activity.content_blocks.map((block) => (
              <ContentBlockComponent key={block.id} block={block} />
            ))}
          </section>
        )}

        {/* Voltar */}
        <div className="perfil-footer-nav">
          {activity.category ? (
            <Link to={`/atividades/categoria/${activity.category.slug}`} className="perfil-back-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M19 12H5M12 5l-7 7 7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
              Voltar para {activity.category.label}
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