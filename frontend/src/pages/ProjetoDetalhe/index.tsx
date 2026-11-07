import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { Activity, Project, SuccessCase, SuccessCaseParticipant } from "../../types"
import PageHero from "../../components/PageHero"
import ProjetoCard from "../../components/ProjetoCard"
import NaoEncontrada from "../NaoEncontrada"
import { ArrowRightIcon, CheckIcon, ExternalIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useProgramas from "../../hooks/useProgramas"
import "./index.css"

function Pessoas({ pessoas }: { pessoas: SuccessCaseParticipant[] }) {
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

export default function ProjetoDetalhe() {
  const { slug } = useParams()
  const programas = useProgramas()
  const [componentes, setComponentes] = useState<Activity[]>([])
  const [cases, setCases] = useState<SuccessCase[]>([])
  const [projetos, setProjetos] = useState<Project[]>([])

  const programa = programas.find((p) => p.slug === slug)
  usePageTitle(programa?.label, programa?.description)

  useEffect(() => {
    if (!slug) return
    api.getActivities(slug).then(setComponentes).catch(() => setComponentes([]))
    api.getSuccessCases(slug).then(setCases).catch(() => setCases([]))
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

  return (
    <div className="projeto-page">
      <PageHero
        back={{ to: "/projetos", label: "Todos os projetos" }}
        eyebrow={programa.subtitle}
        title={programa.label}
        lead={programa.description}
      >
        {programa.signup_url && (
          <a href={programa.signup_url} target="_blank" rel="noopener noreferrer" className="btn btn--primary projeto-page__cta">
            Formulário de inscrição
            <ExternalIcon />
          </a>
        )}
      </PageHero>

      {componentes.length > 0 && (
        <section className="section">
          <div className="container">
            <div className="section-head">
              <h2 className="section-title">Como funciona</h2>
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
              <h2 className="section-title">Benefícios</h2>
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
              <h2 className="section-title">Projetos</h2>
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
              <h2 className="section-title">Cases resolvidos</h2>
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
                          <dt>Banca avaliadora</dt>
                          <dd>{c.panel.join(", ")}</dd>
                        </div>
                      )}
                      {equipe.length > 0 && (
                        <div>
                          <dt>Grupo vencedor</dt>
                          <dd><Pessoas pessoas={equipe} /></dd>
                        </div>
                      )}
                      {mentores.length > 0 && (
                        <div>
                          <dt>Mentor(a)</dt>
                          <dd><Pessoas pessoas={mentores} /></dd>
                        </div>
                      )}
                    </dl>

                    {c.award && (
                      <p className="case-card__premiacao">
                        <strong>Premiação</strong>
                        {c.award}
                      </p>
                    )}

                    {c.publication_url && (
                      <a href={c.publication_url} target="_blank" rel="noopener noreferrer" className="link-arrow case-card__link">
                        Ver post do case
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
            <p className="eyebrow">Projetos</p>
            <h2 className="section-title">Outros programas</h2>
          </div>
          <div className="grid grid--3">
            {outros.map((outro) => (
              <Link to={`/projetos/${outro.slug}`} className="card projeto-outro" key={outro.slug}>
                <h3 className="projeto-outro__nome">{outro.label}</h3>
                <p className="projeto-outro__tipo">{outro.subtitle}</p>
                <span className="link-arrow">
                  Saiba mais
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
