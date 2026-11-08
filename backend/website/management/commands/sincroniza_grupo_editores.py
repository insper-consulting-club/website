from django.apps import apps
from django.core.management.base import BaseCommand

from website.editors_group import NOME, sincroniza_grupo_editores


class Command(BaseCommand):
    help = f'Restaura o grupo "{NOME}" às permissões padrão (descarta ajustes feitos no admin).'

    def handle(self, *args, **options):
        sincroniza_grupo_editores(apps, apps.get_app_config("website"), redefinir=True)
        self.stdout.write(self.style.SUCCESS(f'Grupo "{NOME}" restaurado ao padrão.'))
