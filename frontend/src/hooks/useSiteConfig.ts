import { useEffect, useState } from "react"
import { api } from "../api"
import type { SiteConfig } from "../types"

declare global {
  interface Window {
    // Cópia da Configuração do site gravada no HTML durante o build (ver
    // plugins/siteConfig.ts). Faz a primeira tela já sair com os textos do
    // admin, sem esperar a API. Só falta no servidor de desenvolvimento.
    __SITE_CONFIG__?: Partial<SiteConfig>
  }
}

// Sem cópia do build e sem API ainda: tudo vazio. O site não guarda textos próprios;
// quem manda neles é o admin. Em produção a cópia do build sempre existe, porque o
// build falha quando não consegue lê-la. Só o servidor de desenvolvimento passa
// pelo estado vazio, por alguns instantes.
const VAZIA: SiteConfig = {
  site_name: "", site_description: "", logo_url: null, favicon_url: null, og_image_url: null,
  email: "", instagram_url: "", instagram_label: "", linkedin_url: "", linkedin_label: "",
  github_url: "", github_label: "", home_about_photo_url: null, home_about_photo_alt: "",
  featured_program_slug: "", privacy_updated: "", privacy_text: "",
  partner_benefits: [], home_sections: [], texts: {}, nav_items: [],
}

function inicial(): SiteConfig {
  const copia = typeof window !== "undefined" ? window.__SITE_CONFIG__ : undefined
  if (!copia || typeof copia.email !== "string") return VAZIA
  // Campos que a cópia não tem (a Política de Privacidade sai por ser longa) ficam vazios.
  return { ...VAZIA, ...copia }
}

// Header, Footer e várias páginas usam a mesma configuração. Como em
// useProgramas, a promessa fica guardada no módulo para que todas as
// montagens compartilhem uma requisição só. A cópia do build vale até a
// resposta da API chegar; depois vale a API, que é sempre a mais recente.
let pedido: Promise<SiteConfig> | null = null
let atual: SiteConfig = inicial()
let atualizada = false

export default function useSiteConfig(): SiteConfig {
  const [config, setConfig] = useState<SiteConfig>(atual)

  useEffect(() => {
    if (atualizada) return
    if (!pedido) {
      pedido = api.getSiteConfig().then((dados: SiteConfig) => {
        // Resposta sem os campos esperados (erro do servidor, por exemplo)
        // não pode substituir o que já temos.
        if (!dados || typeof dados.email !== "string" || !Array.isArray(dados.home_sections)) {
          throw new Error("Configuração inválida")
        }
        return dados
      })
      // Falha: libera uma nova tentativa na próxima montagem.
      pedido.catch(() => {
        pedido = null
      })
    }
    let ativo = true
    pedido
      .then((dados) => {
        atual = dados
        atualizada = true
        if (ativo) setConfig(dados)
      })
      .catch(() => {
        // Sem a API, o site segue com a cópia do build.
      })
    return () => {
      ativo = false
    }
  }, [])

  return config
}
