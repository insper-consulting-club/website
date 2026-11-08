import { Link } from "react-router-dom";
import "./index.css";
import logoBranca from "../../images/logo-icc-branca.png";
import useProgramas from "../../hooks/useProgramas";
import { GitHubIcon, InstagramIcon, LinkedInIcon, MailIcon } from "../Icons";
import useSiteConfig from "../../hooks/useSiteConfig";
import LinkDoSite from "../LinkDoSite";
import useTextos from "../../hooks/useTextos";

// O admin fica no backend, no mesmo endereço da API sem o "/api"
// (local: localhost:8000/admin/; produção: icc-backend…onrender.com/admin/).
const ADMIN_URL = import.meta.env.VITE_API_URL.replace(/\/api\/?$/, "/admin/")

export default function Footer() {
  const t = useTextos();
  const programas = useProgramas();
  const config = useSiteConfig();
  const navegacao = config.nav_items.filter((item) => item.area === "menu" || item.area === "rodape");

  return (
    <footer className="footer">
      <div className="container footer__grid">
        <div className="footer__brand">
          <Link to="/" aria-label={`${config.site_name}, página inicial`}>
            <img src={config.logo_url ?? logoBranca} alt="" className="footer__logo" />
          </Link>
          <p className="footer__tagline">{config.footer_tagline}</p>
        </div>

        <nav className="footer__col" aria-label="Navegação do rodapé">
          <h2 className="footer__title">{t("rodape.navegacao")}</h2>
          <ul className="footer__list">
            {navegacao.map((item) => (
              <li key={item.id}>
                <LinkDoSite to={item.path} externo={item.external}>
                  {item.label}
                </LinkDoSite>
              </li>
            ))}
          </ul>
        </nav>

        <div className="footer__col">
          <h2 className="footer__title">{t("rodape.programas")}</h2>
          <ul className="footer__list">
            {programas.map((programa) => (
              <li key={programa.slug}>
                <Link to={`/projetos/${programa.slug}`}>{programa.label}</Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="footer__col">
          <h2 className="footer__title">{t("rodape.contato")}</h2>
          <ul className="footer__list">
            <li>
              <a href={`mailto:${config.email}`} className="footer__contact">
                <MailIcon size={16} />
                {config.email}
              </a>
            </li>
            <li>
              <a href={config.instagram_url} target="_blank" rel="noopener noreferrer" className="footer__contact">
                <InstagramIcon size={16} />
                Instagram
              </a>
            </li>
            <li>
              <a href={config.linkedin_url} target="_blank" rel="noopener noreferrer" className="footer__contact">
                <LinkedInIcon size={15} />
                LinkedIn
              </a>
            </li>
            <li>
              <a href={config.github_url} target="_blank" rel="noopener noreferrer" className="footer__contact">
                <GitHubIcon size={15} />
                GitHub
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="container footer__bottom">
        <span>© {new Date().getFullYear()} {config.site_name}</span>
        <div className="footer__bottom-links">
          <Link to="/politica-de-privacidade">{t("rodape.privacidade")}</Link>
          <a href={ADMIN_URL}>{t("rodape.admin")}</a>
        </div>
      </div>
    </footer>
  );
}
