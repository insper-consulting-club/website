const apiUrl = import.meta.env.VITE_API_URL;

// Só cabeçalhos que o navegador aceita sem consulta prévia (preflight CORS).
// Um "Content-Type" em um GET faria cada endpoint novo custar uma requisição OPTIONS a mais.
const headers = {
  "Accept": "application/json",
};

export const api = {
  getMembers: () =>
    fetch(`${apiUrl}/members/`, { headers }).then((res) => res.json()),

  getMember: (id: number) =>
    fetch(`${apiUrl}/members/${id}/`, { headers }).then((res) => res.json()),

  getPartners: () =>
    fetch(`${apiUrl}/partners/`, { headers }).then((res) => res.json()),

  getPartner: (id: number) =>
    fetch(`${apiUrl}/partners/${id}/`, { headers }).then((res) => res.json()),

  getDirectorates: () =>
    fetch(`${apiUrl}/directorates/`, { headers }).then((res) => res.json()),

  getPrograms: () =>
    fetch(`${apiUrl}/programs/`, { headers }).then((res) => res.json()),

  getProgram: (slug: string) =>
    fetch(`${apiUrl}/programs/${slug}/`, { headers }).then((res) => res.json()),

  getProjects: (program?: string) =>
    fetch(`${apiUrl}/projects/${program ? `?program=${program}` : ""}`, { headers }).then((res) => res.json()),

  getProject: (id: number) =>
    fetch(`${apiUrl}/projects/${id}/`, { headers }).then((res) => res.json()),

  getProgramCases: (program?: string) =>
    fetch(`${apiUrl}/program-cases/${program ? `?program=${program}` : ""}`, { headers }).then((res) => res.json()),

  getComponents: (program?: string) =>
    fetch(`${apiUrl}/components/${program ? `?program=${program}` : ""}`, { headers }).then((res) => res.json()),

  getStatistics: () =>
    fetch(`${apiUrl}/statistics/`, { headers }).then((res) => res.json()),

  getArticles: () =>
    fetch(`${apiUrl}/articles/`, { headers }).then((res) => res.json()),

  getArticle: (identifier: string | number) =>
    fetch(`${apiUrl}/articles/${identifier}/`, { headers }).then((res) => res.json()),

  getSelectionProcess: () =>
    fetch(`${apiUrl}/selection-process/`, { headers }).then((res) => res.json()),

  getSiteConfig: () =>
    fetch(`${apiUrl}/site-config/`, { headers }).then((res) => res.json()),
};