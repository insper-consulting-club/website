from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import recurring_ical_events
from icalendar import Calendar

from django.core.management.base import BaseCommand

from website.models import CalendarMonth

TZ = ZoneInfo("America/Sao_Paulo")

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}


class Command(BaseCommand):
    help = (
        "Importa eventos de um arquivo .ics (exportado do Google Calendar) para o "
        "Calendário do Semestre (CalendarMonth). Eventos recorrentes são expandidos dentro "
        "do ano importado. Um mês do calendário é substituído por completo a cada "
        "importação (update_or_create por mês + ano, então importar anos diferentes "
        "não sobrescreve um ao outro)."
    )

    def add_arguments(self, parser):
        parser.add_argument("ics_path", type=str, help="Caminho do arquivo .ics")
        parser.add_argument(
            "--year",
            type=int,
            default=date.today().year,
            help="Ano a importar (default: ano atual)",
        )

    def handle(self, *args, **options):
        ics_path = Path(options["ics_path"])
        year = options["year"]

        if not ics_path.exists():
            self.stderr.write(self.style.ERROR(f"Arquivo não encontrado: {ics_path}"))
            return

        calendar = Calendar.from_ical(ics_path.read_bytes())
        # A janela de busca é alargada além do ano alvo porque um evento com
        # horário perto da virada UTC pode cair no ano/mês seguinte em UTC mas
        # no ano/mês anterior no horário de Brasília (e vice-versa); o filtro
        # por ano abaixo, já convertido para America/Sao_Paulo, corrige isso.
        occurrences = recurring_ical_events.of(calendar).between(
            (year - 1, 12, 28), (year + 1, 1, 4)
        )

        events_by_month = defaultdict(list)
        for occurrence in occurrences:
            summary = str(occurrence.get("summary", "")).strip()
            if not summary:
                continue
            start = occurrence["DTSTART"].dt
            if isinstance(start, datetime):
                start_date = start.astimezone(TZ).date()
            else:
                start_date = start
            if start_date.year != year:
                continue
            events_by_month[start_date.month].append((start_date, summary))

        if not events_by_month:
            self.stdout.write(self.style.WARNING(f"Nenhum evento encontrado em {year}."))
            return

        for month_num, events in sorted(events_by_month.items()):
            events.sort(key=lambda e: e[0])
            items = "\n".join(f"{d.strftime('%d/%m')} - {title}" for d, title in events)
            semester = "1" if month_num <= 6 else "2"
            month_name = MESES_PT[month_num]

            CalendarMonth.objects.update_or_create(
                month=month_name,
                year=year,
                defaults={"items": items, "semester": semester, "order": month_num},
            )
            self.stdout.write(self.style.SUCCESS(f"{month_name}: {len(events)} evento(s)"))

        # Um mês do mesmo ano que veio de uma importação anterior mas não tem
        # mais nenhum evento no arquivo atual (porque foram todos apagados na
        # fonte): esvazia em vez de manter o conteúdo antigo, senão a
        # reimportação vira só uma adição, contradizendo o texto de ajuda
        # acima ("substituído por completo a cada importação").
        meses_sem_evento_agora = CalendarMonth.objects.filter(year=year).exclude(
            order__in=events_by_month.keys()
        )
        for mes in meses_sem_evento_agora:
            if mes.items:
                mes.items = ""
                mes.save(update_fields=["items"])
                self.stdout.write(f"  {mes.month}: eventos removidos (não constam mais no arquivo)")
