import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../../api";
import type { MemberDetail } from "../../types";
import { ArrowLeftIcon, LinkedInIcon } from "../../components/Icons";
import usePageTitle from "../../hooks/usePageTitle";
import "./index.css";

export default function PerfilMembro() {
  const { id } = useParams();
  const [member, setMember] = useState<MemberDetail | null>(null);
  const [loadedId, setLoadedId] = useState<string | undefined>();
  const loading = loadedId !== id;
  usePageTitle(member?.name, member?.position);

  useEffect(() => {
    if (!id) return;
    api
      .getMember(Number(id))
      .then((data) => setMember(data && data.id ? data : null))
      .catch(() => setMember(null))
      .finally(() => setLoadedId(id));
  }, [id]);

  if (loading) return <p className="loading">Carregando...</p>;

  if (!member) {
    return (
      <section className="section">
        <div className="container">
          <Link to="/equipe" className="back-link">
            <ArrowLeftIcon size={14} />
            Voltar para a equipe
          </Link>
          <p className="state-message">
            <strong>Membro não encontrado</strong>
            O perfil procurado não existe ou foi removido.
          </p>
        </div>
      </section>
    );
  }

  // Uma pessoa pode ter mais de um cargo ao mesmo tempo (ex: diretora de
  // Pedagógico e também mentora); directorate_memberships é a fonte de
  // verdade do que é atual, então o título e o "Atual" na trajetória usam os
  // mesmos cargos.
  const memberships = member.directorate_memberships ?? [];
  const cargosAtuais = memberships.map((m) => m.cargo);
  const cargoTitulo = cargosAtuais.length > 0 ? cargosAtuais.join(" e ") : member.position;
  const trajetoria = member.trajetoria ?? [];
  // "Atual" marca só o semestre mais recente da trajetória. Conferir apenas o
  // cargo marcaria também um semestre antigo em que a pessoa ocupou o mesmo
  // cargo, como quem foi mentor, saiu da função e voltou a ela depois.
  const ultimoSemestre = trajetoria.map((e) => e.semestre).sort().at(-1);

  return (
    <div className="membro-page">
      <div className="container">
        <Link to="/equipe" className="back-link membro-back">
          <ArrowLeftIcon size={14} />
          Voltar para a equipe
        </Link>

        <section className="membro-hero">
          <div className="membro-hero__photo">
            {member.photo_url ? (
              <img src={member.photo_url} alt={member.name} />
            ) : (
              <span aria-hidden="true">{member.name.charAt(0)}</span>
            )}
          </div>

          <div className="membro-hero__info">
            {memberships.length > 0 && (
              <p className="eyebrow">
                {memberships.map((m, i) => (
                  <span key={m.directorate}>
                    {i > 0 && " · "}
                    <Link to={`/equipe#${m.directorate_slug}`}>{m.directorate}</Link>
                  </span>
                ))}
              </p>
            )}
            <h1 className="membro-hero__name">{member.name}</h1>
            <p className="membro-hero__role">{cargoTitulo}</p>

            {member.linkedin && (
              <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="btn btn--secondary btn--sm membro-hero__linkedin">
                <LinkedInIcon size={16} />
                LinkedIn
              </a>
            )}

            {trajetoria.length > 0 && (
              <div className="membro-trajetoria">
                <h2 className="membro-trajetoria__title">Trajetória no ICC</h2>
                <ol className="membro-trajetoria__list">
                  {trajetoria.map((etapa, i) => {
                    const isAtual = etapa.semestre === ultimoSemestre && cargosAtuais.includes(etapa.cargo);
                    return (
                      <li key={i} className={isAtual ? "is-atual" : undefined}>
                        <span className="membro-trajetoria__semestre">{etapa.semestre}</span>
                        <span className="membro-trajetoria__cargo">{etapa.cargo}</span>
                        {isAtual && <span className="tag tag--accent">Atual</span>}
                      </li>
                    );
                  })}
                </ol>
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
