# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocorrencias', '0004_auto_20210416_0841'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='categoria',
            options={'ordering': ('nome',), 'verbose_name': 'Categoria', 'verbose_name_plural': 'Categorias'},
        ),
    ]
