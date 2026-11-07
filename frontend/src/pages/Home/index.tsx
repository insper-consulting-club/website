import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { Member, Statistic, Partner } from "../../types"
import reuniaoInaugural from "../../images/reuniao-inaugural.jpg"
import logoBranca from "../../images/logo-icc-branca.png"
import useProgramas from "../../hooks/useProgramas"
import MemberCard from "../../components/MemberCard"
import { ArrowRightIcon, ChevronDownIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import "./index.css"

// Conteúdo institucional estático, extraído de site-data/icc.json
// (sobre.missaoEProposito). Não há model de backend para isso.
const MISSAO = {
  missao:
    "Conectar alunos do Insper ao mercado de consultoria, desenvolvendo as competências técnicas e comportamentais exigidas pelas principais firmas do setor.",
  comoPreparamos:
    "Treinamento para processos seletivos (GMAT, Verbal, Data e Fit Interview) e capacitação prática na resolução de cases reais de negócio.",
  ondeQueremosChegar:
    "Consolidar o ICC como referência em consultoria entre os clubes estudantis do Brasil e expandir a atuação para tecnologia e empreendedorismo.",
}

// Na Home aparece só a liderança. O corte usa a prioridade do cargo, que o
// model guarda e o admin controla (0 para presidência, 2 para diretoria, daí
// para cima o restante), e não palavras dentro do texto do cargo: renomear um
// cargo no admin não muda em silêncio quem aparece aqui.
const PRIORIDADE_LIDERANCA = 2

function eLideranca(member: Member): boolean {
  return member.position_power !== null && member.position_power <= PRIORIDADE_LIDERANCA
}

export default function Home() {
  usePageTitle()
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

  return (
    <div className="home">
      <section className="home-hero">
        <div className="home-hero__inner">
          <img
            src={logoBranca}
            alt="Liga Insper Consulting Club"
            className="home-hero__logo"
            width={733}
            height={410}
            fetchPriority="high"
          />
          <h1 className="home-hero__title">O futuro consultor começa no ICC</h1>
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
          <p className="home-intro__statement">
            Preparamos nossos membros para os processos seletivos mais exigentes do mercado.
          </p>
          <div className="home-intro__actions">
            <Link to="/processo" className="btn btn--primary">
              Seja membro
              <ArrowRightIcon />
            </Link>
            <Link to="/projetos" className="btn btn--secondary">
              Conheça os projetos
            </Link>
          </div>
        </div>
      </section>

      <section className="section home-about">
        <div className="container home-about__grid">
          <div>
            <p className="eyebrow">Quem somos</p>
            <h2 className="section-title">
              Mais do que um clube, somos um ambiente de formação{" "}
              <span className="destaque">para futuros consultores.</span>
            </h2>
            <p className="home-about__text">
              A Liga Insper Consulting Club é uma organização estudantil
              fundada em 2020, dedicada ao desenvolvimento de futuros
              consultores. Ao longo do semestre, promovemos capacitações,
              resolução de cases, visitas corporativas e iniciativas que
              aproximam nossos membros da realidade das principais empresas
              do mercado.
            </p>
          </div>
          <figure className="home-about__figure">
            <img src={reuniaoInaugural} alt="Membros da Liga Insper Consulting Club na reunião inaugural" />
          </figure>
        </div>
      </section>

      {statistics.length > 0 && (
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
      )}

      <section className="section section--muted">
        <div className="container home-mission">
          <div className="home-mission__main">
            <p className="eyebrow">Missão</p>
            <p className="home-mission__statement">{MISSAO.missao}</p>
          </div>
          <div className="home-mission__details">
            <div className="home-mission__detail">
              <h3>Como preparamos</h3>
              <p>{MISSAO.comoPreparamos}</p>
            </div>
            <div className="home-mission__detail">
              <h3>Onde queremos chegar</h3>
              <p>{MISSAO.ondeQueremosChegar}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-head section-head--row">
            <div>
              <p className="eyebrow">Projetos</p>
              <h2 className="section-title">Nossos programas e cases</h2>
            </div>
            <Link to="/projetos" className="link-arrow">
              Ver todos os projetos
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
                  Saiba mais
                  <ArrowRightIcon />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="section section--muted">
        <div className="container">
          <div className="section-head section-head--row">
            <div>
              <p className="eyebrow">Membros</p>
              <h2 className="section-title">Quem constrói o clube</h2>
            </div>
            <Link to="/equipe" className="link-arrow">
              Ver equipe completa
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

      {partners.length > 0 && (
        <section className="section">
          <div className="container">
            <div className="section-head section-head--row">
              <div>
                <p className="eyebrow">Parceiros</p>
                <h2 className="section-title">Empresas que confiam no nosso trabalho</h2>
              </div>
              <Link to="/parceiros" className="link-arrow">
                Ver todos os parceiros
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
      )}

      <section className="home-cta">
        <div className="container home-cta__inner">
          <h2 className="home-cta__title">Pronto para dar o próximo passo na sua carreira?</h2>
          <div className="home-cta__actions">
            <Link to="/processo" className="btn btn--light">
              Faça parte do ICC
              <ArrowRightIcon />
            </Link>
            <Link to="/contato" className="btn btn--ghost-light">
              Fale com a gente
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
