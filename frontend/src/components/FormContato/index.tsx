import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./index.css";
import { api } from "../../api";
import { ArrowRightIcon, CheckIcon } from "../Icons";

type ContactType = "aluno" | "empresa" | "alumni" | "imprensa" | "outro";
type Status = "idle" | "enviando" | "sucesso" | "erro";

const VAZIO = { nome: "", email: "", phone: "", contactType: "", message: "" };

export default function FormContato() {
  const [campos, setCampos] = useState(VAZIO);
  const [status, setStatus] = useState<Status>("idle");

  const atualizar =
    (campo: keyof typeof VAZIO) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
      setCampos((atual) => ({ ...atual, [campo]: e.target.value }));

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setStatus("enviando");
    try {
      await api.postContact({
        name: campos.nome,
        email: campos.email,
        phone: campos.phone,
        contact_type: campos.contactType as ContactType,
        message: campos.message,
      });
      setCampos(VAZIO);
      setStatus("sucesso");
    } catch {
      setStatus("erro");
    }
  };

  if (status === "sucesso") {
    return (
      <div className="form-contato__sucesso" role="status">
        <span className="form-contato__sucesso-icon">
          <CheckIcon size={24} />
        </span>
        <h2>Muito obrigado!</h2>
        <p>Entraremos em contato em breve.</p>
        <button type="button" className="btn btn--secondary btn--sm" onClick={() => setStatus("idle")}>
          Enviar outra mensagem
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="form-contato">
      <div className="form-contato__row">
        <div className="campo">
          <label htmlFor="nome">Nome</label>
          <input id="nome" type="text" autoComplete="name" placeholder="Nome completo" required value={campos.nome} onChange={atualizar("nome")} />
        </div>
        <div className="campo">
          <label htmlFor="email">E-mail</label>
          <input id="email" type="email" autoComplete="email" placeholder="exemplo@email.com" required value={campos.email} onChange={atualizar("email")} />
        </div>
      </div>

      <div className="form-contato__row">
        <div className="campo">
          <label htmlFor="telefone">Telefone</label>
          <input id="telefone" type="tel" autoComplete="tel" placeholder="(11) 91234-5678" required value={campos.phone} onChange={atualizar("phone")} />
        </div>
        <div className="campo">
          <label htmlFor="tipo-contato">Você é</label>
          <select id="tipo-contato" required value={campos.contactType} onChange={atualizar("contactType")}>
            <option value="" disabled>
              Escolha uma opção
            </option>
            <option value="aluno">Aluno do Insper</option>
            <option value="empresa">Empresa / Parceiro</option>
            <option value="alumni">Ex-aluno do ICC</option>
            <option value="imprensa">Imprensa</option>
            <option value="outro">Outro</option>
          </select>
        </div>
      </div>

      <div className="campo">
        <label htmlFor="mensagem">Mensagem</label>
        <textarea id="mensagem" placeholder="Escreva sua mensagem aqui" rows={6} required value={campos.message} onChange={atualizar("message")} />
      </div>

      {status === "erro" && (
        <p className="form-contato__erro" role="alert">
          Não foi possível enviar sua mensagem agora. Tente novamente em instantes ou escreva para insperconsultingclub@gmail.com.
        </p>
      )}

      <div className="form-contato__footer">
        <p className="form-contato__termos">
          Enviando esse formulário, você aceita a{" "}
          <Link to="/politica-de-privacidade" target="_blank" rel="noopener noreferrer">
            Política de Privacidade
          </Link>{" "}
          do ICC.
        </p>
        <button type="submit" className="btn btn--primary" disabled={status === "enviando"}>
          {status === "enviando" ? "Enviando..." : "Enviar mensagem"}
          {status !== "enviando" && <ArrowRightIcon />}
        </button>
      </div>
    </form>
  );
}
