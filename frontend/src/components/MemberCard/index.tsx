import { useState } from "react";
import { Link } from "react-router-dom";
import { LinkedInIcon } from "../Icons";
import "./index.css";

type Member = {
  id: number;
  name: string;
  position: string;
  photo_url: string | null;
  linkedin?: string | null;
};

function iniciais(nome: string) {
  return nome
    .split(" ")
    .filter(Boolean)
    .map((parte) => parte[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export default function MemberCard({ member, roleOverride }: { member: Member; roleOverride?: string }) {
  const [fotoQuebrada, setFotoQuebrada] = useState(false);

  return (
    <article className="member-card">
      <Link to={`/equipe/${member.id}`} className="member-card__link">
        <div className="member-card__photo">
          {member.photo_url && !fotoQuebrada ? (
            <img
              src={member.photo_url}
              alt={member.name}
              loading="lazy"
              onError={() => setFotoQuebrada(true)}
            />
          ) : (
            <span className="member-card__initials" aria-hidden="true">{iniciais(member.name)}</span>
          )}
        </div>
        <h3 className="member-card__name">{member.name}</h3>
      </Link>
      <div className="member-card__footer">
        <p className="member-card__role">{roleOverride || member.position}</p>
        {member.linkedin && (
          <a
            href={member.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="member-card__linkedin"
            aria-label={`LinkedIn de ${member.name}`}
          >
            <LinkedInIcon size={15} />
          </a>
        )}
      </div>
    </article>
  );
}
