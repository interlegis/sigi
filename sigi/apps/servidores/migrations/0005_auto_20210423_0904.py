# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servidores', '0004_auto_20210422_1907'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servico',
            options={'ordering': ('-subordinado__sigla', 'nome'), 'verbose_name': 'servi\xe7o', 'verbose_name_plural': 'servi\xe7os'},
        ),
    ]
