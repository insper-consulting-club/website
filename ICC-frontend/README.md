# Frontend

Site público do Insper Consulting Club, em React 19, TypeScript e Vite. Todo o conteúdo vem da API do backend. O que fica fixo no código é a estrutura, os textos institucionais da Home e os links das redes sociais.

Para subir o projeto inteiro (banco, backend e frontend), siga o [`desenvolvimento.md`](../docs/desenvolvimento.md). Para rodar só o frontend contra uma API que aceite a origem `http://localhost:5173`:

```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000/api npm run dev
```

## Scripts

| Comando | O que faz |
|---|---|
| `npm run dev` | Servidor de desenvolvimento em `http://localhost:5173` |
| `npm run build` | Checa os tipos (`tsc`) e gera o site em `dist/` |
| `npm run lint` | ESLint |
| `npm run preview` | Serve o `dist/` localmente, para conferir o build |

Antes de abrir um PR, rode `npm run lint` e `npm run build`: os dois precisam passar.

## Variável de ambiente

| Variável | Valor |
|---|---|
| `VITE_API_URL` | Endereço da API, terminando em `/api`. Local: `http://localhost:8000/api` (o `docker-compose.yml` já define). Produção: `https://api.insperconsultingclub.com.br/api` |

As variáveis `VITE_*` entram no código **na hora do build**. Mudar o valor no Render exige um novo deploy do frontend. O link "Área administrativa" do rodapé é derivado dessa variável.

## Estrutura

```
frontend/
├── index.html           # Metadados estáticos (título, Open Graph) e carregamento da fonte
├── public/              # Favicon, ícone de iOS e imagem de compartilhamento
├── vite.config.ts
└── src/
    ├── main.tsx         # Rotas (cada página carrega sob demanda, exceto a Home)
    ├── App.tsx          # Layout: Header, conteúdo da rota e Footer
    ├── api.ts           # Todas as chamadas à API
    ├── types.ts         # Tipos dos dados que a API devolve
    ├── redes.ts         # E-mail e links do Instagram, LinkedIn e GitHub, num lugar só
    ├── index.css        # Design tokens e estilos globais
    ├── components/      # Header, Footer, PageHero, MemberCard, ProjetoCard, Icons, CargaInicial
    ├── hooks/           # usePageTitle, useProgramas, useDiretorias
    ├── images/          # Logo e imagens fixas
    └── pages/           # Uma pasta por página, com index.tsx e index.css
```

Cada página fica em `pages/<Nome>/` com o seu próprio CSS. Os estilos que valem para o site todo (botões, seções, grades, títulos) ficam em `index.css`.

## Rotas

| Rota | Pasta | Conteúdo |
|---|---|---|
| `/` | `Home` | Apresentação, liderança, números e carrossel de parceiros |
| `/equipe` | `Equipe` | Membros por diretoria |
| `/equipe/:id` | `PerfilMembro` | Perfil de um membro |
| `/parceiros` | `Parceiros` | Lista de parceiros |
| `/parceiros/:id` | `PerfilParceiro` | Perfil de um parceiro e seus projetos concluídos |
| `/projetos` | `Projetos` | Programas e a seção "Outros projetos" (projetos sem programa) |
| `/projetos/:slug` | `Programa` | Um programa, com os componentes ("Como funciona"), os projetos e os cases |
| `/projetos/projeto/:id` | `Projeto` | Um projeto: blocos de conteúdo, imagens, linha do tempo, parceiros e equipe |
| `/artigos` | `Artigos` | Lista de artigos |
| `/artigos/:slugOrId` | `Artigo` | Um artigo: resumo, temas, texto, "Como citar" e compartilhar |
| `/processo` | `Processo` | Processo seletivo ("Inscreva-se" ou "Inscrições encerradas", conforme o admin) |
| `/contato` | `Contato` | Canais oficiais |
| `/politica-de-privacidade` | `PoliticaPrivacidade` | Política de privacidade |
| qualquer outra | `NaoEncontrada` | Página 404 |

## Como o frontend usa a API

- Todas as chamadas estão em `src/api.ts`, e os formatos de resposta estão em `src/types.ts`. Ao mudar um endpoint ou um campo no backend, atualize os dois arquivos.
- As páginas buscam os dados ao abrir. Os hooks `useProgramas` e `useDiretorias` buscam uma vez e reaproveitam a lista, que alimenta os menus do Header e do Footer.
- A página de artigo usa `slugOrId`: a API aceita o slug do artigo ou o número dele.
- Os endereços das imagens vêm absolutos da API. Nos artigos, o texto chama as imagens por número (`![](imagem-1)`), e a página troca o número pelo endereço da imagem cadastrada.

### Artigos

O texto é exibido com `react-markdown`, `remark-gfm`, `remark-math` e `rehype-katex`. A biblioteca não executa HTML: marcação digitada no admin aparece como texto, e links `javascript:` são descartados. Só o `$$` abre fórmula, para que valores em reais (`R$ 10 mi`) continuem texto. O CSS e as fontes do KaTeX só carregam nessa página.

## Adicionar uma página

1. Crie `pages/<Nome>/index.tsx` (com `export default`) e `index.css`.
2. Registre a rota em `main.tsx`, no mesmo formato `lazy` das outras.
3. Se a página precisar de dados novos, acrescente a chamada em `api.ts` e o tipo em `types.ts`.
4. Se ela for para o menu, acrescente o item em `NAV` (`components/Header`) e em `NAVEGACAO` (`components/Footer`).
5. Use `usePageTitle` para o título da aba e `PageHero` para o cabeçalho das páginas internas.

## Design tokens

Definidos em `:root`, no início de `src/index.css`, a partir do guia de marca do ICC. Use as variáveis em vez de valores soltos.

| Grupo | Tokens |
|---|---|
| Cores da marca | `--vermelho-icc` (#b20000), `--vermelho-escuro` (#7b001e), `--preto`, `--branco`, `--gradiente-icc`, `--vermelho-suave` |
| Cinzas | `--cinza-50` a `--cinza-800` |
| Tipografia | `--font-display` e `--font-body` (Poppins), `--fs-display`, `--fs-h1` a `--fs-h3`, `--fs-lead`, `--fs-body`, `--fs-small`, `--fs-xs` |
| Layout | `--container` (1200px), `--container-narrow`, `--gutter`, `--section-y`, `--radius-sm`, `--radius`, `--shadow-sm`, `--shadow-md`, `--ease` |
| Cabeçalho | `--header-height`, atualizada pelo Header via `ResizeObserver` |

## Componentes reutilizáveis

| Componente | Uso |
|---|---|
| `Header` e `Footer` | Navegação do site. O submenu de Projetos e o de Equipe vêm da API |
| `PageHero` | Cabeçalho das páginas internas (título, subtítulo, eyebrow e link de voltar) |
| `MemberCard` | Card de membro (Home e Equipe) |
| `ProjetoCard` | Card de projeto (página do programa) |
| `Icons` | Ícones SVG (setas, redes sociais, menu), que herdam a cor do texto |
| `CargaInicial` | Tela exibida enquanto a primeira rota carrega |

Hooks: `usePageTitle(titulo, descricao)` define o título da aba e a descrição para compartilhamento.

## Observações

- **Prévia ao compartilhar um link:** o WhatsApp, o LinkedIn e similares não executam JavaScript e só leem o HTML estático do `index.html`. Por isso, a imagem e a descrição da prévia são as mesmas em todas as páginas, mesmo com o `usePageTitle` atualizando o título e as meta tags no navegador.
- **Fonte:** a Poppins é carregada do Google Fonts por um `<link>` no `index.html`.
- **Servidor de desenvolvimento:** o Vite usa verificação por polling (`vite.config.ts`), que funciona com o volume montado do Docker.
- **Single-page app:** o serviço de hospedagem precisa reescrever `/*` para `/index.html`. Sem isso, recarregar uma página interna dá 404 (ver [`operacao.md`](../docs/operacao.md)).
