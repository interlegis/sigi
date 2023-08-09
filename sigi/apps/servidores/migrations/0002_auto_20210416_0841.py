# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("servidores", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servico",
            name="responsavel",
            field=models.ForeignKey(
                related_name="chefe",
                on_delete=django.db.models.deletion.SET_NULL,
                to="servidores.Servidor",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="servidor",
            name="servico",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="servidores.Servico",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="subsecretaria",
            name="responsavel",
            field=models.ForeignKey(
                related_name="diretor",
                on_delete=django.db.models.deletion.SET_NULL,
                to="servidores.Servidor",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
