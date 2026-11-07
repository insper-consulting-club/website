import type { ReactNode } from "react"
import { Link } from "react-router-dom"
import { ArrowLeftIcon } from "./Icons"

type PageHeroProps = {
  eyebrow?: string
  title: ReactNode
  lead?: ReactNode
  back?: { to: string; label: string }
  children?: ReactNode
}

export default function PageHero({ eyebrow, title, lead, back, children }: PageHeroProps) {
  return (
    <header className="page-hero">
      <div className="container">
        {back && (
          <Link to={back.to} className="back-link">
            <ArrowLeftIcon size={14} />
            {back.label}
          </Link>
        )}
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1 className="page-hero__title">{title}</h1>
        {lead && <p className="lead">{lead}</p>}
        {children}
      </div>
    </header>
  )
}
