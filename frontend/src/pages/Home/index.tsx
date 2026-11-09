import { Fragment, useEffect, useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { HomeSection, Member, Statistic, Partner } from "../../types"
import reuniaoInaugural from "../../images/reuniao-inaugural.jpg"
import logoBranca from "../../images/logo-icc-branca.png"
import useProgramas from "../../hooks/useProgramas"
import useSiteConfig from "../../hooks/useSiteConfig"
import useTextos from "../../hooks/useTextos"
import MemberCard from "../../components/MemberCard"
import { ArrowRightIcon, ChevronDownIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import "./index.css"

// Na Home aparece só a liderança. O corte usa a prioridade do cargo, que o
// model guarda e o admin controla (0 para presidência, 2 para diretoria, daí
// para cima o restante), e não palavras dentro do texto do cargo: renomear um
// cargo no admin não muda em silêncio quem aparece aqui.
const PRIORIDADE_LIDERANCA = 2

function eLideranca(member: Member): boolean {
  return member.position_power !== null && member.position_power <= PRIORIDADE_LIDERANCA
}

// As seções depois da Apresentação vêm da API, na ordem e com a visibilidade que o editor escolheu. O fundo
// alterna entre claro e cinza pela posição, e não por seção: mover uma seção não deixa duas iguais lado a lado.
// Estatísticas e Chamada final têm estilo próprio e ficam fora dessa alternância.
const ALTERNAM_O_FUNDO = new Set(["aviso", "quem_somos", "missao", "programas", "equipe", "parceiros"])

function fundoDaPosicao(secoes: HomeSection[], indice: number): string {
  const antes = secoes.slice(0, indice).filter((s) => ALTERNAM_O_FUNDO.has(s.key)).length
  return antes % 2 === 0 ? "section" : "section section--muted"
}

export default function Home() {
  usePageTitle()
  const config = useSiteConfig()
  const t = useTextos()
  const programas = useProgramas()
  const [members, setMembers] = useState<Member[]>([])
  const [statistics, setStatistics] = useState<Statistic[]>([])
  const [partners, setPartners] = useState<Partner[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getMembers(), api.getStatistics(), api.getPartners()])
      .then(([membersData, statsData, partnersData]) => {
        setMembers((membersData as Member[]).filter(eLideranca))
        setStatistics(statsData)
        setPartners(partnersData)
      })
      .finally(() => setLoading(false))
  }, [])

  // Seção sem nada para mostrar (sem estatísticas, sem parceiros) some, e não ocupa lugar na alternância do fundo.
  const temConteudo = (chave: string) =>
    chave === "estatisticas" ? statistics.length > 0 : chave === "parceiros" ? partners.length > 0 : true
  const CONHECIDAS = ["aviso", "quem_somos", "estatisticas", "missao", "programas", "equipe", "parceiros", "chamada_final"]
  const secoes = config.home_sections.filter((s) => CONHECIDAS.includes(s.key) && temConteudo(s.key))

  const desenha = (secao: HomeSection, fundo: string): ReactNode => {
    switch (secao.key) {
      case "aviso":
        return (
          <section className={`${fundo} home-notice`}>
            <div className="container">
              {t("home.aviso_titulo") && <h2 className="section-title">{t("home.aviso_titulo")}</h2>}
              <p className="home-notice__text">{t("home.aviso_texto")}</p>
              {t("home.aviso_botao") && secao.button_path && (
                <div className="home-notice__actions">
                  {secao.button_external ? (
                    <a href={secao.button_path} className="btn btn--primary" target="_blank" rel="noopener noreferrer">
                      {t("home.aviso_botao")}
                      <ArrowRightIcon />
                    </a>
                  ) : (
                    <Link to={secao.button_path} className="btn btn--primary">
                      {t("home.aviso_botao")}
                      <ArrowRightIcon />
                    </Link>
                  )}
                </div>
              )}
            </div>
          </section>
        )
      case "quem_somos":
        return (
          <section className={`${fundo} home-about`}>
            <div className="container home-about__grid">
              <div>
                <p className="eyebrow">{t("home.sobre_eyebrow")}</p>
                <h2 className="section-title">
                  {t("home.sobre_titulo")}
                  {t("home.sobre_titulo_destaque") && (
                    <>
                      {" "}
                      <span className="destaque">{t("home.sobre_titulo_destaque")}</span>
                    </>
                  )}
                </h2>
                <p className="home-about__text">{t("home.sobre_texto")}</p>
              </div>
              <figure className="home-about__figure">
                <img src={config.home_about_photo_url ?? reuniaoInaugural} alt={config.home_about_photo_alt} />
              </figure>
            </div>
          </section>
        )
      case "estatisticas":
        return (
          <section className="home-stats" aria-label="Conquistas">
            <div className="container home-stats__grid">
              {statistics.map((stat) => (
                <div className="home-stats__item" key={stat.id}>
                  <span className="home-stats__value">{stat.value}</span>
                  <span className="home-stats__label">{stat.description}</span>
                </div>
              ))}
            </div>
          </section>
        )
      case "missao":
        return (
          <section className={fundo}>
            <div className="container home-mission">
              <div className="home-mission__main">
                <p className="eyebrow">{t("home.missao_eyebrow")}</p>
                <p className="home-mission__statement">{t("home.missao_texto")}</p>
              </div>
              <div className="home-mission__details">
                <div className="home-mission__detail">
                  <h3>{t("home.missao_como_titulo")}</h3>
                  <p>{t("home.missao_como_texto")}</p>
                </div>
                <div className="home-mission__detail">
                  <h3>{t("home.missao_meta_titulo")}</h3>
                  <p>{t("home.missao_meta_texto")}</p>
                </div>
              </div>
            </div>
          </section>
        )
      case "programas":
        return (
          <section className={fundo}>
            <div className="container">
              <div className="section-head section-head--row">
                <div>
                  <p className="eyebrow">{t("home.programas_eyebrow")}</p>
                  <h2 className="section-title">{t("home.programas_titulo")}</h2>
                </div>
                <Link to="/projetos" className="link-arrow">
                  {t("home.programas_link")}
                  <ArrowRightIcon />
                </Link>
              </div>

              <div className="grid grid--4">
                {programas.map((programa, index) => (
                  <Link to={`/projetos/${programa.slug}`} className="card home-program" key={programa.slug}>
                    <span className="home-program__index">{String(index + 1).padStart(2, "0")}</span>
                    <h3 className="home-program__name">{programa.label}</h3>
                    <p className="home-program__type">{programa.subtitle}</p>
                    <span className="link-arrow home-program__more">
                      {t("home.programa_card_link")}
                      <ArrowRightIcon />
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          </section>
        )
      case "equipe":
        return (
          <section className={fundo}>
            <div className="container">
              <div className="section-head section-head--row">
                <div>
                  <p className="eyebrow">{t("home.membros_eyebrow")}</p>
                  <h2 className="section-title">{t("home.membros_titulo")}</h2>
                </div>
                <Link to="/equipe" className="link-arrow">
                  {t("home.membros_link")}
                  <ArrowRightIcon />
                </Link>
              </div>

              {loading ? (
                <p className="loading">Carregando equipe...</p>
              ) : (
                <div className="grid grid--4 home-team">
                  {members.map((member) => (
                    <MemberCard key={member.id} member={member} />
                  ))}
                </div>
              )}
            </div>
          </section>
        )
      case "parceiros":
        return (
          <section className={fundo}>
            <div className="container">
              <div className="section-head section-head--row">
                <div>
                  <p className="eyebrow">{t("home.parceiros_eyebrow")}</p>
                  <h2 className="section-title">{t("home.parceiros_titulo")}</h2>
                </div>
                <Link to="/parceiros" className="link-arrow">
                  {t("home.parceiros_link")}
                  <ArrowRightIcon />
                </Link>
              </div>

              <div className="home-partners-carousel">
                <ul className="home-partners-carousel__track">
                  {/* Lista duplicada para o loop não ter emenda; a cópia fica fora do leitor de tela e do Tab */}
                  {[...partners, ...partners].map((partner, i) => {
                    const copia = i >= partners.length
                    return (
                      <li key={`${partner.id}-${i}`} aria-hidden={copia || undefined}>
                        <Link
                          to={`/parceiros/${partner.id}`}
                          className="home-partners__logo"
                          title={partner.name}
                          tabIndex={copia ? -1 : undefined}
                        >
                          {partner.logo_url ? (
                            <img src={partner.logo_url} alt={partner.name} loading="lazy" />
                          ) : (
                            <span>{partner.name}</span>
                          )}
                        </Link>
                      </li>
                    )
                  })}
                </ul>
              </div>
            </div>
          </section>
        )
      case "chamada_final":
        return (
          <section className="home-cta">
            <div className="container home-cta__inner">
              <h2 className="home-cta__title">{t("home.cta_titulo")}</h2>
              <div className="home-cta__actions">
                <Link to="/processo" className="btn btn--light">
                  {t("home.cta_botao_principal")}
                  <ArrowRightIcon />
                </Link>
                <Link to="/contato" className="btn btn--ghost-light">
                  {t("home.cta_botao_secundario")}
                </Link>
              </div>
            </div>
          </section>
        )
      default:
        return null
    }
  }

  return (
    <div className="home">
      <section className="home-hero">
        <div className="home-hero__inner">
          <img
            src={config.logo_url ?? logoBranca}
            alt={config.site_name}
            className="home-hero__logo"
            width={733}
            height={410}
            fetchPriority="high"
          />
          <h1 className="home-hero__title">{t("home.hero_titulo")}</h1>
        </div>
        <a href="#inicio-conteudo" className="home-hero__scroll" aria-label="Rolar para o conteúdo">
          <ChevronDownIcon size={22} />
        </a>
      </section>
      {/* Marca onde o hero termina; o Header observa isso pra saber quando
          ficar sólido (ver components/Header). */}
      <div id="hero-sentinel" />

      <section className="home-intro" id="inicio-conteudo">
        <div className="container home-intro__inner">
          <p className="home-intro__statement">{t("home.hero_frase")}</p>
          <div className="home-intro__actions">
            <Link to="/processo" className="btn btn--primary">
              {t("home.hero_botao_principal")}
              <ArrowRightIcon />
            </Link>
            <Link to="/projetos" className="btn btn--secondary">
              {t("home.hero_botao_secundario")}
            </Link>
          </div>
        </div>
      </section>

      {secoes.map((secao, i) => (
        <Fragment key={secao.key}>{desenha(secao, fundoDaPosicao(secoes, i))}</Fragment>
      ))}
    </div>
  )
}
