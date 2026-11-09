import json
from pathlib import Path

from django.core.management.base import BaseCommand

from website.conteudo_padrao import BENEFICIOS_PADRAO, NAV_ITEMS_PADRAO
from website.models import NavItem, SiteConfig

CABECALHO = (
    "// Gerado por `python manage.py export_site_config_padrao`. Não edite à mão: a fonte são os valores\n"
    "// padrão dos campos de SiteConfig (backend/website/models.py) e backend/website/conteudo_padrao.py.\n"
    "//\n"
    "// Reserva usada enquanto a Configuração do site não chega da API, ou quando a chamada falha: o\n"
    "// site continua com contatos e textos válidos. O que vale, depois, é o que estiver no admin. O texto\n"
    "// da Política de Privacidade fica de fora de propósito: é longo, e a página avisa quando não o recebe.\n"
)

# Campos de imagem: o frontend recebe só o endereço (<nome>_url), que na reserva é nulo.
CAMPOS_DE_IMAGEM = {"logo", "favicon", "og_image", "home_about_photo"}


def _valor(v):
    return json.dumps(v, ensure_ascii=False)


def _objeto(dados):
    return "{ " + ", ".join(f"{chave}: {_valor(valor)}" for chave, valor in dados.items()) + " }"


def gera_arquivo_ts():
    linhas = []
    for campo in SiteConfig._meta.concrete_fields:
        if campo.primary_key:
            continue
        if campo.name in CAMPOS_DE_IMAGEM:
            linhas.append(f"  {campo.name}_url: null,")
        elif campo.name == "privacy_text":
            linhas.append('  privacy_text: "",')
        else:
            padrao = campo.get_default()
            linhas.append(f"  {campo.name}: {_valor(padrao)},")

    itens = [
        {
            "id": indice, "label": texto, "area": area, "page": pagina,
            "path": NavItem.PAGINAS[pagina], "external": False, "order": ordem,
        }
        for indice, (texto, area, pagina, ordem) in enumerate(NAV_ITEMS_PADRAO)
    ]
    beneficios = [
        {"id": indice, "title": titulo, "description": descricao, "order": ordem}
        for indice, (titulo, descricao, ordem) in enumerate(BENEFICIOS_PADRAO)
    ]
    linhas.append("  texts: TEXTOS_PADRAO,")
    linhas.append("  nav_items: [")
    linhas.extend(f"    {_objeto(item)}," for item in itens)
    linhas.append("  ],")
    linhas.append("  partner_benefits: [")
    linhas.extend(f"    {_objeto(item)}," for item in beneficios)
    linhas.append("  ],")

    corpo = "\n".join(linhas)
    return (
        f"{CABECALHO}"
        'import { TEXTOS_PADRAO } from "./textosPadrao"\n'
        'import type { SiteConfig } from "./types"\n\n'
        f"export const SITE_CONFIG_PADRAO: SiteConfig = {{\n{corpo}\n}}\n"
    )


class Command(BaseCommand):
    help = "Gera o arquivo de reserva da Configuração do site para o frontend (siteConfigPadrao.ts)."

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
