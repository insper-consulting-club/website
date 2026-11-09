from django.db import migrations, models

# Campo da Configuração do site -> chave do texto (website/conteudo/), com o tamanho máximo que o campo tinha.
# A lista é cópia fixa de propósito: uma migration não pode depender de um registro que continua mudando.
CAMPOS = (
    ('home_hero_title', 'home.hero_titulo', 200),
    ('home_statement', 'home.hero_frase', 300),
    ('home_about_title', 'home.sobre_titulo', 200),
    ('home_about_title_highlight', 'home.sobre_titulo_destaque', 200),
    ('home_about_text', 'home.sobre_texto', None),
    ('mission', 'home.missao_texto', None),
    ('mission_how', 'home.missao_como_texto', None),
    ('mission_goal', 'home.missao_meta_texto', None),
    ('home_cta_title', 'home.cta_titulo', 200),
    ('footer_tagline', 'rodape.frase', 300),
    ('team_lead', 'equipe.abertura', 300),
    ('partners_lead', 'parceiros.abertura', 300),
    ('partners_benefits_title', 'parceiros.beneficios_titulo', 200),
    ('projects_lead', 'projetos.abertura', 300),
    ('articles_lead', 'artigos.abertura', 300),
    ('contact_lead', 'contato.abertura', 300),
    ('process_lead', 'processo.abertura', 300),
    ('process_closed_message', 'processo.inscricoes_encerradas', 300),
)


def para_os_textos(apps, schema_editor):
    """Leva o que está nos campos da Configuração do site para os textos, sem perder o que o ICC editou."""
    SiteConfig = apps.get_model('website', 'SiteConfig')
    SiteText = apps.get_model('website', 'SiteText')
    config = SiteConfig.objects.filter(pk=1).first()
    if config is None:
        return  # banco sem configuração: os textos nascem com o valor original
    for campo, chave, _limite in CAMPOS:
        # Grupo, descrição e ordem são acertados pela sincronização que roda depois da migração.
        SiteText.objects.update_or_create(key=chave, defaults={'value': getattr(config, campo)})


def de_volta_aos_campos(apps, schema_editor):
    """Desfaz: devolve os textos aos campos e apaga as linhas que eles tinham em SiteText."""
    SiteConfig = apps.get_model('website', 'SiteConfig')
    SiteText = apps.get_model('website', 'SiteText')
    config = SiteConfig.objects.filter(pk=1).first()
    valores = dict(SiteText.objects.filter(key__in=[c[1] for c in CAMPOS]).values_list('key', 'value'))
    if config is not None:
        for campo, chave, limite in CAMPOS:
            if chave in valores:
                # O campo antigo tinha um limite de tamanho; o texto novo não.
                setattr(config, campo, valores[chave][:limite] if limite else valores[chave])
        config.save()
    SiteText.objects.filter(key__in=valores).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0029_paginas_de_textos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitetext',
            name='value',
            field=models.TextField(
                help_text='Mantenha os trechos entre chaves, como {n} ou {data}: o site os preenche.',
                verbose_name='Texto',
            ),
        ),
        migrations.RunPython(para_os_textos, de_volta_aos_campos),
    ] + [
        migrations.RemoveField(model_name='siteconfig', name=campo) for campo, _chave, _limite in CAMPOS
    ]
