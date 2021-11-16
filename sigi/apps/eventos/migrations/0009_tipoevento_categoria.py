# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0008_auto_20211104_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipoevento',
            name='categoria',
            field=models.CharField(default='E', max_length=1, verbose_name='Categoaria', choices=[(b'C', 'Curso'), (b'E', 'Encontro'), (b'O', 'Oficina'), (b'S', 'Semin\xe1rio'), (b'V', 'Visita')]),
            preserve_default=False,
        ),
    ]
