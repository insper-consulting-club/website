import json
from pathlib import Path

from django.core.management.base import BaseCommand

from website.site_texts import TEXTOS

CABECALHO = (
    "// Gerado por `python manage.py export_site_texts`. Não edite à mão: a fonte é\n"
    "// backend/website/site_texts.py. Estes são os textos de reserva, usados até a\n"
    "// API responder; o que vale, depois, é o que estiver no admin (Textos do site).\n"
)


def gera_arquivo_ts():
    linhas = [f"  {json.dumps(chave)}: {json.dumps(texto, ensure_ascii=False)}," for chave, _g, _d, texto in TEXTOS]
    corpo = "\n".join(linhas)
    return (
        f"{CABECALHO}export const TEXTOS_PADRAO = {{\n{corpo}\n}} as const\n\n"
        "export type ChaveTexto = keyof typeof TEXTOS_PADRAO\n"
    )


class Command(BaseCommand):
    help = "Gera o arquivo do frontend com os textos de reserva do catálogo (site_texts.py)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--saida",
            help="Caminho do arquivo a escrever. Sem ele, o conteúdo vai para a saída padrão.",
        )

    def handle(self, *args, **options):
        conteudo = gera_arquivo_ts()
        if options["saida"]:
            Path(options["saida"]).write_text(conteudo, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"Escrito em {options['saida']}"))
        else:
            self.stdout.write(conteudo, ending="")
