# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ("diagnosticos", "0003_auto_20201101_2240"),
        ("casas", "0014_auto_20210406_1945"),
    ]

    operations = [
        migrations.AlterField(
            model_name="diagnostico",
            name="casa_legislativa",
            field=models.ForeignKey(
                verbose_name="Casa Legislativa", to="casas.Orgao"
            ),
            preserve_default=True,
        ),
    ]
