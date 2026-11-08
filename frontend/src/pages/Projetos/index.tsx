import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { Project, ProgramCase } from "../../types"
import PageHero from "../../components/PageHero"
import ProjetoCard from "../../components/ProjetoCard"
import { ArrowRightIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useProgramas from "../../hooks/useProgramas"
import useSiteConfig from "../../hooks/useSiteConfig"
import useTextos from "../../hooks/useTextos"
import "./index.css"

export default function Projetos() {
  const config = useSiteConfig()
  const t = useTextos()
  usePageTitle(t("projetos.eyebrow"), config.projects_lead)
  const programas = useProgramas()
  const [cases, setCases] = useState<ProgramCase[]>([])
  const [outrosProjetos, setOutrosProjetos] = useState<Project[]>([])

  useEffect(() => {
    api.getProgramCases().then(setCases).catch(() => setCases([]))
    // Os projetos de um programa aparecem na página dele; aqui ficam os que
    // estão sem programa, como visitas e capacitações com parceiros.
    api
      .getProjects()
      .then((data: Project[]) => setOutrosProjetos(data.filter((p) => !p.program)))
      .catch(() => setOutrosProjetos([]))
  }, [])

  // A seção de cases leva ao programa escolhido em Configuração do site. Sem
  // slug, ou com um slug que não existe mais, a seção não aparece.
  const slugDestaque = config.featured_program_slug
  const programaDestaque = programas.find((p) => p.slug === slugDestaque)
  const casesDestaque = cases.filter((c) => c.program === slugDestaque)

  return (
    <div className="projetos-page">
      <PageHero
        eyebrow={t("projetos.eyebrow")}
        title={<>{t("projetos.titulo")} <span className="destaque">{t("projetos.titulo_destaque")}</span></>}
        lead={config.projects_lead}
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
              <p className="eyebrow">{t("projetos.outros_eyebrow")}</p>
              <h2 className="section-title">{t("projetos.outros_titulo")}</h2>
            </div>
            <div className="grid grid--2">
              {outrosProjetos.map((projeto) => (
                <ProjetoCard projeto={projeto} key={projeto.id} />
              ))}
            </div>
          </div>
        </section>
      )}

      {programaDestaque && casesDestaque.length > 0 && (
        <section className={`section${outrosProjetos.length > 0 ? "" : " section--muted"}`}>
          <div className="container projetos-cases">
            <div>
              <p className="eyebrow">{t("projetos.cases_eyebrow")}</p>
              <h2 className="section-title">{t(casesDestaque.length === 1 ? "projetos.cases_titulo_um" : "projetos.cases_titulo_varios", { programa: programaDestaque.label, n: casesDestaque.length })}</h2>
            </div>
            <Link to={`/projetos/${programaDestaque.slug}#cases`} className="btn btn--primary">
              {t("projetos.cases_botao")}
              <ArrowRightIcon />
            </Link>
          </div>
        </section>
      )}
    </div>
  )
}
