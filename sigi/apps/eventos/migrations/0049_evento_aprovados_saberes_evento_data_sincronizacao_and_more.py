# Generated by Django 4.2.4 on 2023-10-02 11:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0048_evento_set_defaults"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="aprovados_saberes",
            field=models.PositiveIntegerField(
                default=0,
                editable=False,
                help_text="Número de pessoas que concluíram o curso no Saberes. Computado via integração SIGI x Saberes.",
                verbose_name="aprovados no Saberes",
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="data_sincronizacao",
            field=models.DateTimeField(
                editable=False,
                null=True,
                verbose_name="data da última sincronização com Saberes",
            ),
        ),
        migrations.AddField(
            model_name="evento",
            name="inscritos_saberes",
            field=models.PositiveIntegerField(
                default=0,
                editable=False,
                help_text="Número de pessoas que se inscreveram no evento no Saberes. Computado via integração SIGI x Saberes.",
                verbose_name="inscritos no Saberes",
            ),
        ),
        migrations.AlterField(
            model_name="evento",
            name="total_participantes",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Se informar quantidade de participantes na aba de convites, este campo será ajustado com a somatória dos participantes naquela aba. Senão, será igual ao número de inscritos no Saberes.",
                verbose_name="total de participantes",
            ),
        ),
    ]
