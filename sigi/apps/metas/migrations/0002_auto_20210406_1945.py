# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metas', '0001_initial'),
        ('casas', '0014_auto_20210406_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planodiretor',
            name='casa_legislativa',
            field=models.ForeignKey(verbose_name='Casa Legislativa', to='casas.Orgao'),
            preserve_default=True,
        ),
    ]
