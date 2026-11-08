import { TEXTOS_PADRAO, type ChaveTexto } from "../textosPadrao"
import useSiteConfig from "./useSiteConfig"

type Variaveis = Record<string, string | number>

// Devolve a função que busca um texto curto pela chave, já com os trechos
// entre chaves preenchidos: t("projeto.periodo_desde", { inicio: "1 de março" }).
// O valor vem do admin (Textos do site); sem ele, vale o texto original.
export default function useTextos() {
  const { texts } = useSiteConfig()

  return function t(chave: ChaveTexto, variaveis?: Variaveis): string {
    const texto = texts?.[chave] || TEXTOS_PADRAO[chave]
    if (!variaveis) return texto
    return texto.replace(/\{(\w+)\}/g, (trecho, nome: string) =>
      nome in variaveis ? String(variaveis[nome]) : trecho
    )
  }
}
