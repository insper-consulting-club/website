import { useState } from "react"
import { MESES_PT_INDEX, parseItemsByDay } from "./calendario"

const DIAS_SEMANA = ["D", "S", "T", "Q", "Q", "S", "S"]

interface MonthCalendarGridProps {
  month: string
  year: number | null
  items: string[]
}

export default function MonthCalendarGrid({ month, year, items }: MonthCalendarGridProps) {
  const [selectedDay, setSelectedDay] = useState<number | null>(null)

  const monthIndex = MESES_PT_INDEX[month]
  const eventsByDay = year !== null && monthIndex !== undefined ? parseItemsByDay(items) : null

  // Sem ano cadastrado (ou tópicos sem data), cai pra lista simples: não dá
  // pra montar uma grade de dias da semana sem saber o ano.
  if (!eventsByDay) {
    return (
      <ul className="calendario-card__list">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    )
  }

  const firstWeekday = new Date(year as number, monthIndex, 1).getDay()
  const daysInMonth = new Date(year as number, monthIndex + 1, 0).getDate()
  const cells: (number | null)[] = [
    ...Array(firstWeekday).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ]

  const today = new Date()
  const isCurrentMonth = year === today.getFullYear() && monthIndex === today.getMonth()

  const selectedTitles = selectedDay !== null ? eventsByDay.get(selectedDay) : undefined

  return (
    <div className="mes-grid">
      <div className="mes-grid__weekdays">
        {DIAS_SEMANA.map((label, i) => (
          <span key={i}>{label}</span>
        ))}
      </div>
      <div className="mes-grid__days">
        {cells.map((day, i) => {
          if (day === null) {
            return <span key={`pad-${i}`} className="mes-grid__day mes-grid__day--empty" />
          }
          const titles = eventsByDay.get(day)
          const isSelected = selectedDay === day
          const isToday = isCurrentMonth && day === today.getDate()
          return (
            <button
              key={day}
              type="button"
              className={`mes-grid__day${titles ? " mes-grid__day--event" : ""}${isSelected ? " mes-grid__day--selected" : ""}${isToday ? " mes-grid__day--today" : ""}`}
              onClick={() => titles && setSelectedDay(isSelected ? null : day)}
              disabled={!titles}
              title={titles?.join("; ")}
            >
              {day}
            </button>
          )
        })}
      </div>

      {selectedTitles && (
        <div className="mes-grid__agenda">
          <span className="mes-grid__agenda-date">
            {String(selectedDay).padStart(2, "0")}/{String(monthIndex + 1).padStart(2, "0")}
          </span>
          <ul>
            {selectedTitles.map((title) => (
              <li key={title}>{title}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
