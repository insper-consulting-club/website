import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import { api } from "../../api"
import type { ProjectDetail } from "../../types"
import PageHero from "../../components/PageHero"
import { ArrowLeftIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useTextos from "../../hooks/useTextos"
import "./index.css"

function formatDate(date: string) {
  // Ano/mês/dia separados: new Date("AAAA-MM-DD") seria meia-noite UTC,
  // que em Brasília já é o dia anterior.
  const [ano, mes, dia] = date.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
}

// No admin, os parágrafos de um bloco são separados por quebras de linha.
function paragrafos(texto: string) {
  return texto.split("\n").map((p) => p.trim()).filter(Boolean)
}

export default function Projeto() {
  const t = useTextos()
  const { id } = useParams<{ id: string }>()
  const [projeto, setProjeto] = useState<ProjectDetail | null>(null)
  const [loadedId, setLoadedId] = useState<string | undefined>()
  const loading = loadedId !== id
  usePageTitle(projeto?.title, projeto?.description)

  useEffect(() => {
    if (!id) return
    api
      .getProject(Number(id))
      .then((data: ProjectDetail) => setProjeto(data && data.id ? data : null))
      .catch(() => setProjeto(null))
      .finally(() => setLoadedId(id))
  }, [id])

  if (loading) return <p className="loading">Carregando...</p>

  if (!projeto) {
    return (
      <section className="section">
        <div className="container">
          <Link to="/projetos" className="back-link">
            <ArrowLeftIcon size={14} />
            {t("projeto.voltar")}
          </Link>
          <p className="state-message">
            <strong>{t("projeto.nao_encontrado_titulo")}</strong>
            {t("projeto.nao_encontrado_texto")}
          </p>
        </div>
      </section>
    )
  }

  const voltar = projeto.program
    ? { to: `/projetos/${projeto.program.slug}`, label: projeto.program.label }
    : { to: "/projetos", label: t("projeto.voltar") }
  // Evento de um dia só (visita, competição): mostra a data uma vez.
  const umDia = projeto.end_date === projeto.start_date
  const periodo = umDia
    ? formatDate(projeto.start_date)
    : projeto.end_date
      ? t("projeto.periodo_intervalo", { inicio: formatDate(projeto.start_date), fim: formatDate(projeto.end_date) })
      : t("projeto.periodo_desde", { inicio: formatDate(projeto.start_date) })

  return (
    <div className="projeto-detalhe">
      <PageHero back={voltar} eyebrow={projeto.program?.label} title={projeto.title} lead={projeto.description} />

      <section className="section">
        <div className="container projeto-detalhe__corpo">
          <dl className="projeto-detalhe__dados">
            <div>
              <dt>{umDia ? t("projeto.rotulo_data") : t("projeto.rotulo_periodo")}</dt>
              <dd>{periodo}</dd>
            </div>
            <div>
              <dt>{t("projeto.rotulo_situacao")}</dt>
              <dd>{projeto.end_date ? t("projeto.concluido") : t("projeto.em_andamento")}</dd>
            </div>
            {projeto.partners.length > 0 && (
              <div>
                <dt>{projeto.partners.length > 1 ? t("projeto.rotulo_parceiros") : t("projeto.rotulo_parceiro")}</dt>
                <dd>
                  {projeto.partners.map((parceiro, i) => (
                    <span key={parceiro.id}>
                      {i > 0 && ", "}
                      <Link to={`/parceiros/${parceiro.id}`}>{parceiro.name}</Link>
                    </span>
                  ))}
                </dd>
              </div>
            )}
          </dl>

          {projeto.content_blocks.map((bloco) => (
            <div className="projeto-detalhe__bloco" key={bloco.id}>
              {bloco.title && <h2>{bloco.title}</h2>}
              {paragrafos(bloco.text).map((p, i) => (
                <p key={i}>{p}</p>
              ))}
              {bloco.image_url && (
                <figure>
                  <img src={bloco.image_url} alt={bloco.image_caption || bloco.title} loading="lazy" />
                  {bloco.image_caption && <figcaption>{bloco.image_caption}</figcaption>}
                </figure>
              )}
            </div>
          ))}

          {projeto.timeline_events.length > 0 && (
            <div className="projeto-detalhe__bloco">
              <h2>{t("projeto.linha_do_tempo")}</h2>
              <ol className="projeto-detalhe__timeline">
                {projeto.timeline_events.map((evento) => (
                  <li key={evento.id}>
                    <span>{formatDate(evento.date)}</span>
                    <strong>{evento.title}</strong>
                    {evento.description && <p>{evento.description}</p>}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {projeto.images.length > 0 && (
            <div className="projeto-detalhe__bloco">
              <h2>{t("projeto.imagens")}</h2>
              <div className="projeto-detalhe__galeria">
                {projeto.images.map((imagem) => (
                  <figure key={imagem.id}>
                    <img src={imagem.image_url} alt={imagem.caption || projeto.title} loading="lazy" />
                    {imagem.caption && <figcaption>{imagem.caption}</figcaption>}
                  </figure>
                ))}
              </div>
            </div>
          )}

          {projeto.members.length > 0 && (
            <div className="projeto-detalhe__bloco">
              <h2>{t("projeto.equipe")}</h2>
              <ul className="projeto-detalhe__membros">
                {projeto.members.map((membro) => (
                  <li key={membro.id}>
                    <Link to={`/equipe/${membro.id}`}>{membro.name}</Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
