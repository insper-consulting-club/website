import { useEffect, useState } from "react"
import { api } from "../api"
import type { ActivityCategory } from "../types"

// Header, Footer e Home listam os mesmos programas. A promessa fica guardada
// no módulo para que as três montagens compartilhem uma requisição só, em vez
// de pedir a mesma lista três vezes em toda visita.
let pedido: Promise<ActivityCategory[]> | null = null

export default function useProgramas() {
  const [programas, setProgramas] = useState<ActivityCategory[]>([])

  useEffect(() => {
    if (!pedido) pedido = api.getCategories()
    let ativo = true
    pedido
      .then((dados) => {
        if (ativo) setProgramas(dados)
      })
      .catch(() => {
        // Sem a lista, os menus simplesmente não exibem os programas; nenhuma
        // outra parte da página depende disso.
        if (ativo) setProgramas([])
      })
    return () => {
      ativo = false
    }
  }, [])

  return programas
}
