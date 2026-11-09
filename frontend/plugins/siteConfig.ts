import type { Plugin } from "vite"

// Grava a Configuração do site (admin) no HTML durante o build.
//
// O site é estático: quem compartilha um link no WhatsApp ou no LinkedIn só
// lê o index.html, sem executar JavaScript. Por isso o nome, a descrição, a
// imagem de compartilhamento e o ícone precisam estar no HTML já pronto. O
// plugin também grava uma cópia da configuração em window.__SITE_CONFIG__,
// para a primeira tela já sair com os textos e o logo certos, sem esperar a API.
//
// O site não guarda textos próprios: se a API não responder, o build falha. Assim
// o deploy anterior continua no ar, em vez de publicar um site sem textos.

type Dados = Record<string, unknown> & {
  site_name?: string
  site_description?: string
  logo_url?: string | null
  favicon_url?: string | null
  og_image_url?: string | null
}

const TENTATIVAS = 2
// O backend gratuito dorme e leva cerca de 30 segundos para acordar.
const ESPERA_MS = 60_000

async function busca(apiUrl: string): Promise<Dados | null> {
  for (let tentativa = 1; tentativa <= TENTATIVAS; tentativa++) {
    try {
      const resposta = await fetch(`${apiUrl.replace(/\/$/, "")}/site-config/`, {
        headers: { Accept: "application/json" },
        signal: AbortSignal.timeout(ESPERA_MS),
      })
      if (!resposta.ok) throw new Error(`HTTP ${resposta.status}`)
      const dados = (await resposta.json()) as Dados
      if (typeof dados?.email !== "string") throw new Error("resposta sem os campos esperados")
      return dados
    } catch (erro) {
      const motivo = erro instanceof Error ? erro.message : String(erro)
      console.warn(`[site-config] tentativa ${tentativa} de ${TENTATIVAS} falhou: ${motivo}`)
    }
  }
  return null
}

const escapaAtributo = (valor: string) =>
  valor.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;")

// Um valor entre aspas, para dentro de content="..." ou href="...".
const trocaAtributo = (html: string, tag: RegExp, atributo: string, valor: string) =>
  html.replace(tag, (trecho) =>
    trecho.replace(new RegExp(`(${atributo}=")[^"]*(")`), (_m, a: string, b: string) => `${a}${escapaAtributo(valor)}${b}`)
  )

export function aplicaNoHtml(html: string, dados: Dados): string {
  let saida = html

  if (dados.site_name) {
    saida = saida.replace(/<title>[^<]*<\/title>/, `<title>${escapaAtributo(dados.site_name)}</title>`)
    saida = trocaAtributo(saida, /<meta\s+property="og:site_name"[^>]*>/, "content", dados.site_name)
    saida = trocaAtributo(saida, /<meta\s+property="og:title"[^>]*>/, "content", dados.site_name)
  }
  if (dados.site_description) {
    saida = trocaAtributo(saida, /<meta\s+name="description"[^>]*>/, "content", dados.site_description)
    saida = trocaAtributo(saida, /<meta\s+property="og:description"[^>]*>/, "content", dados.site_description)
  }
  if (dados.og_image_url) {
    saida = trocaAtributo(saida, /<meta\s+property="og:image"\s[^>]*>/, "content", dados.og_image_url)
    // As medidas do arquivo original não valem para a imagem nova.
    saida = saida.replace(/\s*<meta\s+property="og:image:(width|height)"[^>]*>/g, "")
  }
  if (dados.favicon_url) {
    saida = trocaAtributo(saida, /<link\s+rel="icon"[^>]*>/, "href", dados.favicon_url)
    // O tipo (png) do ícone original pode não ser o do novo.
    saida = saida.replace(/(<link\s+rel="icon")\s+type="[^"]*"/, "$1")
  }
  if (dados.logo_url) {
    saida = trocaAtributo(saida, /<link\s+rel="preload"\s+as="image"[^>]*>/, "href", dados.logo_url)
  }

  // Cópia da configuração, sem a Política de Privacidade (longa, e a própria
  // página a busca). O "<" é escapado para o JSON não fechar o <script>.
  const copia = { ...dados }
  delete copia.privacy_text
  const json = JSON.stringify(copia).replace(/</g, "\\u003c")
  return saida.replace("</head>", `    <script>window.__SITE_CONFIG__=${json}</script>\n  </head>`)
}

export default function siteConfig(apiUrl: string | undefined): Plugin {
  let dados: Dados | null = null

  return {
    name: "icc-site-config",
    apply: "build",
    async buildStart() {
      if (!apiUrl) throw new Error("[site-config] VITE_API_URL não está definida: sem ela o build não tem de onde ler os textos.")
      dados = await busca(apiUrl)
      if (!dados) throw new Error(`[site-config] a API não respondeu em ${apiUrl}: build interrompido para não publicar um site sem textos.`)
    },
    transformIndexHtml(html) {
      return dados ? aplicaNoHtml(html, dados) : html
    },
  }
}
