# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0002_auto_20151016_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='curso_moodle_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Curso saberes', choices=[(None, '---------'), (59L, 'Oficina Interlegis em Montes Claros, MG')]),
            preserve_default=True,
        ),
    ]
