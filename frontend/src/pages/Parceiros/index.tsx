import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { Partner } from "../../types"
import PageHero from "../../components/PageHero"
import { ArrowRightIcon, MailIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import "./index.css"

// Extraído de site-data/icc.json (sobre.porQueSerParceiro).
const BENEFICIOS_PARCEIRO = [
  {
    nome: "Acesso a talentos",
    descricao:
      "Contato direto com alunos de alta performance, treinados em resolução de cases e raciocínio analítico.",
  },
  {
    nome: "Visibilidade Institucional",
    descricao:
      "Presença em eventos, capacitações e redes sociais com crescimento consistente de alcance e engajamento.",
  },
  {
    nome: "Cases aplicados à realidade",
    descricao:
      "Possibilidade de propor desafios reais de negócio para serem resolvidos pelos nossos grupos de trainees e do Pedagógico.",
  },
]

export default function Parceiros() {
  usePageTitle("Parceiros", "Conheça as empresas que apoiam o Insper Consulting Club e contribuem para a formação dos futuros líderes em consultoria.")
  const [partners, setPartners] = useState<Partner[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getPartners()
      .then((data) => setPartners(data || []))
      .catch(() => setPartners([]))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="parceiros-page">
      <PageHero
        eyebrow="Parceiros"
        title={<>Quem caminha <span className="destaque">conosco</span></>}
        lead="Conheça as empresas que apoiam o Insper Consulting Club e contribuem para a formação dos futuros líderes em consultoria."
      />

      <section className="section">
        <div className="container">
          {loading ? (
            <p className="loading">Carregando parceiros...</p>
          ) : partners.length === 0 ? (
            <p className="state-message">Em breve, novos parceiros.</p>
          ) : (
            <div className="grid grid--3">
              {partners.map((p) => (
                <Link key={p.id} to={`/parceiros/${p.id}`} className="parceiro-card">
                  <div className="parceiro-card__logo">
                    {p.logo_url ? <img src={p.logo_url} alt={p.name} loading="lazy" /> : <span>{p.name}</span>}
                  </div>
                  <div className="parceiro-card__body">
                    {p.category && <p className="parceiro-card__categoria">{p.category}</p>}
                    <h2 className="parceiro-card__nome">{p.name}</h2>
                    {p.description && <p className="parceiro-card__descricao">{p.description}</p>}
                    <span className="link-arrow parceiro-card__mais">
                      Ver detalhes
                      <ArrowRightIcon />
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="section section--dark">
        <div className="container">
          <div className="section-head">
            <p className="eyebrow">Por que ser parceiro</p>
            <h2 className="section-title">O que sua empresa ganha ao apoiar o Insper Consulting Club</h2>
          </div>

          <div className="grid grid--3 parceiros-beneficios">
            {BENEFICIOS_PARCEIRO.map((b, index) => (
              <div className="parceiros-beneficio" key={b.nome}>
                <span className="parceiros-beneficio__index">{String(index + 1).padStart(2, "0")}</span>
                <h3>{b.nome}</h3>
                <p>{b.descricao}</p>
              </div>
            ))}
          </div>

          <a href="mailto:insperconsultingclub@gmail.com" className="btn btn--light parceiros-cta">
            <MailIcon size={18} />
            Fale com a gente
          </a>
        </div>
      </section>
    </div>
  )
}
