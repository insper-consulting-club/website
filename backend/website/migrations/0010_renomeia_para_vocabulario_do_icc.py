from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Alinha os nomes dos models ao vocabulário do ICC: programa, componente,
    case, artigo e membro. Só renomeia (RenameModel e RenameField), então os
    dados são preservados. O app continua se chamando "website".
    """

    dependencies = [
        ('website', '0009_media_slug'),
    ]

    operations = [
        # Models
        migrations.RenameModel(old_name='Media', new_name='Article'),
        migrations.RenameModel(old_name='SuccessCaseParticipant', new_name='ProgramCaseParticipant'),
        migrations.RenameModel(old_name='SuccessCase', new_name='ProgramCase'),
        migrations.RenameModel(old_name='Activity', new_name='ProgramComponent'),
        migrations.RenameModel(old_name='ActivityCategory', new_name='Program'),
        migrations.RenameModel(old_name='Team_Member', new_name='Member'),
        migrations.RenameModel(old_name='Member_Position', new_name='Position'),
        migrations.RenameModel(old_name='Partner_Category', new_name='PartnerCategory'),

        # Campo "category" vira "program" em projetos, componentes e cases
        migrations.RenameField(model_name='project', old_name='category', new_name='program'),
        migrations.RenameField(model_name='programcomponent', old_name='category', new_name='program'),
        migrations.RenameField(model_name='programcase', old_name='category', new_name='program'),

        # Nomes das relações reversas e textos exibidos no admin
        migrations.AlterField(
            model_name='project',
            name='program',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='projects', to='website.program', verbose_name='Programa',
            ),
        ),
        migrations.AlterField(
            model_name='programcomponent',
            name='program',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='components', to='website.program', verbose_name='Programa',
            ),
        ),
        migrations.AlterField(
            model_name='programcase',
            name='program',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='cases', to='website.program', verbose_name='Programa',
            ),
        ),
        migrations.AlterField(
            model_name='programcaseparticipant',
            name='member',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='program_cases', to='website.member', verbose_name='Membro',
            ),
        ),
        migrations.AlterField(
            model_name='program',
            name='badge',
            field=models.CharField(
                blank=True, max_length=50, verbose_name='Frequência (badge)',
                help_text='Opcional. Deixe vazio quando o programa não tiver uma periodicidade definida.',
            ),
        ),
        migrations.AlterModelOptions(
            name='program',
            options={'ordering': ['order'], 'verbose_name': 'Programa', 'verbose_name_plural': 'Programas'},
        ),
        migrations.AlterModelOptions(
            name='programcomponent',
            options={'verbose_name': 'Componente do programa', 'verbose_name_plural': 'Componentes dos programas'},
        ),
        migrations.AlterModelOptions(
            name='programcase',
            options={
                'ordering': ['-semester', 'order'],
                'verbose_name': 'Case do programa',
                'verbose_name_plural': 'Cases dos programas',
            },
        ),
    ]
