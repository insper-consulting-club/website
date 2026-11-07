export const MESES_ORDER = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]

export const MESES_PT_INDEX: Record<string, number> = Object.fromEntries(
  MESES_ORDER.map((nome, i) => [nome, i])
)

const ITEM_PATTERN = /^(\d{2})\/(\d{2})\s*-\s*(.+)$/

export function parseItemsByDay(items: string[]): Map<number, string[]> | null {
  const byDay = new Map<number, string[]>()
  let algumBateuFormato = false
  for (const item of items) {
    const match = item.match(ITEM_PATTERN)
    // Uma linha fora do formato não invalida o mês inteiro: só é ignorada.
    // O mês só cai pra lista simples (retorno null) quando NENHUMA linha bate
    // o formato, sinal de que é conteúdo antigo, sem data, e não dá pra
    // montar grade nenhuma a partir dele.
    if (!match) continue
    algumBateuFormato = true
    const day = parseInt(match[1], 10)
    const title = match[3].trim()
    byDay.set(day, [...(byDay.get(day) ?? []), title])
  }
  return algumBateuFormato ? byDay : null
}

// Reaproveitado fora daqui pra achar o "próximo evento" entre todos os
// meses carregados, não só o mês sendo exibido no momento.
export function extractEvents(
  month: string, year: number | null, items: string[]
): { date: Date; title: string }[] {
  const monthIndex = MESES_PT_INDEX[month]
  if (year === null || monthIndex === undefined) return []
  const events: { date: Date; title: string }[] = []
  for (const item of items) {
    const match = item.match(ITEM_PATTERN)
    if (!match) continue
    events.push({ date: new Date(year, monthIndex, parseInt(match[1], 10)), title: match[3].trim() })
  }
  return events
}
