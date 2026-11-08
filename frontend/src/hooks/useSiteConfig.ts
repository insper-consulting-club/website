import { useEffect, useState } from "react"
import { api } from "../api"
import { SITE_CONFIG_PADRAO } from "../siteConfigPadrao"
import { TEXTOS_PADRAO } from "../textosPadrao"
import type { SiteConfig } from "../types"

declare global {
  interface Window {
    // Cópia da Configuração do site gravada no HTML durante o build (ver
    // plugins/siteConfig.ts). Faz a primeira tela já sair com os textos do
    // admin, sem esperar a API. Pode faltar (build sem acesso à API).
    __SITE_CONFIG__?: Partial<SiteConfig>
  }
}

function inicial(): SiteConfig {
  const copia = typeof window !== "undefined" ? window.__SITE_CONFIG__ : undefined
  if (!copia || typeof copia.email !== "string") return SITE_CONFIG_PADRAO
  // Campos que a cópia não tem (por exemplo, a Política, que sai por ser longa)
  // ficam com o valor de reserva.
  return { ...SITE_CONFIG_PADRAO, ...copia, texts: { ...TEXTOS_PADRAO, ...copia.texts } }
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
        if (!dados || typeof dados.email !== "string") throw new Error("Configuração inválida")
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
        // Sem a API, o site segue com a cópia do build ou com os textos de reserva.
      })
    return () => {
      ativo = false
    }
  }, [])

  return config
}
