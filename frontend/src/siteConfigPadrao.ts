import { TEXTOS_PADRAO } from "./textosPadrao"
import type { SiteConfig } from "./types"

// Reserva usada enquanto a Configuração do site não chega da API, ou quando a
// chamada falha: o site continua com contatos e textos válidos. Os valores
// acompanham os que a migration do backend grava no primeiro registro; o que
// vale, depois, é o que estiver no admin. O texto da Política de Privacidade
// fica de fora de propósito: é longo, e a página avisa quando não o recebe.
export const SITE_CONFIG_PADRAO: SiteConfig = {
  site_name: "Liga Insper Consulting Club",
  site_description:
    "A Liga Insper Consulting Club é uma organização estudantil dedicada ao desenvolvimento de futuros consultores.",
  logo_url: null,
  favicon_url: null,
  og_image_url: null,
  email: "insperconsultingclub@gmail.com",
  instagram_url: "https://www.instagram.com/insperconsultingclub/",
  instagram_label: "@insperconsultingclub",
  linkedin_url: "https://br.linkedin.com/company/insperconsultingclub",
  linkedin_label: "Insper Consulting Club",
  github_url: "https://github.com/insper-consulting-club",
  github_label: "insper-consulting-club",
  home_hero_title: "O futuro consultor começa no ICC",
  home_statement: "Preparamos nossos membros para os processos seletivos mais exigentes do mercado.",
  home_about_title: "Mais do que um clube, somos um ambiente de formação",
  home_about_title_highlight: "para futuros consultores.",
  home_about_text:
    "A Liga Insper Consulting Club é uma organização estudantil fundada em 2020, dedicada ao desenvolvimento de futuros consultores. Ao longo do semestre, promovemos capacitações, resolução de cases, visitas corporativas e iniciativas que aproximam nossos membros da realidade das principais empresas do mercado.",
  home_about_photo_url: null,
  home_about_photo_alt: "Membros da Liga Insper Consulting Club na reunião inaugural",
  mission:
    "Conectar alunos do Insper ao mercado de consultoria, desenvolvendo as competências técnicas e comportamentais exigidas pelas principais firmas do setor.",
  mission_how:
    "Treinamento para processos seletivos (GMAT, Verbal, Data e Fit Interview) e capacitação prática na resolução de cases reais de negócio.",
  mission_goal:
    "Consolidar o ICC como referência em consultoria entre os clubes estudantis do Brasil e expandir a atuação para tecnologia e empreendedorismo.",
  home_cta_title: "Pronto para dar o próximo passo na sua carreira?",
  footer_tagline: "Mais do que um clube, somos um ambiente de formação para futuros consultores.",
  team_lead: "Conheça os membros que fazem parte da Liga Insper Consulting Club",
  partners_lead:
    "Conheça as empresas que apoiam o Insper Consulting Club e contribuem para a formação dos futuros líderes em consultoria.",
  partners_benefits_title: "O que sua empresa ganha ao apoiar o Insper Consulting Club",
  projects_lead:
    "Como formamos consultores, do primeiro semestre na entidade aos cases reais resolvidos ao longo da Jornada do Consultor.",
  featured_program_slug: "jornada-do-consultor",
  articles_lead: "Artigos e publicações produzidos por membros do ICC",
  contact_lead: "Entre em contato com o Insper Consulting Club",
  process_lead: "Participe do processo seletivo e faça parte da Liga Insper Consulting Club",
  process_closed_message:
    "Inscrições encerradas. Acompanhe nosso Instagram para saber quando abrirmos o próximo processo.",
  privacy_updated: "novembro de 2026",
  privacy_text: "",
  texts: TEXTOS_PADRAO,
  nav_items: [
    { id: 0, label: "Nossa Equipe", area: "menu", page: "equipe", path: "/equipe", external: false, order: 1 },
    { id: 1, label: "Parceiros", area: "menu", page: "parceiros", path: "/parceiros", external: false, order: 2 },
    { id: 2, label: "Projetos", area: "menu", page: "projetos", path: "/projetos", external: false, order: 3 },
    { id: 3, label: "Artigos", area: "menu", page: "artigos", path: "/artigos", external: false, order: 4 },
    { id: 4, label: "Seja membro", area: "rodape", page: "processo", path: "/processo", external: false, order: 5 },
    { id: 5, label: "Contato", area: "menu", page: "contato", path: "/contato", external: false, order: 6 },
    { id: 6, label: "Seja membro", area: "botao", page: "processo", path: "/processo", external: false, order: 7 },
  ],
  partner_benefits: [
    {
      id: 0,
      title: "Acesso a talentos",
      description:
        "Contato direto com alunos de alta performance, treinados em resolução de cases e raciocínio analítico.",
      order: 1,
    },
    {
      id: 1,
      title: "Visibilidade Institucional",
      description:
        "Presença em eventos, capacitações e redes sociais com crescimento consistente de alcance e engajamento.",
      order: 2,
    },
    {
      id: 2,
      title: "Cases aplicados à realidade",
      description:
        "Possibilidade de propor desafios reais de negócio para serem resolvidos pelos nossos grupos de trainees e do Pedagógico.",
      order: 3,
    },
  ],
}
