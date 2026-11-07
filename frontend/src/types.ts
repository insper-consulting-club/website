export interface ActivityCategory {
  id: number
  slug: string
  label: string
  subtitle: string
  description: string
  highlights: string[]
  icon_url: string | null
  badge: string
  badge_class: string
  signup_url: string
  order: number
}

export interface SuccessCaseParticipant {
  member_id: number
  name: string
  linkedin: string | null
  role: "integrante" | "mentor"
  order: number
}

export interface SuccessCase {
  id: number
  category: string
  semester: string
  title: string
  area: string
  theme: string
  panel: string[]
  award: string
  publication_url: string
  participants: SuccessCaseParticipant[]
  order: number
}

export interface CalendarMonth {
  id: number
  month: string
  year: number | null
  items: string[]
  semester: '1' | '2' | 'both'
  order: number
}

export interface ProjectImage {
  id: number
  image_url: string
  caption: string
  order: number
}

export interface TimelineEvent {
  id: number
  date: string
  title: string
  description: string
  order: number
}

export interface ContentBlock {
  id: number
  title: string
  text: string
  image_url: string | null
  image_caption: string
  image_align: 'left' | 'right' | 'center'
  order: number
}

export interface Project {
  id: number
  title: string
  description: string
  category: string | null
  partners: string[]
  start_date: string
  end_date: string | null
}

export interface ProjectDetail {
  id: number
  title: string
  description: string
  category: ActivityCategory | null
  start_date: string
  end_date: string | null
  partners: { id: number; name: string }[]
  members: { id: number; name: string }[]
  images: ProjectImage[]
  timeline_events: TimelineEvent[]
  content_blocks: ContentBlock[]
}

export interface ActivityImage {
  id: number
  image_url: string
  caption: string
  order: number
}

export interface Activity {
  id: number
  title: string
  description: string
  category: string | null
}

export interface ActivityDetail {
  id: number
  title: string
  description: string
  category: ActivityCategory | null
  images: ActivityImage[]
  content_blocks: ContentBlock[]
  responsible_partner: {
    id: number
    name: string
    logo_url: string | null
  } | null
}

export interface DirectorateMembership {
  directorate: string
  directorate_slug: string
  cargo: string
  order: number
}

export interface Directorate {
  id: number
  name: string
  slug: string
  order: number
}

export interface Member {
  id: number
  name: string
  position: string
  position_power: number | null
  directorate_memberships: DirectorateMembership[]
  photo_url: string | null
  linkedin: string | null
}

export interface TrajetoriaEtapa {
  semestre: string
  cargo: string
}

export interface MemberDetail extends Member {
  biography: string
  number_of_projects: number
  hours: number
  entry_date: string
  exit_date: string | null
  linkedin: string | null
  projects: Project[]
  trajetoria: TrajetoriaEtapa[]
}

export interface Partner {
  id: number
  name: string
  logo_url: string | null
  description: string
  category: string | null
}

export type PartnerDetail = Partner

export interface Statistic {
  id: number
  value: string
  description: string
  order: number
}

export interface NewsItem {
  id: number
  slug: string | null
  title: string
  description: string
  link: string
  image_url: string | null
  source: string
  date: string | null
  order: number
  authors: string
  topics: string
  content: string
  images: ArticleImage[]
}

// Imagem chamada no texto do artigo como ![](imagem-<number>).
export interface ArticleImage {
  number: number
  image_url: string | null
  caption: string
}

export interface ContactInfo {
  id: number
  email: string
  instagram: string
  linkedin: string
  whatsapp: string
}

export interface SelectionProcessStage {
  id: number
  label: string
  date: string
  order: number
}

export interface SelectionProcessStep {
  id: number
  number: string
  title: string
  description: string
  image_url: string | null
  duration: string
  tips: string[]
  order: number
}

export interface SelectionProcessRequirement {
  id: number
  text: string
  icon_url: string | null
  order: number
}

export interface SelectionProcess {
  id: number
  title: string
  stages: SelectionProcessStage[]
  steps: SelectionProcessStep[]
  requirements: SelectionProcessRequirement[]
  materials: PreparationMaterial[]
  registrations_open: boolean
  registration_url: string
}


export interface PreparationMaterialItem {
  id: number
  text: string
  order: number
}

export interface PreparationMaterial {
  id: number
  title: string
  items: PreparationMaterialItem[]
  order: number
}
