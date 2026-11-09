import useSiteConfig from "./useSiteConfig"

type Variaveis = Record<string, string | number>

// Devolve a função que busca um texto curto pela chave, já com os trechos
// entre chaves preenchidos: t("projeto.periodo_desde", { inicio: "1 de março" }).
// O valor vem do admin (Textos do site), pela cópia do build ou pela API. Se a chave
// não existir, o desenvolvimento mostra a própria chave (para o erro aparecer) e a
// produção mostra nada.
export default function useTextos() {
  const { texts } = useSiteConfig()

  return function t(chave: string, variaveis?: Variaveis): string {
    const texto = texts?.[chave] || (import.meta.env.DEV ? chave : "")
    if (!variaveis) return texto
    return texto.replace(/\{(\w+)\}/g, (trecho, nome: string) =>
      nome in variaveis ? String(variaveis[nome]) : trecho
    )
  }
}
