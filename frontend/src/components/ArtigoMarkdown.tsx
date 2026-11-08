import Markdown, { type Components, type Options } from "react-markdown"
import remarkGfm from "remark-gfm"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import "katex/dist/katex.min.css"
import type { ArticleImage } from "../types"

// Links externos abrem em outra aba. Imagens viram figura com legenda; a
// figura é feita de <span> porque o Markdown coloca a imagem dentro de um <p>.
// No admin, a imagem é chamada pelo número, como ![](imagem-1): o endereço e
// a legenda vêm de "Imagens do artigo". A legenda escrita entre os colchetes,
// se houver, vale mais que a do cadastro.
// Fórmulas em LaTeX, desenhadas pelo KaTeX, sempre entre $$ (em linha ou num
// bloco próprio). O $ sozinho fica desligado: "R$ 10 mi e R$ 20 mi" viraria
// fórmula. Fórmula com erro aparece em vermelho, sem derrubar a página.
// O texto vem em Markdown. HTML digitado no admin não é executado: o
// react-markdown o mostra como texto.
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
      // Número sem imagem cadastrada: omite o trecho em vez de mostrar imagem quebrada.
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

// Texto de um artigo: o mesmo na página do artigo e na prévia do admin.
export default function ArtigoMarkdown({ texto, imagens }: { texto: string; imagens: ArticleImage[] }) {
  return (
    <Markdown remarkPlugins={pluginsRemark} rehypePlugins={pluginsRehype} components={componentesMarkdown(imagens)}>
      {texto}
    </Markdown>
  )
}
