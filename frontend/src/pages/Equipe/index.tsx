import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import MemberCard from "../../components/MemberCard";
import PageHero from "../../components/PageHero";
import usePageTitle from "../../hooks/usePageTitle";
import { api } from "../../api";
import type { Member } from "../../types";
import "./index.css";

type Group = { directorate: string; slug: string; members: { member: Member; cargo: string; order: number }[] };

export default function Equipe() {
  usePageTitle("Nossa Equipe", "Conheça os membros que fazem parte da Liga Insper Consulting Club");
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    api
      .getMembers()
      .then((data) => setMembers(data))
      .finally(() => setLoading(false));
  }, []);

  // Rola até a diretoria certa quando a página é aberta (ou o hash muda)
  // via link com âncora, ex: /equipe#marketing, vindo do dropdown do header.
  useEffect(() => {
    if (loading || !location.hash) return;
    const id = decodeURIComponent(location.hash.replace("#", ""));
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
  }, [loading, location.hash]);

  // A API já retorna os membros ordenados pela primeira diretoria de cada
  // um, então basta agrupar preservando a ordem de chegada. Quem está em mais
  // de uma diretoria aparece em cada seção, com o cargo daquela diretoria.
  const groups: Group[] = [];
  for (const member of members) {
    const memberships = member.directorate_memberships.length > 0
      ? member.directorate_memberships
      : [{ directorate: "Outros", directorate_slug: "outros", cargo: member.position, order: 0 }];

    for (const { directorate, directorate_slug, cargo, order } of memberships) {
      let group = groups.find((g) => g.directorate === directorate);
      if (!group) {
        group = { directorate, slug: directorate_slug, members: [] };
        groups.push(group);
      }
      group.members.push({ member, cargo, order });
    }
  }

  // Dentro de cada diretoria, a ordem do vínculo manda: o diretor daquela
  // área sempre vem primeiro.
  for (const group of groups) {
    group.members.sort((a, b) => a.order - b.order);
  }

  return (
    <div className="equipe-page">
      <PageHero
        eyebrow="Membros"
        title="Nossa Equipe"
        lead="Conheça os membros que fazem parte da Liga Insper Consulting Club"
      />

      {!loading && groups.length > 0 && (
        <nav className="equipe-nav" aria-label="Diretorias">
          <div className="container equipe-nav__inner">
            {groups.map((group) => (
              <a key={group.directorate} href={`#${group.slug}`} className="equipe-nav__link">
                {group.directorate}
              </a>
            ))}
          </div>
        </nav>
      )}

      <div className="container equipe-body">
        {loading ? (
          <p className="loading">Carregando equipe...</p>
        ) : groups.length === 0 ? (
          <p className="state-message">Nenhum membro cadastrado no momento.</p>
        ) : (
          groups.map((group) => (
            <section className="equipe-group" id={group.slug} key={group.directorate}>
              <div className="equipe-group__head">
                <h2 className="equipe-group__title">{group.directorate}</h2>
                <span className="equipe-group__count">
                  {group.members.length} {group.members.length === 1 ? "membro" : "membros"}
                </span>
              </div>
              <div className="grid grid--4 equipe-group__grid">
                {group.members.map(({ member, cargo }) => (
                  <MemberCard key={member.id} member={member} roleOverride={cargo} />
                ))}
              </div>
            </section>
          ))
        )}
      </div>
    </div>
  );
}
