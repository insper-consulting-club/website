from django.db import migrations

# Texto que a página Política de Privacidade tinha no código. Daqui em diante
# ele é editado no admin; esta cópia só alimenta o primeiro registro.
POLITICA = """\
Esta política explica como o site do Insper Consulting Club (ICC) trata os dados pessoais de quem o visita, em conformidade com a Lei Geral de Proteção de Dados (Lei nº 13.709/2018).

## 1. Quais dados coletamos

O site não tem formulários, cadastro nem área de login para visitantes. O ICC não coleta nome, e-mail, telefone nem outro dado pessoal por meio dele.

## 2. Dados técnicos de acesso

Como em qualquer site, os servidores que entregam as páginas, os dados e as imagens recebem informações técnicas da sua conexão, como o endereço IP, o tipo de navegador e o horário do acesso. Elas servem para o funcionamento e a segurança do site, e o ICC não as usa para identificar visitantes.

## 3. Serviços de terceiros

Para funcionar, o site usa serviços de terceiros que recebem o seu endereço IP quando você abre uma página: a Render (hospedagem do site e dos dados), o Cloudinary (armazenamento das imagens) e o Google Fonts (fonte de texto). Cada um segue a própria política de privacidade.

## 4. Cookies e rastreamento

Este site não usa cookies de rastreamento nem ferramentas de análise de terceiros. Não fazemos publicidade direcionada nem perfilamento de visitantes. O login da área administrativa, restrito a membros do ICC, usa um cookie de sessão.

## 5. Contato e processo seletivo

Para falar com o ICC, use o e-mail e as redes sociais da página de Contato. Tratamos o que você enviar apenas para responder à sua mensagem e, quando for o caso, dar seguimento a propostas de parceria ou a dúvidas sobre o processo seletivo, sem enviar comunicações que você não pediu e sem ceder os dados a terceiros para fins de marketing.

As inscrições do processo seletivo são feitas em um formulário externo (Google Forms), aberto pelo link da página Processo Seletivo. Os dados informados nele são tratados pelo ICC para conduzir o processo e pelo Google, conforme a política de privacidade do Google.

Os links para Instagram, LinkedIn e GitHub, e o botão de compartilhar artigos no LinkedIn, levam a sites de terceiros com políticas próprias. A conexão com eles só acontece quando você clica.

## 6. Por quanto tempo guardamos seus dados

Mantemos as mensagens recebidas e os dados do processo seletivo pelo tempo necessário para responder e conduzir o processo e, depois disso, por um período razoável, caso seja preciso retomar a conversa (por exemplo, uma parceria em andamento). Você pode pedir a exclusão a qualquer momento, como descrito abaixo.

## 7. Seus direitos

Você pode, a qualquer momento, pedir para: confirmar se temos dados seus, acessar esses dados, corrigir informações incompletas ou desatualizadas, ou solicitar a exclusão dos seus dados de nossos registros. Para exercer qualquer um desses direitos, entre em contato pelo e-mail abaixo.

## 8. Contato

Dúvidas sobre esta política ou sobre o tratamento dos seus dados podem ser enviadas para [insperconsultingclub@gmail.com](mailto:insperconsultingclub@gmail.com).
"""

BENEFICIOS = [
    (
        'Acesso a talentos',
        'Contato direto com alunos de alta performance, treinados em resolução de cases e raciocínio analítico.',
    ),
    (
        'Visibilidade Institucional',
        'Presença em eventos, capacitações e redes sociais com crescimento consistente de alcance e engajamento.',
    ),
    (
        'Cases aplicados à realidade',
        'Possibilidade de propor desafios reais de negócio para serem resolvidos pelos nossos grupos de '
        'trainees e do Pedagógico.',
    ),
]


def cria_dados_iniciais(apps, schema_editor):
    SiteConfig = apps.get_model('website', 'SiteConfig')
    PartnerBenefit = apps.get_model('website', 'PartnerBenefit')

    # Os demais campos usam os valores padrão do model, que são os textos
    # que o site já exibia.
    config, _ = SiteConfig.objects.get_or_create(pk=1, defaults={'privacy_text': POLITICA})
    if not config.privacy_text:
        config.privacy_text = POLITICA
        config.save(update_fields=['privacy_text'])

    if not PartnerBenefit.objects.filter(site_config=config).exists():
        for ordem, (titulo, descricao) in enumerate(BENEFICIOS, start=1):
            PartnerBenefit.objects.create(
                site_config=config, title=titulo, description=descricao, order=ordem
            )


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0013_configuracao_do_site'),
    ]

    operations = [
        # Sem volta: os registros criados aqui são apagados junto com as
        # tabelas se a 0013 for desfeita.
        migrations.RunPython(cria_dados_iniciais, migrations.RunPython.noop),
    ]
