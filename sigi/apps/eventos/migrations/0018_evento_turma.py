# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0017_auto_20220413_0900'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='turma',
            field=models.CharField(max_length=100, verbose_name='Turma', blank=True),
            preserve_default=True,
        ),
    ]
