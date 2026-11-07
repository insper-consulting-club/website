import { Outlet, ScrollRestoration, useLocation, useNavigation } from "react-router-dom"
import Header from "./components/Header"
import Footer from "./components/Footer"

function App() {
  const { pathname } = useLocation()
  const { state } = useNavigation()
  const isHome = pathname === "/"

  return (
    <>
      <a href="#conteudo" className="skip-link">Pular para o conteúdo</a>
      {/* Aparece só durante o carregamento do código de outra rota (code
          splitting): a navegação em si já é instantânea assim que baixado. */}
      <div className={`route-progress${state === "loading" ? " route-progress--active" : ""}`} aria-hidden="true" />
      <Header />
      <main id="conteudo" className={`page-outlet${isHome ? " page-outlet--flush" : ""}`}>
        <Outlet />
      </main>
      <Footer />
      <ScrollRestoration />
    </>
  )
}

export default App
