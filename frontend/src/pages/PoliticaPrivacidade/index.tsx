import PageHero from "../../components/PageHero"
import usePageTitle from "../../hooks/usePageTitle"
import "./index.css"

export default function PoliticaPrivacidade() {
  usePageTitle("Política de Privacidade")

  return (
    <div className="politica-page">
      <PageHero title="Política de Privacidade" lead="Última atualização: setembro de 2026" />

      <section className="section">
      <article className="container container--narrow politica-content">
        <p>
          Esta política explica quais dados a Liga Insper Consulting Club
          (ICC) coleta através do formulário de contato deste site, para que
          eles são usados e quais direitos você tem sobre eles, em
          conformidade com a Lei Geral de Proteção de Dados (Lei nº
          13.709/2018).
        </p>

        <h2>1. Quais dados coletamos</h2>
        <p>
          Quando você preenche o formulário de contato, coletamos: nome
          completo, e-mail, telefone, o tipo de contato que você selecionou
          (aluno do Insper, empresa/parceiro, ex-aluno do ICC, imprensa ou
          outro) e a mensagem que você escreve. Não coletamos esses dados por
          nenhum outro meio deste site.
        </p>

        <h2>2. Para que usamos esses dados</h2>
        <p>
          Usamos os dados enviados exclusivamente para responder ao seu
          contato: entender sua solicitação, retornar por e-mail ou telefone
          e, quando aplicável, dar seguimento a propostas de parceria ou
          dúvidas sobre o processo seletivo. Não usamos esses dados para
          enviar comunicações que você não solicitou, nem os vendemos ou
          cedemos a terceiros para fins de marketing.
        </p>

        <h2>3. Com quem compartilhamos</h2>
        <p>
          Os dados do formulário são enviados por e-mail à diretoria do ICC
          responsável por contato, usando o serviço SendGrid como
          intermediário técnico de envio. O SendGrid processa essa mensagem
          apenas para entregá-la; o ICC não compartilha seus dados com
          nenhum outro terceiro.
        </p>

        <h2>4. Cookies e rastreamento</h2>
        <p>
          Este site não usa cookies de rastreamento nem ferramentas de
          análise de terceiros. Não fazemos publicidade direcionada nem
          perfilamento de visitantes.
        </p>

        <h2>5. Por quanto tempo guardamos seus dados</h2>
        <p>
          Mantemos os dados de contato pelo tempo necessário para responder
          sua solicitação e, depois disso, por um período razoável caso seja
          preciso retomar a conversa (por exemplo, uma parceria em
          andamento). Você pode pedir a exclusão a qualquer momento, como
          descrito abaixo.
        </p>

        <h2>6. Seus direitos</h2>
        <p>
          Você pode, a qualquer momento, pedir para: confirmar se temos
          dados seus, acessar esses dados, corrigir informações incompletas
          ou desatualizadas, ou solicitar a exclusão dos seus dados de
          nossos registros. Para exercer qualquer um desses direitos, entre
          em contato pelo e-mail abaixo.
        </p>

        <h2>7. Contato</h2>
        <p>
          Dúvidas sobre esta política ou sobre o tratamento dos seus dados
          podem ser enviadas para{" "}
          <a href="mailto:insperconsultingclub@gmail.com">
            insperconsultingclub@gmail.com
          </a>
          .
        </p>
      </article>
      </section>
    </div>
  )
}
