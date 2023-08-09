# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("contatos", "0002_auto_20151104_0810"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contato",
            name="municipio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="munic\xedpio",
                blank=True,
                to="contatos.Municipio",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="endereco",
            name="municipio",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="munic\xedpio",
                blank=True,
                to="contatos.Municipio",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="municipio",
            name="microrregiao",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Microrregi\xe3o",
                blank=True,
                to="contatos.Microrregiao",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="municipio",
            name="uf",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="UF",
                to="contatos.UnidadeFederativa",
            ),
            preserve_default=True,
        ),
    ]
