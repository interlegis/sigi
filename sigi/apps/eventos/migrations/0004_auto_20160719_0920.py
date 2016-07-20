# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0003_auto_20151104_0810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='curso_moodle_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Curso saberes', choices=[(None, '---------'), (851L, 'Implanta\xe7\xe3o SAPL em Cuiab\xe1')]),
            preserve_default=True,
        ),
    ]
