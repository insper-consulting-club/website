import type { ReactNode } from "react"
import { Link, NavLink } from "react-router-dom"

type Props = {
  to: string
  externo: boolean
  className?: string
  children: ReactNode
  // Link do menu, que marca a página atual.
  menu?: boolean
  end?: boolean
}

// Item de navegação vindo do admin: página do site (navega dentro do app) ou
// link livre. Endereço externo abre em outra aba.
export default function LinkDoSite({ to, externo, className, children, menu, end }: Props) {
  if (externo) {
    return (
      <a
        href={to}
        className={className}
        {...(to.startsWith("http") ? { target: "_blank" } : {})}
        rel="noopener noreferrer"
      >
        {children}
      </a>
    )
  }
  if (menu) {
    return (
      <NavLink to={to} end={end} className={className}>
        {children}
      </NavLink>
    )
  }
  return (
    <Link to={to} className={className}>
      {children}
    </Link>
  )
}
