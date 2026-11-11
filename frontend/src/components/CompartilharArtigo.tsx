import { useEffect, useRef, useState } from "react"
import useTextos from "../hooks/useTextos"
import { CheckIcon, CopyIcon, LinkedInIcon, ShareIcon, WhatsAppIcon } from "./Icons"

type Props = { titulo: string; url: string }

// Botão "Compartilhar". No celular abre a folha de compartilhamento do sistema (WhatsApp, Instagram, e-mail...).
// No computador abre um menu com LinkedIn, WhatsApp e Copiar link.
export default function CompartilharArtigo({ titulo, url }: Props) {
  const t = useTextos()
  const [aberto, setAberto] = useState(false)
  const [copiado, setCopiado] = useState(false)
  const caixa = useRef<HTMLDivElement>(null)
  const nativo = typeof navigator.share === "function" && window.matchMedia("(pointer: coarse)").matches

  useEffect(() => {
    if (!aberto) return
    const fora = (e: MouseEvent) => {
      if (!caixa.current?.contains(e.target as Node)) setAberto(false)
    }
    const esc = (e: KeyboardEvent) => e.key === "Escape" && setAberto(false)
    document.addEventListener("mousedown", fora)
    document.addEventListener("keydown", esc)
    return () => {
      document.removeEventListener("mousedown", fora)
      document.removeEventListener("keydown", esc)
    }
  }, [aberto])

  async function aoClicar() {
    if (!nativo) {
      setAberto((a) => !a)
      return
    }
    try {
      await navigator.share({ title: titulo, url })
    } catch {
      /* o leitor fechou a folha de compartilhamento */
    }
  }

  async function copia() {
    try {
      await navigator.clipboard.writeText(url)
      setCopiado(true)
      setTimeout(() => setCopiado(false), 2000)
    } catch {
      /* sem permissão para a área de transferência: o endereço continua na barra do navegador */
    }
  }

  return (
    <div className="compartilhar" ref={caixa}>
      <button
        type="button"
        className="btn btn--secondary btn--sm"
        onClick={aoClicar}
        aria-haspopup={nativo ? undefined : "menu"}
        aria-expanded={nativo ? undefined : aberto}
      >
        <ShareIcon size={16} />
        {t("artigo.compartilhar")}
      </button>
      {aberto && (
        <div className="compartilhar__menu" role="menu">
          <a
            role="menuitem"
            href={`https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(url)}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <LinkedInIcon size={16} />
            LinkedIn
          </a>
          <a
            role="menuitem"
            href={`https://wa.me/?text=${encodeURIComponent(`${titulo} ${url}`)}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            <WhatsAppIcon size={16} />
            WhatsApp
          </a>
          <button type="button" role="menuitem" onClick={copia}>
            {copiado ? <CheckIcon size={16} /> : <CopyIcon size={16} />}
            {copiado ? t("artigo.link_copiado") : t("artigo.copiar_link")}
          </button>
        </div>
      )}
    </div>
  )
}
