import sqlite3
from datetime import date
from pathlib import Path
from django.core.management.base import BaseCommand
from website.models import Member_Position, Team_Member

SQL_FILE = Path(__file__).parents[3] / "membros_icc.sql"

def _carregar_membros():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SQL_FILE.read_text(encoding="utf-8"))
    rows = conn.execute(
        "SELECT nome, data_entrada, foto, cargo_atual, descricao FROM membros"
    ).fetchall()
    conn.close()
    return [
        {
            "nome": r[0].strip(),
            "data_entrada": r[1],
            "foto": r[2],
            "cargo_atual": r[3].strip(),
            "descricao": r[4],
        }
        for r in rows
    ]

POWER_MAP = {
    "presidente": 0,
    "vice-presidente": 1,
    "diretor": 2,
    "diretora": 2,
    "diretoria": 2,
    "mentor": 3,
    "membro": 4,
    "trainee": 5,
}


def _power_for(cargo: str) -> int:
    cargo_lower = cargo.lower()
    for keyword, power in POWER_MAP.items():
        if keyword in cargo_lower:
            return power
    return 3


class Command(BaseCommand):
    help = "Importa os membros do ICC a partir dos dados do membros_icc.sql"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Remove todos os membros e cargos existentes antes de importar.",
        )

    def handle(self, *args, **options):
        if options["limpar"]:
            Team_Member.objects.all().delete()
            Member_Position.objects.all().delete()
            self.stdout.write("Membros e cargos removidos.")

        membros = _carregar_membros()

        self.stdout.write("Criando cargos...")
        cargos_unicos = {m["cargo_atual"] for m in membros}
        posicoes = {}
        for cargo in cargos_unicos:
            pos, created = Member_Position.objects.get_or_create(
                title=cargo,
                defaults={"power": _power_for(cargo)},
            )
            posicoes[cargo] = pos
            status = "criado" if created else "já existia"
            self.stdout.write(f"  '{cargo}' ({status})")

        self.stdout.write("Importando membros...")
        criados = 0
        ignorados = 0
        for m in membros:
            ano, mes, dia = m["data_entrada"].split("-")
            _, created = Team_Member.objects.get_or_create(
                name=m["nome"],
                defaults={
                    # "foto" no SQL legado é um link do Google Drive, que não
                    # é mais utilizável diretamente (rate limit / 429). As
                    # fotos agora são enviadas manualmente pelo admin Django.
                    "biography": m["descricao"],
                    "position": posicoes[m["cargo_atual"]],
                    "entry_date": date(int(ano), int(mes), int(dia)),
                    "hours": None,
                },
            )
            if created:
                criados += 1
                self.stdout.write(f"  + {m['nome']}")
            else:
                ignorados += 1
                self.stdout.write(f"  ~ {m['nome']} (já existia, ignorado)")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nConcluído: {criados} criados, {ignorados} ignorados."
            )
        )
