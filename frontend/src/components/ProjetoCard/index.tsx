import { Link } from "react-router-dom"
import type { Project } from "../../types"
import { ArrowRightIcon } from "../Icons"
import "./index.css"

function formatDateBR(dateString: string) {
  // new Date("AAAA-MM-DD") seria meia-noite UTC, que em Brasília já é o dia
  // anterior; com ano/mês/dia separados, a data fica no fuso local.
  const [ano, mes, dia] = dateString.split("-").map(Number)
  return new Date(ano, mes - 1, dia).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric" })
}

export default function ProjetoCard({ projeto }: { projeto: Project }) {
  return (
    <Link to={`/projetos/projeto/${projeto.id}`} className="card projeto-card">
      {projeto.partners.length > 0 && (
        <p className="projeto-card__parceiros">Com {projeto.partners.join(", ")}</p>
      )}
      <h3 className="projeto-card__titulo">{projeto.title}</h3>
      {projeto.description && <p className="projeto-card__descricao">{projeto.description}</p>}
      <p className="projeto-card__meta">
        {projeto.end_date ? `Concluído em ${formatDateBR(projeto.end_date)}` : "Em andamento"}
      </p>
      <span className="link-arrow">
        Ver projeto
        <ArrowRightIcon />
      </span>
    </Link>
  )
}
