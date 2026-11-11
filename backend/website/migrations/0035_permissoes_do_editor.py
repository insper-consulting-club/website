from django.db import migrations

# O que o grupo Editores ganha (as permissões padrão de um grupo novo estão em website/editors_group.py):
# as listas Trajetória e Autores, que faltavam; apagar membro e artigo (o admin só deixa apagar o que não tem
# histórico); alterar cargos; os benefícios para parceiros; e ver a atividade recente.
NOVAS = [
    ("website", f"{acao}_{modelo}")
    for modelo in ("membertrajectory", "articleauthor", "partnerbenefit")
    for acao in ("add", "change", "delete", "view")
] + [
    ("website", "delete_member"),
    ("website", "delete_article"),
    ("website", "change_position"),
    ("admin", "view_logentry"),
]


def permitir_aos_editores(apps, schema_editor):
    """O grupo Editores já existe em produção e só é criado uma vez: acrescenta, uma única vez, as permissões novas.

    Os ajustes que alguém fizer depois, em Acesso > Grupos, ficam: esta migration não roda de novo. Num banco novo o
    grupo ainda não existe (ele nasce depois do migrate, com todas as permissões), então não há nada a fazer."""
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    grupo = Group.objects.filter(name="Editores").first()
    if grupo is None:
        return
    for app_label, codename in NOVAS:
        permissao = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
        if permissao is not None:
            grupo.permissions.add(permissao)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0034_remove_artigo_institucional'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.RunPython(permitir_aos_editores, migrations.RunPython.noop),
    ]
