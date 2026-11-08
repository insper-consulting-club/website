import { useEffect, useState } from "react"
import ArtigoMarkdown from "../../components/ArtigoMarkdown"
import TextoMarkdown from "../../components/TextoMarkdown"
import type { ArticleImage } from "../../types"
import "../Artigo/index.css"
import "../PoliticaPrivacidade/index.css"
import "../Programa/index.css"

// Prévia do Markdown para o admin. A página do admin (backend) a abre num
// iframe e envia o texto por postMessage; aqui ele é desenhado com os mesmos
// componentes e estilos do site, então a prévia é fiel ao resultado publicado.
// Só mensagens vindas do endereço do backend são aceitas.

type Modo = "artigo" | "politica" | "programa"

type Mensagem = {
  tipo: "markdown"
  texto: string
  modo: Modo
  imagens?: ArticleImage[]
}

const ORIGEM_ADMIN = new URL(import.meta.env.VITE_API_URL).origin

function eMensagem(dados: unknown): dados is Mensagem {
  const m = dados as Partial<Mensagem> | null
  return (
    !!m &&
    m.tipo === "markdown" &&
    typeof m.texto === "string" &&
    (m.modo === "artigo" || m.modo === "politica" || m.modo === "programa")
  )
}

export default function Previa() {
  const [mensagem, setMensagem] = useState<Mensagem | null>(null)

  useEffect(() => {
    document.title = "Prévia"
    // Página interna do admin: não deve aparecer em buscas.
    const robots = document.createElement("meta")
    robots.name = "robots"
    robots.content = "noindex"
    document.head.appendChild(robots)

    function aoReceber(evento: MessageEvent) {
      if (evento.origin !== ORIGEM_ADMIN) return
      if (eMensagem(evento.data)) setMensagem(evento.data)
    }
    window.addEventListener("message", aoReceber)
    // Avisa o admin de que já pode enviar o texto.
    window.parent.postMessage({ tipo: "previa-pronta" }, ORIGEM_ADMIN)

    return () => {
      window.removeEventListener("message", aoReceber)
      robots.remove()
    }
  }, [])

  if (!mensagem) return <p className="loading">Carregando prévia...</p>
  if (!mensagem.texto.trim()) return <p className="state-message">Escreva algo para ver a prévia.</p>

  if (mensagem.modo === "artigo") {
    return (
      <section className="section">
        <article className="container artigo">
          <div className="artigo__texto">
            <ArtigoMarkdown texto={mensagem.texto} imagens={mensagem.imagens ?? []} />
          </div>
        </article>
      </section>
    )
  }

  if (mensagem.modo === "politica") {
    return (
      <section className="section">
        <article className="container container--narrow politica-content">
          <TextoMarkdown>{mensagem.texto}</TextoMarkdown>
        </article>
      </section>
    )
  }

  return (
    <section className="section">
      <div className="container">
        <div className="programa-bloco">
          <div className="programa-bloco__texto">
            <TextoMarkdown>{mensagem.texto}</TextoMarkdown>
          </div>
        </div>
      </div>
    </section>
  )
}
