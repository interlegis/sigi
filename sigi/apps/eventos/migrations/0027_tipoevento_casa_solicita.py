# Generated by Django 4.1 on 2022-08-08 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eventos", "0026_preenche_turma"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipoevento",
            name="casa_solicita",
            field=models.BooleanField(
                default=False, verbose_name="casa pode solicitar"
            ),
        ),
    ]