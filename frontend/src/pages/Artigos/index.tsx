import { useEffect, useMemo, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
import { api } from "../../api"
import type { ArticleSummary } from "../../types"
import AutoresDoArtigo from "../../components/AutoresDoArtigo"
import PageHero from "../../components/PageHero"
import { ArrowRightIcon } from "../../components/Icons"
import usePageTitle from "../../hooks/usePageTitle"
import useTextos from "../../hooks/useTextos"
import "./index.css"

function formatDate(date: string) {
  // new Date(date) leria "AAAA-MM-DD" como meia-noite UTC, que em horário de
  // Brasília já é o dia anterior; construindo com ano/mês/dia separados, a
  // data é interpretada no fuso local, sem esse desvio de um dia.
  const [ano, mes, dia] = date.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "numeric", month: "long", year: "numeric" })
}

// Para achar homônimos: sem acento, sem maiúscula e sem espaços repetidos.
const normaliza = (nome: string) =>
  nome
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase()

type OpcaoDeAutor = { id: number; nome: string; temPerfil: boolean }

// Os membros que assinam algum artigo publicado. Autor de fora não entra: não há como saber que dois nomes
// iguais são a mesma pessoa. Dois membros com o mesmo nome aparecem com o ID, como no admin.
function autoresDosArtigos(artigos: ArticleSummary[]): OpcaoDeAutor[] {
  const porId = new Map<number, OpcaoDeAutor>()
  for (const artigo of artigos) {
    for (const autor of artigo.authors) {
      if (autor.member_id !== null && !porId.has(autor.member_id)) {
        porId.set(autor.member_id, { id: autor.member_id, nome: autor.name, temPerfil: autor.has_profile })
      }
    }
  }
  const opcoes = [...porId.values()]
  const repetidos = new Set(
    opcoes.map((o) => normaliza(o.nome)).filter((nome, i, todos) => todos.indexOf(nome) !== i)
  )
  return opcoes
    .map((o) => (repetidos.has(normaliza(o.nome)) ? { ...o, nome: `${o.nome} (ID ${o.id})` } : o))
    .sort((a, b) => a.nome.localeCompare(b.nome, "pt-BR"))
}

export default function Artigos() {
  const t = useTextos()
  usePageTitle(t("artigos.titulo"))
  const [artigos, setArtigos] = useState<ArticleSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [params, setParams] = useSearchParams()

  useEffect(() => {
    api
      .getArticles()
      .then((data) => setArtigos(data || []))
      .catch(() => setArtigos([]))
      .finally(() => setLoading(false))
  }, [])

  const autores = useMemo(() => autoresDosArtigos(artigos), [artigos])
  const autorId = Number(params.get("autor")) || null
  const autor = autores.find((a) => a.id === autorId) ?? null
  const visiveis = autorId ? artigos.filter((a) => a.authors.some((x) => x.member_id === autorId)) : artigos

  function escolheAutor(valor: string) {
    if (valor) setParams({ autor: valor })
    else setParams({})
  }

  return (
    <div className="artigos-page">
      <PageHero
        title={t("artigos.titulo")}
        lead={t("artigos.abertura")}
      />

      <section className="section">
        <div className="container">
          {loading ? (
            <p className="loading">Carregando...</p>
          ) : artigos.length === 0 ? (
            <p className="state-message">{t("artigos.vazio")}</p>
          ) : (
            <>
              {autores.length > 0 && (
                <div className="artigos-filtro">
                  <label htmlFor="filtro-autor">{t("artigos.filtro_autor")}</label>
                  <select id="filtro-autor" value={autorId ?? ""} onChange={(e) => escolheAutor(e.target.value)}>
                    <option value="">{t("artigos.todos_os_autores")}</option>
                    {autores.map((a) => (
                      <option key={a.id} value={a.id}>
                        {a.nome}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {autorId && (
                <div className="artigos-filtro__resumo">
                  {autor && <h2>{t("artigos.autor_titulo", { autor: autor.nome })}</h2>}
                  <div className="artigos-filtro__links">
                    {autor?.temPerfil && (
                      <Link to={`/equipe/${autor.id}`} className="link-arrow">
                        {t("artigos.ver_perfil")}
                        <ArrowRightIcon />
                      </Link>
                    )}
                    <Link to="/artigos" className="link-arrow">
                      {t("artigos.ver_todos")}
                      <ArrowRightIcon />
                    </Link>
                  </div>
                </div>
              )}

              {visiveis.length === 0 ? (
                <p className="state-message">{t("artigos.nenhum_do_autor")}</p>
              ) : (
                <div className="grid grid--3">
                  {visiveis.map((item) => (
                    <Link key={item.id} to={`/artigos/${item.slug || item.id}`} className="artigos-card">
                      <div className="artigos-card__image">
                        {item.image_url ? <img src={item.image_url} alt="" loading="lazy" /> : <span>ICC</span>}
                      </div>
                      <div className="artigos-card__body">
                        {item.date && <p className="artigos-card__meta">{formatDate(item.date)}</p>}
                        <h2 className="artigos-card__title">{item.title}</h2>
                        {item.authors.length > 0 && (
                          <p className="artigos-card__authors">
                            <AutoresDoArtigo autores={item.authors} />
                          </p>
                        )}
                        {item.description && <p className="artigos-card__desc">{item.description}</p>}
                        <span className="link-arrow artigos-card__cta">
                          {t("artigos.card_link")}
                          <ArrowRightIcon />
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </div>
  )
}
