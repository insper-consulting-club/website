import { useEffect, useState } from "react"
import Markdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"
import { api } from "../../api"
import type { SiteConfig } from "../../types"
import PageHero from "../../components/PageHero"
import usePageTitle from "../../hooks/usePageTitle"
import useSiteConfig from "../../hooks/useSiteConfig"
import "./index.css"

// Links externos abrem em outra aba. O HTML digitado no admin não é
// executado: o react-markdown o mostra como texto.
const componentes: Components = {
  a: ({ href, children }) =>
    href?.startsWith("http") ? (
      <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>
    ) : (
      <a href={href}>{children}</a>
    ),
}

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
            <Markdown remarkPlugins={[remarkGfm]} components={componentes}>
              {politica.privacy_text}
            </Markdown>
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
