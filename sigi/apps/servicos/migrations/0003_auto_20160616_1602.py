# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0002_tiposervico_modo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tiposervico',
            name='sigla',
            field=models.CharField(max_length=12, verbose_name='Sigla'),
            preserve_default=True,
        ),
    ]
