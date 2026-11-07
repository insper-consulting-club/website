const apiUrl = import.meta.env.VITE_API_URL;

const headers = {
  "Accept": "application/json",
  "Content-Type": "application/json",
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

  getCategories: () =>
    fetch(`${apiUrl}/categories/`, { headers }).then((res) => res.json()),

  getCalendar: (semester?: string) =>
    fetch(`${apiUrl}/calendar/${semester ? `?semester=${semester}` : ""}`, { headers }).then((res) => res.json()),

  getProjects: (category?: string) =>
    fetch(`${apiUrl}/projects/${category ? `?category=${category}` : ""}`, { headers }).then((res) => res.json()),

  getProject: (id: number) =>
    fetch(`${apiUrl}/projects/${id}/`, { headers }).then((res) => res.json()),

  getSuccessCases: (category?: string) =>
    fetch(`${apiUrl}/success-cases/${category ? `?category=${category}` : ""}`, { headers }).then((res) => res.json()),

  getActivities: (category?: string) =>
    fetch(`${apiUrl}/activities/${category ? `?category=${category}` : ""}`, { headers }).then((res) => res.json()),

  getActivity: (id: number) =>
    fetch(`${apiUrl}/activities/${id}/`, { headers }).then((res) => res.json()),

  getStatistics: () =>
    fetch(`${apiUrl}/statistics/`, { headers }).then((res) => res.json()),

  getNews: () =>
    fetch(`${apiUrl}/news/`, { headers }).then((res) => res.json()),

  getNewsItem: (identifier: string | number) =>
    fetch(`${apiUrl}/news/${identifier}/`, { headers }).then((res) => res.json()),

  getContact: () =>
    fetch(`${apiUrl}/contact/`, { headers }).then((res) => res.json()),

  getSelectionProcess: () =>
    fetch(`${apiUrl}/selection-process/`, { headers }).then((res) => res.json()),

  postContact: (data: {name: string; email: string; phone: string; contact_type: "aluno" | "empresa" | "alumni" | "imprensa" | "outro"; message: string}) =>
    fetch(`${apiUrl}/contact/`, {
      method: "POST",
      headers,
      body: JSON.stringify(data),
    }).then((res) => {
      if (!res.ok) return res.json().then((err) => Promise.reject(err));
      return res.json();
    }),
};