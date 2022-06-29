# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("parlamentares", "0001_initial"),
        ("casas", "0014_auto_20210406_1945"),
    ]

    operations = [
        migrations.AlterField(
            model_name="legislatura",
            name="casa_legislativa",
            field=models.ForeignKey(to="casas.Orgao", on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="mesadiretora",
            name="casa_legislativa",
            field=models.ForeignKey(
                verbose_name="Casa Legislativa",
                to="casas.Orgao",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
