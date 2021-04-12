# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0002_convenio_duracao'),
        ('casas', '0014_auto_20210406_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convenio',
            name='casa_legislativa',
            field=models.ForeignKey(verbose_name='Casa Legislativa', to='casas.Orgao'),
            preserve_default=True,
        ),
    ]
