import PageHero from "../../components/PageHero"
import { GitHubIcon, InstagramIcon, LinkedInIcon, MailIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import { REDES } from "../../redes"
import "./index.css"

const CANAIS = [
  {
    label: "E-mail",
    valor: REDES.email,
    href: `mailto:${REDES.email}`,
    icon: <MailIcon size={20} />,
  },
  {
    label: "Instagram",
    valor: "@insperconsultingclub",
    href: REDES.instagram,
    icon: <InstagramIcon size={20} />,
  },
  {
    label: "LinkedIn",
    valor: "Insper Consulting Club",
    href: REDES.linkedin,
    icon: <LinkedInIcon size={19} />,
  },
  {
    label: "GitHub",
    valor: "insper-consulting-club",
    href: REDES.github,
    icon: <GitHubIcon size={19} />,
  },
]

export default function Contato() {
  usePageTitle("Contato", "Entre em contato com o Insper Consulting Club")

  return (
    <div className="contato-page">
      <PageHero title="Contato" lead="Entre em contato com o Insper Consulting Club" />

      <section className="section">
        <div className="container contato-grid">
          <aside className="contato-canais">
            <h2 className="contato-canais__title">Canais oficiais</h2>
            <ul>
              {CANAIS.map((canal) => (
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
