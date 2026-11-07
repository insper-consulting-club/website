import type { ContentBlock } from "../../types"
import "./index.css"

interface Props {
  block: ContentBlock
}

export default function ContentBlockComponent({ block }: Props) {
  const hasText = block.text.trim().length > 0
  const hasImage = !!block.image_url

  // Se não tem texto, imagem fica centralizada independente do align
  const imageOnly = hasImage && !hasText
  // Alinhamento efetivo
  const align = imageOnly ? "center" : block.image_align

  return (
    <div className={`content-block content-block--${align} ${imageOnly ? "content-block--image-only" : ""}`}>

      {/* Texto */}
      {hasText && (
        <div className="content-block__text">
          {block.title && <h3 className="content-block__title">{block.title}</h3>}
          {block.text.split("\n").map((paragraph, i) =>
            paragraph.trim() ? (
              <p key={i} className="content-block__paragraph">{paragraph}</p>
            ) : null
          )}
        </div>
      )}

      {/* Imagem */}
      {hasImage && (
        <figure className="content-block__figure">
          <img
            src={block.image_url!}
            alt={block.image_caption || block.title || ""}
            className="content-block__image"
          />
          {block.image_caption && (
            <figcaption className="content-block__caption">{block.image_caption}</figcaption>
          )}
        </figure>
      )}

    </div>
  )
}
