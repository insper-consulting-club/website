import { useEffect } from "react"

const SITE = "Liga Insper Consulting Club"
const DEFAULT_DESCRIPTION =
  "A Liga Insper Consulting Club é uma organização estudantil dedicada ao desenvolvimento de futuros consultores."

function setMetaContent(selector: string, content: string) {
  document.head.querySelector(selector)?.setAttribute("content", content)
}

// Atualiza o título da aba e as meta tags de descrição/Open Graph a cada
// página. Isso não resolve a prévia ao compartilhar o link (WhatsApp,
// Facebook etc. não executam JS e só leem o HTML estático em index.html),
// mas mantém a aba do navegador e qualquer ferramenta que leia o DOM
// corretas por página.
export default function usePageTitle(title?: string, description?: string) {
  useEffect(() => {
    const fullTitle = title ? `${title} | ${SITE}` : SITE
    const desc = description || DEFAULT_DESCRIPTION

    document.title = fullTitle
    setMetaContent('meta[name="description"]', desc)
    setMetaContent('meta[property="og:title"]', fullTitle)
    setMetaContent('meta[property="og:description"]', desc)
  }, [title, description])
}
