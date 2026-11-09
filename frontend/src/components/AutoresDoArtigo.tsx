import { Fragment } from "react"
import { Link } from "react-router-dom"
import type { ArticleAuthor } from "../types"

type Props = {
  autores: ArticleAuthor[]
  // Com links, quem é membro leva à lista dos artigos dele. Dentro de um cartão que já é um link, o nome fica só como
  // texto: um link dentro de outro não é HTML válido.
  links?: boolean
}

// Os autores de um artigo, no formato "A, B e C".
export default function AutoresDoArtigo({ autores, links = false }: Props) {
  return (
    <>
      {autores.map((autor, i) => (
        <Fragment key={`${i}-${autor.name}`}>
          {i > 0 && (i === autores.length - 1 ? " e " : ", ")}
          {links && autor.member_id ? (
            <Link to={`/artigos?autor=${autor.member_id}`} className="autor-link">
              {autor.name}
            </Link>
          ) : (
            autor.name
          )}
        </Fragment>
      ))}
    </>
  )
}
