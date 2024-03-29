# Generated by Django 4.1.1 on 2022-09-27 16:12

from django.db import migrations, models

from sigi.apps.contatos.models import UnidadeFederativa


def acerta_sudeste_fw(apps, schema_editor):
    UnidadeFederativa = apps.get_model("contatos", "UnidadeFederativa")
    UnidadeFederativa.objects.filter(regiao="SD").update(regiao="SE")


def acerta_sudeste_rw(apps, schema_editor):
    UnidadeFederativa = apps.get_model("contatos", "UnidadeFederativa")
    UnidadeFederativa.objects.filter(regiao="SE").update(regiao="SD")


class Migration(migrations.Migration):
    dependencies = [
        (
            "contatos",
            "0005_alter_mesorregiao_options_alter_microrregiao_options_and_more",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="unidadefederativa",
            name="regiao",
            field=models.CharField(
                choices=[
                    ("CO", "Centro-Oeste"),
                    ("NE", "Nordeste"),
                    ("NO", "Norte"),
                    ("SE", "Sudeste"),
                    ("SL", "Sul"),
                ],
                max_length=2,
                verbose_name="região",
            ),
        ),
        migrations.RunPython(acerta_sudeste_fw, acerta_sudeste_rw),
    ]
