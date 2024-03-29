# Generated by Django 4.1 on 2022-08-28 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("ocorrencias", "0011_alter_categoria_tipo"),
        ("eventos", "0027_tipoevento_casa_solicita"),
    ]

    operations = [
        migrations.AddField(
            model_name="evento",
            name="solicitacao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ocorrencias.ocorrencia",
                verbose_name="Solicitação de origem",
            ),
        ),
    ]
