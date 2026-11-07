import { useEffect, useState } from "react"
import { api } from "../api"
import type { Program } from "../types"

// Header, Footer e Home listam os mesmos programas. A promessa fica guardada
// no módulo para que as três montagens compartilhem uma requisição só, em vez
// de pedir a mesma lista três vezes em toda visita.
let pedido: Promise<Program[]> | null = null

export default function useProgramas() {
  const [programas, setProgramas] = useState<Program[]>([])

  useEffect(() => {
    if (!pedido) pedido = api.getPrograms()
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
