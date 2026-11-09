import datetime

from django.db import migrations, models


def data_para_marcacao(apps, schema_editor):
    """Quem tinha data de saída passa a ficar desmarcado em "Exibir na equipe"."""
    Member = apps.get_model("website", "Member")
    Member.objects.exclude(exit_date__isnull=True).update(is_active=False)


def marcacao_para_data(apps, schema_editor):
    """Ao desfazer, quem está desmarcado recebe a data de hoje (a data original se perdeu)."""
    Member = apps.get_model("website", "Member")
    Member.objects.filter(is_active=False).update(exit_date=datetime.date.today())


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0025_remove_campos_sem_uso_e_padroniza_nomes"),
    ]

    operations = [
        migrations.AddField(
            model_name="member",
            name="is_active",
            field=models.BooleanField(
                default=True, verbose_name="Exibir na equipe",
                help_text="Desmarque quando a pessoa sair do clube: ela some da página Equipe, mas o perfil, "
                          "os projetos, os cases e a trajetória continuam guardados.",
            ),
        ),
        migrations.RunPython(data_para_marcacao, marcacao_para_data),
        migrations.RemoveField(model_name="member", name="exit_date"),
    ]
