import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { Project, SuccessCase } from "../../types"
import PageHero from "../../components/PageHero"
import ProjetoCard from "../../components/ProjetoCard"
import { ArrowRightIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useProgramas from "../../hooks/useProgramas"
import "./index.css"

export default function Projetos() {
  usePageTitle("Projetos", "Como formamos consultores, do primeiro semestre na entidade aos cases reais resolvidos ao longo da Jornada do Consultor.")
  const programas = useProgramas()
  const [cases, setCases] = useState<SuccessCase[]>([])
  const [outrosProjetos, setOutrosProjetos] = useState<Project[]>([])

  useEffect(() => {
    api.getSuccessCases().then(setCases).catch(() => setCases([]))
    // Os projetos de um programa aparecem na página dele; aqui ficam os que
    // não pertencem a nenhum, como visitas e capacitações com parceiros.
    api
      .getProjects()
      .then((data: Project[]) => setOutrosProjetos(data.filter((p) => !p.category)))
      .catch(() => setOutrosProjetos([]))
  }, [])

  return (
    <div className="projetos-page">
      <PageHero
        eyebrow="Projetos"
        title={<>Programas e <span className="destaque">cases</span></>}
        lead="Como formamos consultores, do primeiro semestre na entidade aos cases reais resolvidos ao longo da Jornada do Consultor."
      />

      <section className="section">
        <div className="container">
          <ol className="projetos-list">
            {programas.map((programa, index) => (
              <li key={programa.slug}>
                <Link to={`/projetos/${programa.slug}`} className="projetos-item">
                  <span className="projetos-item__index">{String(index + 1).padStart(2, "0")}</span>
                  <div className="projetos-item__heading">
                    <h2 className="projetos-item__nome">{programa.label}</h2>
                    <p className="projetos-item__tipo">{programa.subtitle}</p>
                  </div>
                  <p className="projetos-item__descricao">{programa.description}</p>
                  <span className="projetos-item__arrow" aria-hidden="true">
                    <ArrowRightIcon size={20} />
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {outrosProjetos.length > 0 && (
        <section className="section section--muted" id="outros-projetos">
          <div className="container">
            <div className="section-head">
              <p className="eyebrow">Além dos programas</p>
              <h2 className="section-title">Outros projetos</h2>
            </div>
            <div className="grid grid--2">
              {outrosProjetos.map((projeto) => (
                <ProjetoCard projeto={projeto} key={projeto.id} />
              ))}
            </div>
          </div>
        </section>
      )}

      {cases.length > 0 && (
        <section className={`section${outrosProjetos.length > 0 ? "" : " section--muted"}`}>
          <div className="container projetos-cases">
            <div>
              <p className="eyebrow">Cases resolvidos</p>
              <h2 className="section-title">{cases.length} cases na Jornada do Consultor</h2>
            </div>
            <Link to="/projetos/jornada-do-consultor#cases" className="btn btn--primary">
              Ver os cases
              <ArrowRightIcon />
            </Link>
          </div>
        </section>
      )}
    </div>
  )
}
