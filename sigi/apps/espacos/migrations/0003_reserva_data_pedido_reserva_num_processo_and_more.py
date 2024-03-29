# Generated by Django 4.2.4 on 2023-11-28 18:45

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("espacos", "0002_converte_eventos"),
    ]

    operations = [
        migrations.AddField(
            model_name="reserva",
            name="data_pedido",
            field=models.DateField(
                blank=True, null=True, verbose_name="data do pedido"
            ),
        ),
        migrations.AddField(
            model_name="reserva",
            name="num_processo",
            field=models.CharField(
                blank=True,
                help_text="Formato:<em>XXXXX.XXXXXX/XXXX-XX</em>",
                max_length=20,
                verbose_name="número do processo SIGAD",
            ),
        ),
        migrations.AddField(
            model_name="reserva",
            name="total_participantes",
            field=models.PositiveIntegerField(
                default=0, verbose_name="total de participantes"
            ),
        ),
        migrations.AddField(
            model_name="reserva",
            name="virtual",
            field=models.BooleanField(default=False, verbose_name="virtual"),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="inicio",
            field=models.DateTimeField(verbose_name="data/hora de início"),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="solicitante",
            field=models.CharField(
                help_text="indique o nome do Senador, autoridade, pessoa ou setor solicitante da reserva",
                max_length=100,
                verbose_name="senador/autoridade solicitante",
            ),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="status",
            field=models.CharField(
                choices=[("A", "Ativo"), ("C", "Cancelado")],
                default="A",
                editable=False,
                max_length=1,
                verbose_name="status",
            ),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="termino",
            field=models.DateTimeField(verbose_name="data/hora de término"),
        ),
    ]
