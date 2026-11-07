import PageHero from "../../components/PageHero"
import usePageTitle from "../../hooks/usePageTitle"
import { REDES } from "../../redes"
import "./index.css"

export default function PoliticaPrivacidade() {
  usePageTitle("Política de Privacidade")

  return (
    <div className="politica-page">
      <PageHero title="Política de Privacidade" lead="Última atualização: novembro de 2026" />

      <section className="section">
      <article className="container container--narrow politica-content">
        <p>
          Esta política explica como o site do Insper Consulting Club (ICC)
          trata os dados pessoais de quem o visita, em conformidade com a Lei
          Geral de Proteção de Dados (Lei nº 13.709/2018).
        </p>

        <h2>1. Quais dados coletamos</h2>
        <p>
          O site não tem formulários, cadastro nem área de login para
          visitantes. O ICC não coleta nome, e-mail, telefone nem outro dado
          pessoal por meio dele.
        </p>

        <h2>2. Dados técnicos de acesso</h2>
        <p>
          Como em qualquer site, os servidores que entregam as páginas, os
          dados e as imagens recebem informações técnicas da sua conexão, como
          o endereço IP, o tipo de navegador e o horário do acesso. Elas
          servem para o funcionamento e a segurança do site, e o ICC não as
          usa para identificar visitantes.
        </p>

        <h2>3. Serviços de terceiros</h2>
        <p>
          Para funcionar, o site usa serviços de terceiros que recebem o seu
          endereço IP quando você abre uma página: a Render (hospedagem do
          site e dos dados), o Cloudinary (armazenamento das imagens) e o
          Google Fonts (fonte de texto). Cada um segue a própria política de
          privacidade.
        </p>

        <h2>4. Cookies e rastreamento</h2>
        <p>
          Este site não usa cookies de rastreamento nem ferramentas de análise
          de terceiros. Não fazemos publicidade direcionada nem perfilamento
          de visitantes. O login da área administrativa, restrito a membros do
          ICC, usa um cookie de sessão.
        </p>

        <h2>5. Contato e processo seletivo</h2>
        <p>
          Para falar com o ICC, use o e-mail e as redes sociais da página de
          Contato. Tratamos o que você enviar apenas para responder à sua
          mensagem e, quando for o caso, dar seguimento a propostas de parceria
          ou a dúvidas sobre o processo seletivo, sem enviar comunicações que
          você não pediu e sem ceder os dados a terceiros para fins de
          marketing.
        </p>
        <p>
          As inscrições do processo seletivo são feitas em um formulário
          externo (Google Forms), aberto pelo link da página Processo
          Seletivo. Os dados informados nele são tratados pelo ICC para
          conduzir o processo e pelo Google, conforme a política de
          privacidade do Google.
        </p>
        <p>
          Os links para Instagram, LinkedIn e GitHub, e o botão de compartilhar
          artigos no LinkedIn, levam a sites de terceiros com políticas
          próprias. A conexão com eles só acontece quando você clica.
        </p>

        <h2>6. Por quanto tempo guardamos seus dados</h2>
        <p>
          Mantemos as mensagens recebidas e os dados do processo seletivo pelo
          tempo necessário para responder e conduzir o processo e, depois
          disso, por um período razoável, caso seja preciso retomar a conversa
          (por exemplo, uma parceria em andamento). Você pode pedir a exclusão
          a qualquer momento, como descrito abaixo.
        </p>

        <h2>7. Seus direitos</h2>
        <p>
          Você pode, a qualquer momento, pedir para: confirmar se temos dados
          seus, acessar esses dados, corrigir informações incompletas ou
          desatualizadas, ou solicitar a exclusão dos seus dados de nossos
          registros. Para exercer qualquer um desses direitos, entre em
          contato pelo e-mail abaixo.
        </p>

        <h2>8. Contato</h2>
        <p>
          Dúvidas sobre esta política ou sobre o tratamento dos seus dados
          podem ser enviadas para{" "}
          <a href={`mailto:${REDES.email}`}>{REDES.email}</a>.
        </p>
      </article>
      </section>
    </div>
  )
}
