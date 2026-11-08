import { Link } from "react-router-dom"
import usePageTitle from "../../hooks/usePageTitle"
import useTextos from "../../hooks/useTextos"
import { ArrowRightIcon } from "../../components/Icons"

export default function NaoEncontrada() {
  const t = useTextos()
  usePageTitle(t("nao_encontrada.titulo"))

  return (
    <section className="section">
      <div className="container container--narrow" style={{ textAlign: "center" }}>
        <p className="eyebrow">{t("nao_encontrada.eyebrow")}</p>
        <h1 className="page-hero__title" style={{ marginInline: "auto" }}>
          {t("nao_encontrada.titulo")}
        </h1>
        <p className="lead" style={{ marginInline: "auto" }}>
          {t("nao_encontrada.texto")}
        </p>
        <div style={{ marginTop: 32 }}>
          <Link to="/" className="btn btn--primary">
            {t("nao_encontrada.botao")}
            <ArrowRightIcon />
          </Link>
        </div>
      </div>
    </section>
  )
}
