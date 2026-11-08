import PageHero from "../../components/PageHero"
import { GitHubIcon, InstagramIcon, LinkedInIcon, MailIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useSiteConfig from "../../hooks/useSiteConfig"
import useTextos from "../../hooks/useTextos"
import type { SiteConfig } from "../../types"
import "./index.css"

function canais(config: SiteConfig) {
  return [
    {
      label: "E-mail",
      valor: config.email,
      href: `mailto:${config.email}`,
      icon: <MailIcon size={20} />,
    },
    {
      label: "Instagram",
      valor: config.instagram_label,
      href: config.instagram_url,
      icon: <InstagramIcon size={20} />,
    },
    {
      label: "LinkedIn",
      valor: config.linkedin_label,
      href: config.linkedin_url,
      icon: <LinkedInIcon size={19} />,
    },
    {
      label: "GitHub",
      valor: config.github_label,
      href: config.github_url,
      icon: <GitHubIcon size={19} />,
    },
  ]
}

export default function Contato() {
  const t = useTextos()
  const config = useSiteConfig()
  usePageTitle(t("contato.titulo"), config.contact_lead)

  return (
    <div className="contato-page">
      <PageHero title={t("contato.titulo")} lead={config.contact_lead} />

      <section className="section">
        <div className="container contato-grid">
          <aside className="contato-canais">
            <h2 className="contato-canais__title">{t("contato.canais_titulo")}</h2>
            <ul>
              {canais(config).map((canal) => (
                <li key={canal.label}>
                  <a
                    href={canal.href}
                    className="contato-canal"
                    {...(canal.href.startsWith("http") ? { target: "_blank", rel: "noopener noreferrer" } : {})}
                  >
                    <span className="contato-canal__icon">{canal.icon}</span>
                    <span>
                      <span className="contato-canal__label">{canal.label}</span>
                      <span className="contato-canal__valor">{canal.valor}</span>
                    </span>
                  </a>
                </li>
              ))}
            </ul>
          </aside>
        </div>
      </section>
    </div>
  )
}
