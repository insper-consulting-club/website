import { useEffect, useState } from "react"
import { api } from "../../api"
import type { SiteConfig } from "../../types"
import PageHero from "../../components/PageHero"
import TextoMarkdown from "../../components/TextoMarkdown"
import usePageTitle from "../../hooks/usePageTitle"
import useSiteConfig from "../../hooks/useSiteConfig"
import "./index.css"

export default function PoliticaPrivacidade() {
  usePageTitle("Política de Privacidade")
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
        title="Política de Privacidade"
        lead={atualizacao ? `Última atualização: ${atualizacao}` : undefined}
      />

      <section className="section">
        <article className="container container--narrow politica-content">
          {politica?.privacy_text ? (
            <TextoMarkdown>{politica.privacy_text}</TextoMarkdown>
          ) : erro || politica ? (
            <p>
              Não foi possível exibir a política agora. Para qualquer dúvida sobre o tratamento
              dos seus dados, escreva para{" "}
              <a href={`mailto:${reserva.email}`}>{reserva.email}</a>.
            </p>
          ) : (
            <p className="loading">Carregando...</p>
          )}
        </article>
      </section>
    </div>
  )
}
