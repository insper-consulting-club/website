import { useEffect, useState } from "react"
import { api } from "../../api"
import type { SiteConfig } from "../../types"
import PageHero from "../../components/PageHero"
import TextoMarkdown from "../../components/TextoMarkdown"
import usePageTitle from "../../hooks/usePageTitle"
import useSiteConfig from "../../hooks/useSiteConfig"
import useTextos from "../../hooks/useTextos"
import "./index.css"

export default function PoliticaPrivacidade() {
  const t = useTextos()
  usePageTitle(t("privacidade.titulo"))
  const reserva = useSiteConfig()
  const [politica, setPolitica] = useState<SiteConfig | null>(null)
  const [erro, setErro] = useState(false)

  useEffect(() => {
    api
      .getSiteConfig()
      .then((data: SiteConfig) => {
        if (data && typeof data.privacy_text === "string") setPolitica(data)
        else setErro(true)
      })
      .catch(() => setErro(true))
  }, [])

  const atualizacao = (politica ?? reserva).privacy_updated

  return (
    <div className="politica-page">
      <PageHero
        title={t("privacidade.titulo")}
        lead={atualizacao ? `Última atualização: ${atualizacao}` : undefined}
      />

      <section className="section">
        <article className="container container--narrow politica-content">
          {politica?.privacy_text ? (
            <TextoMarkdown>{politica.privacy_text}</TextoMarkdown>
          ) : erro || politica ? (
            <>
              <p>{t("privacidade.erro")}</p>
              <p>
                <a href={`mailto:${reserva.email}`}>{reserva.email}</a>
              </p>
            </>
          ) : (
            <p className="loading">Carregando...</p>
          )}
        </article>
      </section>
    </div>
  )
}
