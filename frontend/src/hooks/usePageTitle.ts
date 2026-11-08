import { useEffect } from "react"
import useSiteConfig from "./useSiteConfig"

function setMetaContent(selector: string, content: string) {
  document.head.querySelector(selector)?.setAttribute("content", content)
}

// Atualiza o título da aba e as meta tags de descrição/Open Graph a cada
// página. Isso não resolve a prévia ao compartilhar o link (WhatsApp,
// Facebook etc. não executam JS e só leem o HTML estático; por isso o nome e
// a descrição do site também são gravados no index.html durante o build, ver
// plugins/siteConfig.ts), mas mantém a aba do navegador e qualquer ferramenta
// que leia o DOM corretas por página.
export default function usePageTitle(title?: string, description?: string) {
  const { site_name: site, site_description: descricaoPadrao } = useSiteConfig()

  useEffect(() => {
    const fullTitle = title ? `${title} | ${site}` : site
    const desc = description || descricaoPadrao

    document.title = fullTitle
    setMetaContent('meta[name="description"]', desc)
    setMetaContent('meta[property="og:title"]', fullTitle)
    setMetaContent('meta[property="og:description"]', desc)
  }, [title, description, site, descricaoPadrao])
}
