import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { api } from "../../api"
import type { ActivityCategory, CalendarMonth } from "../../types"
import MonthCalendarGrid from "./MonthCalendarGrid"
import { MESES_ORDER, extractEvents } from "./calendario"
import PageHero from "../../components/PageHero"
import usePageTitle from "../../hooks/usePageTitle"
import "./index.css"

// "2026.1", "2026.2", "2027.1"... um semestre real (ano + 1 ou 2), no
// mesmo formato usado pelo nome do calendário do Google ("Insper
// Consulting Club 26.2"). Meses com semester "both" (conteúdo mock
// legado, sem ano) não entram: não dá pra encaixar num semestre real.
function semesterKey(m: CalendarMonth): string | null {
  if (!m.year || (m.semester !== '1' && m.semester !== '2')) return null
  return `${m.year}.${m.semester}`
}

function diasAteLabel(date: Date): string {
  const hoje = new Date()
  hoje.setHours(0, 0, 0, 0)
  const diff = Math.round((date.getTime() - hoje.getTime()) / 86400000)
  if (diff === 0) return "hoje"
  if (diff === 1) return "amanhã"
  return `em ${diff} dias`
}

const DIAS_SEMANA_ABREV = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"]

type ViewMode = 'grade' | 'lista'

// Na tela estreita a grade fica com células pequenas demais pra ser
// confortável, então o mobile já abre em Lista por padrão; desktop
// mantém a Grade (mesmo breakpoint usado no resto da página, 600px).
function defaultViewMode(): ViewMode {
  if (typeof window === 'undefined') return 'grade'
  return window.innerWidth < 600 ? 'lista' : 'grade'
}

export default function Atividades() {
  usePageTitle("Atividades", "Um calendário completo de desenvolvimento profissional e prático")
  const [categories, setCategories] = useState<ActivityCategory[]>([])
  const [calendar, setCalendar] = useState<CalendarMonth[]>([])
  const [selectedSemester, setSelectedSemester] = useState<string>('')
  const [viewMode, setViewMode] = useState<ViewMode>(defaultViewMode)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getCategories(),
      api.getCalendar(),
    ]).then(([categoriesData, calendarData]: [ActivityCategory[], CalendarMonth[]]) => {
      setCategories(categoriesData)
      setCalendar(calendarData)
      const keys = Array.from(new Set(calendarData.map(semesterKey).filter((k): k is string => k !== null)))
      keys.sort()
      if (keys.length > 0) setSelectedSemester(keys[keys.length - 1])
      setLoading(false)
    })
  }, [])

  const availableSemesters = Array.from(
    new Set(calendar.map(semesterKey).filter((k): k is string => k !== null))
  ).sort()

  // Um calendário com buracos confunde a passagem do tempo, então os 6
  // meses do semestre selecionado aparecem sempre, mesmo os que ainda não
  // têm evento cadastrado (entram como uma grade vazia).
  const byMonthYear = new Map(calendar.map((m) => [`${m.month}-${m.year}`, m]))
  const [selYear, selSem] = selectedSemester ? selectedSemester.split('.') : [null, null]
  const monthsInSemester = selSem === '1' ? MESES_ORDER.slice(0, 6) : selSem === '2' ? MESES_ORDER.slice(6, 12) : []
  const displayedCalendar: CalendarMonth[] = monthsInSemester.map((month, i) => {
    const existing = byMonthYear.get(`${month}-${selYear}`)
    if (existing) return existing
    return {
      id: -(i + 1),
      month,
      year: selYear ? Number(selYear) : null,
      items: [],
      semester: selSem as '1' | '2',
      order: i + 1,
    }
  })

  // "Próximo evento" olha pra todos os semestres carregados, não só o
  // exibido no momento, pra sempre destacar o que vem por aí de verdade.
  const hoje = new Date()
  hoje.setHours(0, 0, 0, 0)
  const nextEvent = calendar
    .flatMap((m) => extractEvents(m.month, m.year, m.items))
    .filter((e) => e.date >= hoje)
    .sort((a, b) => a.date.getTime() - b.date.getTime())[0]

  if (loading) return <p className="loading">Carregando...</p>

  return (
    <div className="atividades-page">
      <PageHero
        eyebrow="Atividades"
        title="Nossas Atividades"
        lead="Um calendário completo de desenvolvimento profissional e prático"
      />

      {categories.length > 0 && (
        <section className="section">
          <div className="container grid grid--3">
            {categories.map((cat) => (
              <Link key={cat.slug} to={`/atividades/categoria/${cat.slug}`} className="card atividade-card">
                <div className="atividade-card__top">
                  {cat.icon_url && <img src={cat.icon_url} alt="" className="atividade-card__icon" />}
                  {cat.badge && <span className="tag">{cat.badge}</span>}
                </div>
                <h2 className="atividade-card__title">{cat.label}</h2>
                <p className="atividade-card__desc">{cat.description}</p>
                {cat.highlights.length > 0 && (
                  <ul className="atividade-card__list">
                    {cat.highlights.map((h) => (
                      <li key={h}>{h}</li>
                    ))}
                  </ul>
                )}
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Calendário */}
      <section className="section calendario-section">
        <div className="container">
          <div className="calendario-header">
            <h2 className="section-title">Calendário do Semestre</h2>
            {availableSemesters.length > 0 && (
              <div className="calendario-header__controls">
                <div className="calendario-view-toggle">
                  <button
                    type="button"
                    className={`calendario-view-toggle__btn${viewMode === 'grade' ? ' active' : ''}`}
                    onClick={() => setViewMode('grade')}
                  >
                    <svg viewBox="0 0 20 20" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
                      <rect x="2.5" y="2.5" width="15" height="15" rx="2" />
                      <line x1="2.5" y1="8.3" x2="17.5" y2="8.3" />
                      <line x1="8" y1="8.3" x2="8" y2="17.5" />
                      <line x1="13" y1="8.3" x2="13" y2="17.5" />
                    </svg>
                    Grade
                  </button>
                  <button
                    type="button"
                    className={`calendario-view-toggle__btn${viewMode === 'lista' ? ' active' : ''}`}
                    onClick={() => setViewMode('lista')}
                  >
                    <svg viewBox="0 0 20 20" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true">
                      <line x1="7" y1="5" x2="18" y2="5" />
                      <line x1="7" y1="10" x2="18" y2="10" />
                      <line x1="7" y1="15" x2="18" y2="15" />
                      <circle cx="3" cy="5" r="1" fill="currentColor" stroke="none" />
                      <circle cx="3" cy="10" r="1" fill="currentColor" stroke="none" />
                      <circle cx="3" cy="15" r="1" fill="currentColor" stroke="none" />
                    </svg>
                    Lista
                  </button>
                </div>
                <select
                  className="calendario-select"
                  value={selectedSemester}
                  onChange={(e) => setSelectedSemester(e.target.value)}
                  aria-label="Selecionar semestre"
                >
                  {availableSemesters.map((key) => (
                    <option key={key} value={key}>{key}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          {nextEvent && (
            <div
              role="button"
              tabIndex={0}
              className="calendario-next-event"
              onClick={() => {
                const y = nextEvent.date.getFullYear()
                const sem = nextEvent.date.getMonth() < 6 ? '1' : '2'
                setSelectedSemester(`${y}.${sem}`)
              }}
              onKeyDown={(e) => {
                if (e.key !== "Enter" && e.key !== " ") return
                e.preventDefault()
                const y = nextEvent.date.getFullYear()
                const sem = nextEvent.date.getMonth() < 6 ? '1' : '2'
                setSelectedSemester(`${y}.${sem}`)
              }}
            >
              <span className="calendario-next-event__label">Próximo evento</span>
              <span className="calendario-next-event__title">{nextEvent.title}</span>
              <span className="calendario-next-event__date">
                {String(nextEvent.date.getDate()).padStart(2, "0")}/
                {String(nextEvent.date.getMonth() + 1).padStart(2, "0")} · {diasAteLabel(nextEvent.date)}
              </span>
            </div>
          )}

          {availableSemesters.length === 0 ? (
            <p className="calendario-empty">Nenhum semestre cadastrado ainda.</p>
          ) : viewMode === 'grade' ? (
            <div className="calendario-grid">
              {displayedCalendar.map((c) => (
                <div key={c.id} className="calendario-card">
                  <h4 className="calendario-card__month">{c.month}</h4>
                  <MonthCalendarGrid month={c.month} year={c.year} items={c.items} />
                </div>
              ))}
            </div>
          ) : (
            <div className="calendario-list-view">
              {displayedCalendar.map((c) => {
                const events = extractEvents(c.month, c.year, c.items).sort(
                  (a, b) => a.date.getTime() - b.date.getTime()
                )
                return (
                  <div key={c.id} className="calendario-list-month">
                    <h4 className="calendario-list-month__title">{c.month}</h4>
                    {events.length === 0 ? (
                      <p className="calendario-list-month__empty">Nenhum evento cadastrado.</p>
                    ) : (
                      <ul className="calendario-list">
                        {events.map((e, i) => (
                          <li key={i} className="calendario-list__item">
                            <span className="calendario-list__date">
                              {DIAS_SEMANA_ABREV[e.date.getDay()]} {String(e.date.getDate()).padStart(2, "0")}/
                              {String(e.date.getMonth() + 1).padStart(2, "0")}
                            </span>
                            <span className="calendario-list__title">{e.title}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </section>

    </div>
  )
}
