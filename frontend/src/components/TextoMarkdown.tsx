import Markdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"

// Texto escrito em Markdown no admin (Política de Privacidade, blocos dos
// programas). Links externos abrem em outra aba. HTML digitado no admin não é
// executado: o react-markdown o mostra como texto.
const componentes: Components = {
  a: ({ href, children }) =>
    href?.startsWith("http") ? (
      <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>
    ) : (
      <a href={href}>{children}</a>
    ),
}

export default function TextoMarkdown({ children }: { children: string }) {
  return (
    <Markdown remarkPlugins={[remarkGfm]} components={componentes}>
      {children}
    </Markdown>
  )
}
