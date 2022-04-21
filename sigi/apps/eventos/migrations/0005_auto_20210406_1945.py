# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("eventos", "0004_remove_evento_curso_moodle_id"),
        ("casas", "0014_auto_20210406_1945"),
    ]

    operations = [
        migrations.AlterField(
            model_name="convite",
            name="casa",
            field=models.ForeignKey(
                verbose_name="Casa convidada",
                to="casas.Orgao",
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="evento",
            name="casa_anfitria",
            field=models.ForeignKey(
                verbose_name="Casa anfitri\xe3",
                blank=True,
                to="casas.Orgao",
                null=True,
                on_delete=models.CASCADE,
            ),
            preserve_default=True,
        ),
    ]
