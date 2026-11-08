import re

from django.db import migrations

SEMESTRE = re.compile(r'^\d{4}\.[12]$')


def copia_para_etapas(apps, schema_editor):
    """
    Passa a trajetória de cada membro, antes um texto JSON, para linhas da tabela
    MemberTrajectory. Entradas fora do formato (sem semestre no padrão AAAA.S ou
    sem cargo) são ignoradas, em vez de interromper a publicação do site.
    """
    Member = apps.get_model('website', 'Member')
    MemberTrajectory = apps.get_model('website', 'MemberTrajectory')

    for membro in Member.objects.exclude(trajetoria=[]):
        etapas = membro.trajetoria if isinstance(membro.trajetoria, list) else []
        for etapa in etapas:
            if not isinstance(etapa, dict):
                continue
            semestre = str(etapa.get('semestre', '')).strip()
            cargo = str(etapa.get('cargo', '')).strip()
            if SEMESTRE.match(semestre) and cargo:
                MemberTrajectory.objects.get_or_create(member=membro, semester=semestre, role=cargo[:200])


def volta_para_json(apps, schema_editor):
    Member = apps.get_model('website', 'Member')
    MemberTrajectory = apps.get_model('website', 'MemberTrajectory')

    for membro in Member.objects.filter(trajectory_steps__isnull=False).distinct():
        etapas = MemberTrajectory.objects.filter(member=membro).order_by('semester', 'id')
        membro.trajetoria = [{'semestre': e.semester, 'cargo': e.role} for e in etapas]
        membro.save(update_fields=['trajetoria'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0021_etapas_da_trajetoria_e_nomes'),
    ]

    operations = [
        migrations.RunPython(copia_para_etapas, volta_para_json),
    ]
