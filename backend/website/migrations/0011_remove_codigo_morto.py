from django.db import migrations


class Migration(migrations.Migration):
    """
    Remove models e campos que nenhuma parte do site usa mais: calendário,
    pedidos de contato, inscrições de participantes, imagens e blocos de
    conteúdo das atividades, o parceiro responsável por uma atividade e o
    campo "contato" do parceiro.
    """

    dependencies = [
        ('website', '0010_renomeia_para_vocabulario_do_icc'),
    ]

    operations = [
        migrations.DeleteModel(name='ActivityImage'),
        migrations.DeleteModel(name='ActivityContentBlock'),
        migrations.DeleteModel(name='CalendarMonth'),
        migrations.DeleteModel(name='Contact'),
        migrations.DeleteModel(name='Participant'),
        migrations.RemoveField(model_name='programcomponent', name='responsible_partner'),
        migrations.RemoveField(model_name='partner', name='contato'),
    ]
