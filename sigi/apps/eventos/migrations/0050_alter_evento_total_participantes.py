# Generated by Django 4.2.4 on 2023-10-03 12:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "eventos",
            "0049_evento_aprovados_saberes_evento_data_sincronizacao_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="evento",
            name="total_participantes",
            field=models.PositiveIntegerField(
                default=0,
                help_text="Se existe evento relacionado no saberes, mostra o número de participantes aprovados naquela plataforma. Senão, mostra a somatória de participantes das Casas convidadas ou o número de participantes informado manualmente pelo usuário.",
                verbose_name="total de participantes/aprovados",
            ),
        ),
    ]
