import { useEffect, useState } from "react"
import { Link, useParams } from "react-router-dom"
import Markdown, { type Components, type Options } from "react-markdown"
import remarkGfm from "remark-gfm"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.min.css"
import { api } from "../../api"
import type { ArticleImage, NewsItem } from "../../types"
import PageHero from "../../components/PageHero"
import { ArrowLeftIcon, ExternalIcon, LinkedInIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import "./index.css"

function formatDate(date: string) {
  // Mesmo cuidado da lista: ano/mês/dia separados evitam o desvio de um dia do UTC.
  const [ano, mes, dia] = date.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
}

// Links externos abrem em outra aba. Imagens viram figura com legenda; a
// figura é feita de <span> porque o Markdown coloca a imagem dentro de um <p>.
// No admin, a imagem é chamada pelo número, como ![](imagem-1): o endereço e
// a legenda vêm de "Imagens do artigo". A legenda escrita entre os colchetes,
// se houver, vale mais que a do cadastro.
// Fórmulas em LaTeX, desenhadas pelo KaTeX, sempre entre $$ (em linha ou num
// bloco próprio). O $ sozinho fica desligado: "R$ 10 mi e R$ 20 mi" viraria
// fórmula. Fórmula com erro aparece em vermelho, sem derrubar a página.
const pluginsRemark: Options["remarkPlugins"] = [remarkGfm, [remarkMath, { singleDollarTextMath: false }]]
const pluginsRehype: Options["rehypePlugins"] = [[rehypeKatex, { throwOnError: false }]]

function componentesMarkdown(imagens: ArticleImage[]): Components {
  return {
    a: ({ href, children }) =>
      href?.startsWith("http") ? (
        <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>
      ) : (
        <a href={href}>{children}</a>
      ),
    img: ({ src, alt }) => {
      const numero = typeof src === "string" ? src.match(/^imagem-(\d+)$/)?.[1] : undefined
      const cadastrada = numero ? imagens.find((img) => img.number === Number(numero)) : undefined
      const endereco = numero ? cadastrada?.image_url : src
      const legenda = alt || cadastrada?.caption || ""
      // Número sem imagem cadastrada: não mostra nada em vez de imagem quebrada.
      if (typeof endereco !== "string" || !endereco) return null
      return (
        <span className="artigo__figura">
          <img src={endereco} alt={legenda} loading="lazy" />
          {legenda && <span className="artigo__legenda">{legenda}</span>}
        </span>
      )
    },
  }
}

export default function Artigo() {
  const { slugOrId } = useParams<{ slugOrId: string }>()
  const [artigo, setArtigo] = useState<NewsItem | null>(null)
  const [loadedId, setLoadedId] = useState<string | undefined>()
  const [copiado, setCopiado] = useState(false)
  const loading = loadedId !== slugOrId
  const artigoDaRota = artigo && (artigo.slug === slugOrId || String(artigo.id) === slugOrId) ? artigo : null
  usePageTitle(loading ? undefined : artigoDaRota?.title, loading ? undefined : artigoDaRota?.description)

  useEffect(() => {
    if (!slugOrId) return
    api
      .getNewsItem(slugOrId)
      .then((data: NewsItem) => setArtigo(data && data.id ? data : null))
      .catch(() => setArtigo(null))
      .finally(() => setLoadedId(slugOrId))
  }, [slugOrId])

  if (loading) return <p className="loading">Carregando...</p>

  if (!artigo) {
    return (
      <section className="section">
        <div className="container">
          <Link to="/artigos" className="back-link">
            <ArrowLeftIcon size={14} />
            Voltar para artigos
          </Link>
          <p className="state-message">
            <strong>Artigo não encontrado</strong>
            Não foi possível carregar esse artigo.
          </p>
        </div>
      </section>
    )
  }

  const temas = artigo.topics.split(",").map((t) => t.trim()).filter(Boolean)
  const url = window.location.href
  const ano = artigo.date?.slice(0, 4)
  const citacao = `${artigo.authors ? `${artigo.authors}. ` : ""}${artigo.title}. Insper Consulting Club${ano ? `, ${ano}` : ""}. Disponível em: ${url}.`

  function copiarCitacao() {
    navigator.clipboard.writeText(citacao).then(() => {
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2000)
    })
  }

  return (
    <div className="artigo-page">
      <PageHero
        back={{ to: "/artigos", label: "Voltar para artigos" }}
        eyebrow={artigo.date ? formatDate(artigo.date) : undefined}
        title={artigo.title}
        lead={artigo.authors}
      />

      <section className="section">
        <article className="container artigo">
          {temas.length > 0 && (
            <ul className="artigo__temas">
              {temas.map((tema) => (
                <li key={tema}>{tema}</li>
              ))}
            </ul>
          )}
          {artigo.image_url && <img src={artigo.image_url} alt="" className="artigo__capa" />}
          {artigo.description && (
            <div className="artigo__resumo">
              <h2>Resumo</h2>
              <p>{artigo.description}</p>
            </div>
          )}
          {/* O texto vem em Markdown. HTML digitado no admin não é
              executado: o react-markdown o mostra como texto. */}
          {artigo.content && (
            <div className="artigo__texto">
              <Markdown
                remarkPlugins={pluginsRemark}
                rehypePlugins={pluginsRehype}
                components={componentesMarkdown(artigo.images ?? [])}
              >
                {artigo.content}
              </Markdown>
            </div>
          )}

          <div className="artigo__rodape">
            <h2>Como citar</h2>
            <p className="artigo__citacao">{citacao}</p>
            <div className="artigo__acoes">
              <button type="button" className="btn btn--secondary" onClick={copiarCitacao}>
                {copiado ? "Copiado!" : "Copiar citação"}
              </button>
              <a
                href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn--secondary"
              >
                <LinkedInIcon size={16} />
                Compartilhar
              </a>
              {artigo.link && (
                <a href={artigo.link} target="_blank" rel="noopener noreferrer" className="btn btn--secondary">
                  Ver publicação original
                  <ExternalIcon />
                </a>
              )}
            </div>
          </div>
        </article>
      </section>
    </div>
  )
}
