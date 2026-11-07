import { useEffect, useState } from "react"
import { api } from "../../api"
import type { SelectionProcess } from "../../types"
import PageHero from "../../components/PageHero"
import { ArrowRightIcon, CheckIcon, ClockIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import { REDES } from "../../redes"
import "./index.css"

export default function Processo() {
  usePageTitle("Processo Seletivo", "Participe do processo seletivo e faça parte da Liga Insper Consulting Club")
  const [process, setProcess] = useState<SelectionProcess | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getSelectionProcess()
      .then((data) => setProcess(data && data.id ? data : null))
      .catch(() => setProcess(null))
      .finally(() => setLoading(false))
  }, [])

    // Só existe link quando há um processo com as inscrições abertas no admin;
  // em qualquer outro caso, a página mostra "inscrições encerradas".
  const linkInscricao = process?.registrations_open ? process.registration_url : ""

  const cta = linkInscricao ? (
    <div className="processo-cta">
      <h2 className="processo-cta__title">Inscrições abertas!</h2>
      <a href={linkInscricao} target="_blank" rel="noopener noreferrer" className="btn btn--light">
        Inscreva-se
        <ArrowRightIcon />
      </a>
    </div>
  ) : (
    <div className="processo-cta">
      <h2 className="processo-cta__title">Inscrições encerradas. Acompanhe nosso Instagram para saber quando abrirmos o próximo processo.</h2>
      <a href={REDES.instagram} target="_blank" rel="noopener noreferrer" className="btn btn--light">
        Seguir no Instagram
        <ArrowRightIcon />
      </a>
    </div>
  )



  return (
    <div className="processo-page">
      <PageHero
        eyebrow="Seja membro"
        title={process?.title || "Processo Seletivo"}
        lead="Participe do processo seletivo e faça parte da Liga Insper Consulting Club"
      />

      <section className="section">
        <div className="container">
          {loading ? (
            <p className="loading">Carregando...</p>
          ) : !process ? (
            <>
              <p className="state-message">
                <strong>Nenhum processo seletivo ativo no momento.</strong>
                Assim que abrirmos novas vagas, as inscrições aparecem aqui.
              </p>
              {cta}
            </>
          ) : (
            <>
              {process.stages.length > 0 && (
                <div className="processo-bloco">
                  <h2 className="section-title">Calendário</h2>
                  <ol className="processo-datas">
                    {process.stages.map((stage) => (
                      <li key={stage.id}>
                        <span className="processo-datas__data">{stage.date}</span>
                        <span className="processo-datas__label">{stage.label}</span>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {process.steps.length > 0 && (
                <div className="processo-bloco">
                  <div className="section-head">
                    <h2 className="section-title">Etapas do processo</h2>
                  </div>
                  <ol className="processo-etapas">
                    {process.steps.map((step) => (
                      <li key={step.id} className="processo-etapa">
                        <span className="processo-etapa__numero">{step.number}</span>
                        <div className="processo-etapa__conteudo">
                          <div className="processo-etapa__topo">
                            <h3 className="processo-etapa__titulo">{step.title}</h3>
                            {step.duration && (
                              <span className="processo-etapa__duracao">
                                <ClockIcon />
                                {step.duration}
                              </span>
                            )}
                          </div>
                          <p className="processo-etapa__descricao">{step.description}</p>
                          {step.image_url && <img src={step.image_url} alt="" className="processo-etapa__imagem" />}
                          {step.tips.length > 0 && (
                            <ul className="processo-etapa__dicas">
                              {step.tips.map((tip, i) => (
                                <li key={i}>{tip}</li>
                              ))}
                            </ul>
                          )}
                        </div>
                      </li>
                    ))}
                  </ol>
                </div>
              )}

              {process.requirements.length > 0 && (
                <div className="processo-bloco">
                  <div className="section-head">
                    <h2 className="section-title">Requisitos</h2>
                  </div>
                  <ul className="grid grid--2 processo-requisitos">
                    {process.requirements.map((req) => (
                      <li key={req.id} className="processo-requisito">
                        <span className="processo-requisito__icone">
                          {req.icon_url ? <img src={req.icon_url} alt="" /> : <CheckIcon />}
                        </span>
                        {req.text}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {process.materials.length > 0 && (
                <div className="processo-bloco">
                  <div className="section-head">
                    <h2 className="section-title">Materiais de preparação</h2>
                  </div>
                  <div className="grid grid--3">
                    {process.materials.map((material) => (
                      <div key={material.id} className="card">
                        <h3 className="processo-material__titulo">{material.title}</h3>
                        <ul className="processo-material__lista">
                          {material.items.map((item) => (
                            <li key={item.id}>{item.text}</li>
                          ))}
                        </ul>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {cta}
            </>
          )}
        </div>
      </section>
    </div>
  )
}
