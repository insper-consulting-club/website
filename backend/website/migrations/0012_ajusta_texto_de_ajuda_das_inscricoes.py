from django.db import migrations, models


class Migration(migrations.Migration):
    """Só reescreve o texto de ajuda de "Inscrições abertas" no admin."""

    dependencies = [
        ('website', '0011_remove_codigo_morto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selectionprocess',
            name='registrations_open',
            field=models.BooleanField(
                default=False, verbose_name='Inscrições abertas',
                help_text='Marque quando o PS abrir. Desmarcado, o site mostra "inscrições encerradas" e o link do formulário fica escondido.',
            ),
        ),
    ]
