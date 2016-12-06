# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocorrencias', '0002_auto_20160308_0828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anexo',
            name='descricao',
            field=models.CharField(max_length=70, verbose_name='descri\xe7\xe3o do anexo'),
            preserve_default=True,
        ),
    ]
