// Mostrado só na primeiríssima carga da página, enquanto o App e a rota
// atual ainda estão baixando (ver main.tsx). Sem isso a tela ficava em
// branco até o JS terminar de carregar, em vez de dar algum sinal.
export default function CargaInicial() {
  return <div className="hydrate-fallback" aria-hidden="true" />
}
