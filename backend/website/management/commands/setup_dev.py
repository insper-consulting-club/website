import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from website.models import Member


class Command(BaseCommand):
    help = (
        "Prepara o ambiente local: cria o administrador 'admin' (senha 'admin') "
        "quando não há usuários e carrega os dados de exemplo quando não há "
        "membros. Só roda com DEBUG=True e pode ser repetido."
    )

    def handle(self, *args, **options):
        # Senha conhecida: este comando nunca pode rodar em produção.
        if not settings.DEBUG:
            raise CommandError("setup_dev só roda em ambiente local (DEBUG=True).")
        # Com DATABASE_URL o Django usa um banco externo (por exemplo, o de
        # produção), onde um administrador de senha conhecida seria um risco.
        if os.environ.get("DATABASE_URL"):
            raise CommandError("setup_dev não roda com DATABASE_URL definida: o banco não é o local.")

        User = get_user_model()
        if not User.objects.exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write(self.style.SUCCESS("Administrador local criado: admin / admin."))

        if not Member.objects.exists():
            call_command("seed_mock_data", stdout=self.stdout)
