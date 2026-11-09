import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { Partner } from "../../types"
import PageHero from "../../components/PageHero"
import { ArrowRightIcon, MailIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useSiteConfig from "../../hooks/useSiteConfig"
import useTextos from "../../hooks/useTextos"
import "./index.css"

export default function Parceiros() {
  const config = useSiteConfig()
  const t = useTextos()
  usePageTitle(t("parceiros.eyebrow"), t("parceiros.abertura"))
  const [partners, setPartners] = useState<Partner[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getPartners()
      .then((data) => setPartners(data || []))
      .catch(() => setPartners([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="parceiros-page">
      <PageHero
        eyebrow={t("parceiros.eyebrow")}
        title={<>{t("parceiros.titulo")} <span className="destaque">{t("parceiros.titulo_destaque")}</span></>}
        lead={t("parceiros.abertura")}
      />

      <section className="section">
        <div className="container">
          {loading ? (
            <p className="loading">Carregando parceiros...</p>
          ) : partners.length === 0 ? (
            <p className="state-message">{t("parceiros.vazio")}</p>
          ) : (
            <div className="grid grid--3">
              {partners.map((p) => (
                <Link key={p.id} to={`/parceiros/${p.id}`} className="parceiro-card">
                  <div className="parceiro-card__logo">
                    {p.logo_url ? <img src={p.logo_url} alt={p.name} loading="lazy" /> : <span>{p.name}</span>}
                  </div>
                  <div className="parceiro-card__body">
                    {p.category && <p className="parceiro-card__categoria">{p.category}</p>}
                    <h2 className="parceiro-card__nome">{p.name}</h2>
                    {p.description && <p className="parceiro-card__descricao">{p.description}</p>}
                    <span className="link-arrow parceiro-card__mais">
                      {t("parceiros.card_link")}
                      <ArrowRightIcon />
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="section section--dark">
        <div className="container">
          <div className="section-head">
            <p className="eyebrow">{t("parceiros.beneficios_eyebrow")}</p>
            <h2 className="section-title">{t("parceiros.beneficios_titulo")}</h2>
          </div>

          <div className="grid grid--3 parceiros-beneficios">
            {config.partner_benefits.map((b, index) => (
              <div className="parceiros-beneficio" key={b.id}>
                <span className="parceiros-beneficio__index">{String(index + 1).padStart(2, "0")}</span>
                <h3>{b.title}</h3>
                <p>{b.description}</p>
              </div>
            ))}
          </div>

          <a href={`mailto:${config.email}`} className="btn btn--light parceiros-cta">
            <MailIcon size={18} />
            {t("parceiros.botao_contato")}
          </a>
        </div>
      </section>
    </div>
  )
}
