import { Link } from "react-router-dom";
import "./index.css";
import logoBranca from "../../images/logo-icc-branca.png";
import useProgramas from "../../hooks/useProgramas";
import { GitHubIcon, InstagramIcon, LinkedInIcon, MailIcon } from "../Icons";
import { REDES } from "../../redes";

// O admin fica no backend, no mesmo endereço da API sem o "/api"
// (local: localhost:8000/admin/; produção: icc-backend…onrender.com/admin/).
const ADMIN_URL = import.meta.env.VITE_API_URL.replace(/\/api\/?$/, "/admin/")
const NAVEGACAO = [
  { label: "Nossa Equipe", to: "/equipe" },
  { label: "Parceiros", to: "/parceiros" },
  { label: "Projetos", to: "/projetos" },
  { label: "Artigos", to: "/artigos" },
  { label: "Seja membro", to: "/processo" },
  { label: "Contato", to: "/contato" },
];

export default function Footer() {
  const programas = useProgramas();

  return (
    <footer className="footer">
      <div className="container footer__grid">
        <div className="footer__brand">
          <Link to="/" aria-label="Liga Insper Consulting Club, página inicial">
            <img src={logoBranca} alt="" className="footer__logo" />
          </Link>
          <p className="footer__tagline">
            Mais do que um clube, somos um ambiente de formação para futuros
            consultores.
          </p>
        </div>

        <nav className="footer__col" aria-label="Navegação do rodapé">
          <h2 className="footer__title">Navegação</h2>
          <ul className="footer__list">
            {NAVEGACAO.map((item) => (
              <li key={item.to}>
                <Link to={item.to}>{item.label}</Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="footer__col">
          <h2 className="footer__title">Programas</h2>
          <ul className="footer__list">
            {programas.map((programa) => (
              <li key={programa.slug}>
                <Link to={`/projetos/${programa.slug}`}>{programa.label}</Link>
              </li>
            ))}
          </ul>
        </div>

        <div className="footer__col">
          <h2 className="footer__title">Contato</h2>
          <ul className="footer__list">
            <li>
              <a href={`mailto:${REDES.email}`} className="footer__contact">
                <MailIcon size={16} />
                {REDES.email}
              </a>
            </li>
            <li>
              <a href={REDES.instagram} target="_blank" rel="noopener noreferrer" className="footer__contact">
                <InstagramIcon size={16} />
                Instagram
              </a>
            </li>
            <li>
              <a href={REDES.linkedin} target="_blank" rel="noopener noreferrer" className="footer__contact">
                <LinkedInIcon size={15} />
                LinkedIn
              </a>
            </li>
            <li>
              <a href={REDES.github} target="_blank" rel="noopener noreferrer" className="footer__contact">
                <GitHubIcon size={15} />
                GitHub
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="container footer__bottom">
        <span>© {new Date().getFullYear()} Liga Insper Consulting Club</span>
        <div className="footer__bottom-links">
          <Link to="/politica-de-privacidade">Política de Privacidade</Link>
          <a href={ADMIN_URL}>Área administrativa</a>
        </div>
      </div>
    </footer>
  );
}
