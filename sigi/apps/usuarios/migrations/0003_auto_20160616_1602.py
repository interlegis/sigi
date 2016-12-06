# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0002_auto_20160616_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmaemail',
            name='email',
            field=models.EmailField(unique=True, max_length=75, verbose_name='Email'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(unique=True, max_length=75, verbose_name='Email'),
            preserve_default=True,
        ),
    ]
