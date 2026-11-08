from django.apps import AppConfig
from django.apps import apps as apps_globais
from django.db.models.signals import post_migrate


def sincroniza_textos_do_site(sender, apps=None, **kwargs):
    # Depois de cada migrate, cria os textos novos do catálogo. Usa o estado das
    # migrations: se a tabela ainda não existe (migrando para trás), não faz nada.
    # O comando flush envia este sinal sem "apps"; nesse caso valem os modelos atuais.
    from .site_texts import sincroniza_textos
    apps = apps or apps_globais
    try:
        SiteText = apps.get_model('website', 'SiteText')
    except LookupError:
        return
    sincroniza_textos(SiteText)


def cria_grupo_editores(sender, apps=None, **kwargs):
    # Cria o grupo "Editores" na primeira vez; depois não mexe mais (ver editors_group.py).
    from .editors_group import sincroniza_grupo_editores
    apps = apps or apps_globais
    try:
        apps.get_model('auth', 'Group')
        apps.get_model('website', 'Article')
    except LookupError:
        return
    sincroniza_grupo_editores(apps, sender)


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'
    # Nome do grupo de modelos na página inicial do /admin.
    verbose_name = 'Conteúdo do site'

    def ready(self):
        post_migrate.connect(sincroniza_textos_do_site, sender=self)
        post_migrate.connect(cria_grupo_editores, sender=self)
