# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0017_auto_20210416_0841'),
    ]

    operations = [
        migrations.AddField(
            model_name='orgao',
            name='sigla',
            field=models.CharField(max_length=30, verbose_name='sigla do \xf3rg\xe3o', blank=True),
            preserve_default=True,
        ),
    ]
