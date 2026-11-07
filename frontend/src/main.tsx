import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import Home from './pages/Home/index.tsx'
import CargaInicial from './components/CargaInicial.tsx'

// Cada rota carrega seu próprio código sob demanda (code splitting), exceto
// a Home: é a porta de entrada mais comum do site, então fica no pacote
// principal em vez de exigir mais uma viagem de rede pra quem chega aqui
// pela primeira vez.
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    // Cobre a primeiríssima carga: enquanto a rota batida pela URL ainda
    // está baixando, mostra isso em vez de tela em branco.
    HydrateFallback: CargaInicial,
    children: [
      { index: true, Component: Home },
      { path: "equipe", lazy: () => import('./pages/Equipe/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "equipe/:id", lazy: () => import('./pages/PerfilMembro/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "parceiros", lazy: () => import('./pages/Parceiros/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "projetos", lazy: () => import('./pages/Projetos/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "projetos/:slug", lazy: () => import('./pages/ProjetoDetalhe/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "projetos/projeto/:id", lazy: () => import('./pages/Projeto/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "parceiros/:id", lazy: () => import('./pages/PerfilParceiro/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "processo", lazy: () => import('./pages/Processo/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "artigos", lazy: () => import('./pages/Noticias/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "artigos/:slugOrId", lazy: () => import('./pages/Artigo/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "news", element: <Navigate to="/artigos" replace /> },
      { path: "contato", lazy: () => import('./pages/Contato/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "politica-de-privacidade", lazy: () => import('./pages/PoliticaPrivacidade/index.tsx').then((m) => ({ Component: m.default })) },
      { path: "*", lazy: () => import('./pages/NaoEncontrada/index.tsx').then((m) => ({ Component: m.default })) },
    ],
  },
])

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
