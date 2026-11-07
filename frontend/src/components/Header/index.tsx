import "./index.css";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";
import logoBranca from "../../images/logo-icc-branca.png";
import useProgramas from "../../hooks/useProgramas";
import useDiretorias from "../../hooks/useDiretorias";
import { ChevronDownIcon, CloseIcon, GitHubIcon, InstagramIcon, LinkedInIcon, MenuIcon } from "../Icons";
import { REDES } from "../../redes";

const COMPACT_THRESHOLD = 40;

type NavItem = {
  label: string;
  to: string;
  children?: { label: string; to: string }[];
};

const NAV: NavItem[] = [
  { label: "Nossa Equipe", to: "/equipe" },
  { label: "Parceiros", to: "/parceiros" },
  { label: "Projetos", to: "/projetos" },
  { label: "Artigos", to: "/artigos" },
  { label: "Contato", to: "/contato" },
];

export default function Header() {
  const headerRef = useRef<HTMLElement>(null);
  const barRef = useRef<HTMLDivElement>(null);
  const location = useLocation();
  const programas = useProgramas();
  const diretorias = useDiretorias();
  // O submenu de Projetos vem do banco, então só aparece depois que a lista
  // chega; até lá o item continua navegável, levando ao índice.
  const nav = useMemo(
    () =>
      NAV.map((item) => {
        if (item.to === "/projetos" && programas.length > 0) {
          return { ...item, children: programas.map((p) => ({ label: p.label, to: `/projetos/${p.slug}` })) };
        }
        if (item.to === "/equipe" && diretorias.length > 0) {
          return { ...item, children: diretorias.map((d) => ({ label: d.name, to: `/equipe#${d.slug}` })) };
        }
        return item;
      }),
    [programas, diretorias]
  );
  const [compact, setCompact] = useState(false);
  // Guardam em qual página/navegação o estado vale, então trocar de página
  // "reseta" os dois sem precisar de setState dentro de effect.
  const [heroVisibleAt, setHeroVisibleAt] = useState<string | null>(
    location.pathname === "/" ? "/" : null
  );
  const [menuOpenAt, setMenuOpenAt] = useState<string | null>(null);
  const solid = heroVisibleAt !== location.pathname;
  const menuOpen = menuOpenAt === location.key;

  // Encolhe o header assim que a página começa a rolar.
  useEffect(() => {
    const onScroll = () => {
      const shouldBeCompact = window.scrollY > COMPACT_THRESHOLD;
      setCompact((prev) => (prev === shouldBeCompact ? prev : shouldBeCompact));
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [location.pathname]);

  // Mantém --header-height atualizada (o resto do site usa isso pra saber
  // quanto de padding-top precisa, já que o header é fixo).
  useEffect(() => {
    const el = barRef.current;
    if (!el) return;
    const updateHeight = () => {
      document.documentElement.style.setProperty("--header-height", `${el.offsetHeight}px`);
    };
    updateHeight();
    const observer = new ResizeObserver(updateHeight);
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  // Transparente enquanto o fim do hero (#hero-sentinel, só existe na Home)
  // ainda não passou por trás do header; sólido no resto do tempo.
  useEffect(() => {
    const sentinel = document.getElementById("hero-sentinel");
    if (!sentinel) return;
    const path = location.pathname;
    const headerHeight = barRef.current?.offsetHeight ?? 0;
    const observer = new IntersectionObserver(
      ([entry]) => setHeroVisibleAt(entry.isIntersecting ? path : null),
      { rootMargin: `-${headerHeight}px 0px 0px 0px` }
    );
    observer.observe(sentinel);
    return () => observer.disconnect();
  }, [location.pathname]);

  // O menu mobile fecha sozinho ao navegar (location.key muda) e trava a
  // rolagem da página enquanto aberto.
  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  const classes = [
    "header",
    solid || menuOpen ? "header--solid" : "",
    compact ? "header--compact" : "",
    menuOpen ? "header--open" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <header className={classes} ref={headerRef}>
      <div className="header__bar" ref={barRef}>
        <Link to="/" className="header__logo" aria-label="Liga Insper Consulting Club, página inicial">
          <img src={logoBranca} alt="" />
        </Link>

        <nav className="header__nav" aria-label="Navegação principal">
          <ul className="header__menu">
            {nav.map((item) => (
              <li key={item.to} className={item.children ? "header__item header__item--dropdown" : "header__item"}>
                <NavLink to={item.to} className="header__link">
                  {item.label}
                  {item.children && <ChevronDownIcon size={10} />}
                </NavLink>
                {item.children && (
                  <ul className="header__dropdown">
                    {item.children.map((child) => (
                      <li key={child.to}>
                        <Link to={child.to} className="header__dropdown-link">
                          {child.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </nav>

        <div className="header__actions">
          <a href={REDES.instagram} target="_blank" rel="noopener noreferrer" className="header__social" aria-label="Instagram do ICC">
            <InstagramIcon size={18} />
          </a>
          <a href={REDES.linkedin} target="_blank" rel="noopener noreferrer" className="header__social" aria-label="LinkedIn do ICC">
            <LinkedInIcon size={17} />
          </a>
          <a href={REDES.github} target="_blank" rel="noopener noreferrer" className="header__social" aria-label="GitHub do ICC">
            <GitHubIcon size={17} />
          </a>
          <Link to="/processo" className="header__cta">
            Seja membro
          </Link>
          <button
            type="button"
            className="header__toggle"
            aria-expanded={menuOpen}
            aria-controls="menu-mobile"
            aria-label={menuOpen ? "Fechar menu" : "Abrir menu"}
            onClick={() => setMenuOpenAt(menuOpen ? null : location.key)}
          >
            {menuOpen ? <CloseIcon /> : <MenuIcon />}
          </button>
        </div>
      </div>

      <div id="menu-mobile" className="header__mobile" hidden={!menuOpen}>
        <ul className="header__mobile-list">
          {nav.map((item) => (
            <li key={item.to}>
              <NavLink to={item.to} end className="header__mobile-link">
                {item.label}
              </NavLink>
              {item.children && (
                <ul className="header__mobile-sub">
                  {item.children.map((child) => (
                    <li key={child.to}>
                      <Link to={child.to}>{child.label}</Link>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
        <div className="header__mobile-footer">
          <Link to="/processo" className="btn btn--light">
            Seja membro
          </Link>
          <div className="header__mobile-social">
            <a href={REDES.instagram} target="_blank" rel="noopener noreferrer" aria-label="Instagram do ICC">
              <InstagramIcon size={20} />
            </a>
            <a href={REDES.linkedin} target="_blank" rel="noopener noreferrer" aria-label="LinkedIn do ICC">
              <LinkedInIcon size={19} />
            </a>
            <a href={REDES.github} target="_blank" rel="noopener noreferrer" aria-label="GitHub do ICC">
              <GitHubIcon size={19} />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}
