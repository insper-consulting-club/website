import { useEffect, useState } from "react"
import { api } from "../api"
import { SITE_CONFIG_PADRAO } from "../siteConfigPadrao"
import type { SiteConfig } from "../types"

// Header, Footer e várias páginas usam a mesma configuração. Como em
// useProgramas, a promessa fica guardada no módulo para que todas as
// montagens compartilhem uma requisição só.
let pedido: Promise<SiteConfig> | null = null
let carregada: SiteConfig | null = null

export default function useSiteConfig(): SiteConfig {
  const [config, setConfig] = useState<SiteConfig>(carregada ?? SITE_CONFIG_PADRAO)

  useEffect(() => {
    if (carregada) return
    if (!pedido) {
      pedido = api.getSiteConfig().then((dados: SiteConfig) => {
        // Resposta sem os campos esperados (erro do servidor, por exemplo)
        // não pode substituir a reserva.
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
        carregada = dados
        if (ativo) setConfig(dados)
      })
      .catch(() => {
        // Sem a configuração, o site segue com os textos de reserva.
      })
    return () => {
      ativo = false
    }
  }, [])

  return config
}
