from django.apps import AppConfig
from django.db.models.signals import post_migrate


def sincroniza_textos_do_site(sender, apps, **kwargs):
    # Depois de cada migrate, cria os textos novos do catálogo. Usa o estado das
    # migrations: se a tabela ainda não existe (migrando para trás), não faz nada.
    from .site_texts import sincroniza_textos
    try:
        SiteText = apps.get_model('website', 'SiteText')
    except LookupError:
        return
    sincroniza_textos(SiteText)


class WebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'website'

    def ready(self):
        post_migrate.connect(sincroniza_textos_do_site, sender=self)
