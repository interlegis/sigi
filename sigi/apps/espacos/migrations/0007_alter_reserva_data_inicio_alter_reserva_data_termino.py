# Generated by Django 4.2.7 on 2024-03-12 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("espacos", "0006_separa_hora_da_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reserva",
            name="data_inicio",
            field=models.DateField(verbose_name="data início"),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="data_termino",
            field=models.DateField(verbose_name="data término"),
        ),
    ]
