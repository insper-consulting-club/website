from django.db import migrations

# (texto, área, página, ordem). Reproduz o que o menu, o rodapé e o botão do
# topo tinham no código, para o site continuar igual depois da migração.
ITENS = [
    ('Nossa Equipe', 'menu', 'equipe', 1),
    ('Parceiros', 'menu', 'parceiros', 2),
    ('Projetos', 'menu', 'projetos', 3),
    ('Artigos', 'menu', 'artigos', 4),
    ('Seja membro', 'rodape', 'processo', 5),
    ('Contato', 'menu', 'contato', 6),
    ('Seja membro', 'botao', 'processo', 7),
]


def cria_itens(apps, schema_editor):
    SiteConfig = apps.get_model('website', 'SiteConfig')
    NavItem = apps.get_model('website', 'NavItem')

    config, _ = SiteConfig.objects.get_or_create(pk=1)
    if NavItem.objects.filter(site_config=config).exists():
        return
    for texto, area, pagina, ordem in ITENS:
        NavItem.objects.create(site_config=config, label=texto, area=area, page=pagina, order=ordem)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0017_itens_de_navegacao'),
    ]

    operations = [
        migrations.RunPython(cria_itens, migrations.RunPython.noop),
    ]
