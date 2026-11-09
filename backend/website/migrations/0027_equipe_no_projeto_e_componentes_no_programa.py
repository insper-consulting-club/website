from django.db import migrations, models
import django.db.models.deletion


def copiar_equipes_para_o_projeto(apps, schema_editor):
    """Copia quem participou de cada projeto, do lado do membro para o lado do projeto."""
    Antiga = apps.get_model("website", "Member").projects.through
    Nova = apps.get_model("website", "Project").equipe_tmp.through
    Nova.objects.bulk_create(
        [Nova(project_id=ligacao.project_id, member_id=ligacao.member_id) for ligacao in Antiga.objects.all()],
        ignore_conflicts=True,
    )


def copiar_equipes_para_o_membro(apps, schema_editor):
    """Caminho de volta: do projeto para o membro."""
    Antiga = apps.get_model("website", "Member").projects.through
    Nova = apps.get_model("website", "Project").equipe_tmp.through
    Antiga.objects.bulk_create(
        [Antiga(project_id=ligacao.project_id, member_id=ligacao.member_id) for ligacao in Nova.objects.all()],
        ignore_conflicts=True,
    )


def apagar_componentes_sem_programa(apps, schema_editor):
    """Componente sem programa não aparecia em página nenhuma. Passa a ser obrigatório ter programa."""
    apps.get_model("website", "ProgramComponent").objects.filter(program__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("website", "0026_membro_ativo"),
    ]

    operations = [
        # Imagem do artigo: o número pode ficar vazio (é preenchido sozinho).
        migrations.AlterField(
            model_name="articleimage",
            name="number",
            field=models.PositiveIntegerField(
                blank=True, verbose_name="Número",
                help_text="Deixe vazio para numerar sozinho. No texto, escreva ![](imagem-1) para a imagem de número 1.",
            ),
        ),
        # Equipe do projeto: a relação passa a ser definida no projeto, e não no membro.
        migrations.AddField(
            model_name="project",
            name="equipe_tmp",
            field=models.ManyToManyField(blank=True, related_name="+", to="website.member"),
        ),
        migrations.RunPython(copiar_equipes_para_o_projeto, copiar_equipes_para_o_membro),
        migrations.RemoveField(model_name="member", name="projects"),
        migrations.RenameField(model_name="project", old_name="equipe_tmp", new_name="members"),
        migrations.AlterField(
            model_name="project",
            name="members",
            field=models.ManyToManyField(
                blank=True, related_name="projects", to="website.member", verbose_name="Equipe",
                help_text="Membros que participaram do projeto. Aparecem na página do projeto e no perfil de cada pessoa.",
            ),
        ),
        # Componentes do programa: sempre ligados a um programa, e em ordem fixa.
        migrations.RunPython(apagar_componentes_sem_programa, migrations.RunPython.noop),
        migrations.AlterModelOptions(
            name="programcomponent",
            options={"ordering": ["id"], "verbose_name": "Componente do programa", "verbose_name_plural": "Componentes dos programas"},
        ),
        migrations.AlterField(
            model_name="programcomponent",
            name="program",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="components", to="website.program",
                verbose_name="Programa",
            ),
        ),
        # Programa em destaque: agora é escolhido numa lista.
        migrations.AlterField(
            model_name="siteconfig",
            name="featured_program_slug",
            field=models.CharField(
                blank=True, default="jornada-do-consultor", max_length=50, verbose_name="Programa dos cases em destaque",
                help_text='Programa para onde o botão "Ver os cases" da página Projetos leva. Deixe vazio para esconder a seção.',
            ),
        ),
    ]
