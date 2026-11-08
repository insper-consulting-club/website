import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { Project, ProgramCase, ProgramCaseParticipant, ProgramComponent, ProgramContentBlock } from "../../types"
import PageHero from "../../components/PageHero"
import ProjetoCard from "../../components/ProjetoCard"
import TextoMarkdown from "../../components/TextoMarkdown"
import NaoEncontrada from "../NaoEncontrada"
import { ArrowRightIcon, CheckIcon, ExternalIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useProgramas from "../../hooks/useProgramas"
import useTextos from "../../hooks/useTextos"
import "./index.css"

function Pessoas({ pessoas }: { pessoas: ProgramCaseParticipant[] }) {
  return (
    <>
      {pessoas.map((pessoa, i) => (
        <span key={pessoa.member_id}>
          {i > 0 && ", "}
          {pessoa.linkedin ? (
            <a href={pessoa.linkedin} target="_blank" rel="noopener noreferrer" className="case-card__pessoa">
              {pessoa.name}
            </a>
          ) : (
            pessoa.name
          )}
        </span>
      ))}
    </>
  )
}

export default function Programa() {
  const t = useTextos()
  const { slug } = useParams()
  const programas = useProgramas()
  const [componentes, setComponentes] = useState<ProgramComponent[]>([])
  const [cases, setCases] = useState<ProgramCase[]>([])
  const [projetos, setProjetos] = useState<Project[]>([])
  // Guarda de qual programa são os blocos: ao trocar de programa, os do
  // anterior não aparecem na página nova enquanto a resposta não chega.
  const [blocosDe, setBlocosDe] = useState<{ slug: string; blocos: ProgramContentBlock[] } | null>(null)

  const programa = programas.find((p) => p.slug === slug)
  usePageTitle(programa?.label, programa?.description)

  useEffect(() => {
    if (!slug) return
    api
      .getProgram(slug)
      .then((data) => setBlocosDe({ slug, blocos: Array.isArray(data?.content_blocks) ? data.content_blocks : [] }))
      .catch(() => setBlocosDe({ slug, blocos: [] }))
    api.getComponents(slug).then(setComponentes).catch(() => setComponentes([]))
    api.getProgramCases(slug).then(setCases).catch(() => setCases([]))
    api.getProjects(slug).then(setProjetos).catch(() => setProjetos([]))
  }, [slug])

  // Enquanto a lista de programas não chega, ainda não dá para saber se o slug
  // existe: exibir a página de não encontrada aqui acusaria erro em toda
  // visita, antes da resposta.
  if (programas.length === 0) {
    return <p className="loading">Carregando...</p>
  }

  if (!programa) return <NaoEncontrada />

  const outros = programas.filter((p) => p.slug !== programa.slug)
  const blocos = blocosDe && blocosDe.slug === slug ? blocosDe.blocos : []

  return (
    <div className="projeto-page">
      <PageHero
        back={{ to: "/projetos", label: t("programa.voltar") }}
        eyebrow={programa.subtitle}
        title={programa.label}
        lead={programa.description}
      >
        {programa.signup_url && (
          <a href={programa.signup_url} target="_blank" rel="noopener noreferrer" className="btn btn--primary projeto-page__cta">
            {t("programa.botao_inscricao")}
            <ExternalIcon />
          </a>
        )}
      </PageHero>

      {blocos.length > 0 && (
        <section className="section">
          <div className="container programa-blocos">
            {blocos.map((bloco) => {
              const comImagem = Boolean(bloco.image_url)
              return (
                <div
                  className={`programa-bloco${comImagem ? ` programa-bloco--${bloco.image_align}` : ""}`}
                  key={bloco.id}
                >
                  <div className="programa-bloco__texto">
                    {bloco.title && <h2 className="section-title">{bloco.title}</h2>}
                    {bloco.text && <TextoMarkdown>{bloco.text}</TextoMarkdown>}
                  </div>
                  {comImagem && (
                    <figure className="programa-bloco__figura">
                      <img src={bloco.image_url ?? ""} alt={bloco.image_caption || bloco.title} loading="lazy" />
                      {bloco.image_caption && <figcaption>{bloco.image_caption}</figcaption>}
                    </figure>
                  )}
                </div>
              )
            })}
          </div>
        </section>
      )}

      {componentes.length > 0 && (
        <section className="section">
          <div className="container">
            <div className="section-head">
              <h2 className="section-title">{t("programa.como_funciona")}</h2>
            </div>
            <div className="grid grid--3">
              {componentes.map((componente, index) => (
                <article className="card projeto-componente" key={componente.id}>
                  <span className="projeto-componente__index">{String(index + 1).padStart(2, "0")}</span>
                  <h3 className="projeto-componente__nome">{componente.title}</h3>
                  <p className="projeto-componente__descricao">{componente.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>
      )}

      {programa.highlights.length > 0 && (
        <section className="section">
          <div className="container">
            <div className="section-head">
              <h2 className="section-title">{t("programa.beneficios")}</h2>
            </div>
            <ul className="grid grid--4 projeto-beneficios">
              {programa.highlights.map((beneficio) => (
                <li key={beneficio} className="projeto-beneficio">
                  <span className="projeto-beneficio__icon">
                    <CheckIcon size={18} />
                  </span>
                  {beneficio}
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      {projetos.length > 0 && (
        <section className="section" id="projetos">
          <div className="container">
            <div className="section-head">
              <p className="eyebrow">{programa.label}</p>
              <h2 className="section-title">{t("programa.projetos_titulo")}</h2>
            </div>
            <div className="grid grid--2">
              {projetos.map((projeto) => (
                <ProjetoCard projeto={projeto} key={projeto.id} />
              ))}
            </div>
          </div>
        </section>
      )}

      {cases.length > 0 && (
        <section className="section section--muted" id="cases">
          <div className="container">
            <div className="section-head">
              <p className="eyebrow">{programa.label}</p>
              <h2 className="section-title">{t("programa.cases_titulo")}</h2>
            </div>
            <div className="grid grid--2">
              {cases.map((c) => {
                const equipe = c.participants.filter((p) => p.role === "integrante")
                const mentores = c.participants.filter((p) => p.role === "mentor")
                return (
                  <article className="card case-card" key={c.id}>
                    <div className="case-card__meta">
                      <span className="tag">{c.semester}</span>
                      {c.title && <span className="tag tag--accent">{c.title}</span>}
                      <span className="case-card__area">{c.area}</span>
                    </div>

                    <h3 className="case-card__tema">{c.theme}</h3>

                    <dl className="case-card__dados">
                      {c.panel.length > 0 && (
                        <div>
                          <dt>{t("programa.case_banca")}</dt>
                          <dd>{c.panel.join(", ")}</dd>
                        </div>
                      )}
                      {equipe.length > 0 && (
                        <div>
                          <dt>{t("programa.case_grupo")}</dt>
                          <dd><Pessoas pessoas={equipe} /></dd>
                        </div>
                      )}
                      {mentores.length > 0 && (
                        <div>
                          <dt>{t("programa.case_mentor")}</dt>
                          <dd><Pessoas pessoas={mentores} /></dd>
                        </div>
                      )}
                    </dl>

                    {c.award && (
                      <p className="case-card__premiacao">
                        <strong>{t("programa.case_premiacao")}</strong>
                        {c.award}
                      </p>
                    )}

                    {c.publication_url && (
                      <a href={c.publication_url} target="_blank" rel="noopener noreferrer" className="link-arrow case-card__link">
                        {t("programa.case_link")}
                        <ExternalIcon />
                      </a>
                    )}
                  </article>
                )
              })}
            </div>
          </div>
        </section>
      )}

      <section className={`section${cases.length > 0 ? "" : " section--muted"}`}>
        <div className="container">
          <div className="section-head">
            <p className="eyebrow">{t("programa.outros_eyebrow")}</p>
            <h2 className="section-title">{t("programa.outros_titulo")}</h2>
          </div>
          <div className="grid grid--3">
            {outros.map((outro) => (
              <Link to={`/projetos/${outro.slug}`} className="card projeto-outro" key={outro.slug}>
                <h3 className="projeto-outro__nome">{outro.label}</h3>
                <p className="projeto-outro__tipo">{outro.subtitle}</p>
                <span className="link-arrow">
                  {t("programa.outros_link")}
                  <ArrowRightIcon />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
