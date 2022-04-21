# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("servicos", "0002_tiposervico_modo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servico",
            name="contato_administrativo",
            field=models.ForeignKey(
                related_name="contato_administrativo",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Contato administrativo",
                to="casas.Funcionario",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="servico",
            name="contato_tecnico",
            field=models.ForeignKey(
                related_name="contato_tecnico",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Contato t\xe9cnico",
                to="casas.Funcionario",
            ),
            preserve_default=True,
        ),
    ]
