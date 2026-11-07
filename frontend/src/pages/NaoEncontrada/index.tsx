import { Link } from "react-router-dom"
import usePageTitle from "../../hooks/usePageTitle"
import { ArrowRightIcon } from "../../components/Icons"

export default function NaoEncontrada() {
  usePageTitle("Página não encontrada")

  return (
    <section className="section">
      <div className="container container--narrow" style={{ textAlign: "center" }}>
        <p className="eyebrow">Erro 404</p>
        <h1 className="page-hero__title" style={{ marginInline: "auto" }}>
          Página não encontrada
        </h1>
        <p className="lead" style={{ marginInline: "auto" }}>
          O endereço acessado não existe ou foi alterado.
        </p>
        <div style={{ marginTop: 32 }}>
          <Link to="/" className="btn btn--primary">
            Voltar para o início
            <ArrowRightIcon />
          </Link>
        </div>
      </div>
    </section>
  )
}
