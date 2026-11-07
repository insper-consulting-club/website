import re
import sqlite3
from pathlib import Path

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from website.models import Team_Member

SQL_FILE = Path(__file__).parents[3] / "membros_icc.sql"

# Extensão genérica para imagens sem Content-Type confiável
_DEFAULT_EXT = "jpg"

# Domínios do Google que servem thumbnails de Drive
_DRIVE_THUMBNAIL_URL = "https://drive.google.com/thumbnail?id={id}&sz=w800"


def _extract_drive_id(url: str) -> str | None:
    match = re.search(r"[?&/]id=([\w-]+)", url) or re.search(r"/d/([\w-]+)", url)
    return match.group(1) if match else None


def _download_image(drive_id: str) -> tuple[bytes, str] | None:
    """Baixa imagem do Drive via thumbnail URL. Retorna (bytes, extensão) ou None."""
    url = _DRIVE_THUMBNAIL_URL.format(id=drive_id)
    try:
        resp = requests.get(url, timeout=15, allow_redirects=True)
        resp.raise_for_status()
    except requests.RequestException:
        return None

    content_type = resp.headers.get("Content-Type", "")
    ext = content_type.split("/")[-1].split(";")[0].strip() or _DEFAULT_EXT
    if ext == "jpeg":
        ext = "jpg"
    return resp.content, ext


def _load_sql_foto_map() -> dict[str, str]:
    """Lê membros_icc.sql e retorna {nome: drive_url}."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(SQL_FILE.read_text(encoding="utf-8"))
    rows = conn.execute("SELECT nome, foto FROM membros").fetchall()
    conn.close()
    return {r[0].strip(): r[1] for r in rows if r[1]}


class Command(BaseCommand):
    help = "Baixa fotos dos membros do Google Drive e salva no Cloudinary"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sobrescrever",
            action="store_true",
            help="Sobrescreve fotos de membros que já têm imagem cadastrada.",
        )

    def handle(self, *args, **options):
        foto_map = _load_sql_foto_map()
        members = Team_Member.objects.all()

        ok = erros = pulados = 0

        for member in members:
            if member.photo and not options["sobrescrever"]:
                pulados += 1
                self.stdout.write(f"  ~ {member.name} (já tem foto, use --sobrescrever para atualizar)")
                continue

            drive_url = foto_map.get(member.name)
            if not drive_url:
                erros += 1
                self.stdout.write(self.style.WARNING(f"  ! {member.name} — sem URL no SQL"))
                continue

            drive_id = _extract_drive_id(drive_url)
            if not drive_id:
                erros += 1
                self.stdout.write(self.style.WARNING(f"  ! {member.name} — ID do Drive não reconhecido ({drive_url})"))
                continue

            result = _download_image(drive_id)
            if not result:
                erros += 1
                self.stdout.write(self.style.WARNING(f"  ! {member.name} — falha ao baixar imagem"))
                continue

            data, ext = result
            filename = f"{member.id}_{member.name.lower().replace(' ', '_')}.{ext}"
            member.photo.save(filename, ContentFile(data), save=True)
            ok += 1
            self.stdout.write(self.style.SUCCESS(f"  + {member.name}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"\nConcluído: {ok} enviadas, {pulados} puladas, {erros} com erro."
            )
        )
