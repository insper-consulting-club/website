import { useEffect, useState } from "react"
import { api } from "../api"
import type { Directorate } from "../types"

// Mesmo arranjo do useProgramas: o Header monta em toda visita e precisa da
// lista para o submenu, então a promessa fica no módulo e uma requisição
// atende qualquer quantidade de montagens.
let pedido: Promise<Directorate[]> | null = null

export default function useDiretorias() {
  const [diretorias, setDiretorias] = useState<Directorate[]>([])

  useEffect(() => {
    if (!pedido) pedido = api.getDirectorates()
    let ativo = true
    pedido
      .then((dados) => {
        if (ativo) setDiretorias(dados)
      })
      .catch(() => {
        // Sem a lista, o submenu fica sem as diretorias e o item continua
        // levando à página de Equipe, que monta as seções pelos membros.
        if (ativo) setDiretorias([])
      })
    return () => {
      ativo = false
    }
  }, [])

  return diretorias
}
