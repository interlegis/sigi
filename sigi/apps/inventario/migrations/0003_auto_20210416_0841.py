# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0002_auto_20210406_1945"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bem",
            name="fornecedor",
            field=models.ForeignKey(
                to="inventario.Fornecedor",
                on_delete=django.db.models.deletion.PROTECT,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="equipamento",
            name="fabricante",
            field=models.ForeignKey(
                to="inventario.Fabricante",
                on_delete=django.db.models.deletion.PROTECT,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="equipamento",
            name="modelo",
            field=models.ForeignKey(
                to="inventario.ModeloEquipamento",
                on_delete=django.db.models.deletion.PROTECT,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="modeloequipamento",
            name="tipo",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="tipo de equipamento",
                to="inventario.TipoEquipamento",
            ),
            preserve_default=True,
        ),
    ]
