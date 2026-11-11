from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0033_ajuda_do_markdown'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='institutional',
        ),
    ]
