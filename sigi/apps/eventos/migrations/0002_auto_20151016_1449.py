# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='curso_moodle_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Curso saberes', choices=[(None, '---------'), (None, "Erro ao acessar o saberes: 'invalidtoken (moodle_exception): Token inv\xe1lido - token n\xe3o encontrado'")]),
            preserve_default=True,
        ),
    ]
