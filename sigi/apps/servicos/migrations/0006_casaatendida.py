# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0014_auto_20210406_1945'),
        ('servicos', '0005_auto_20210406_1945'),
    ]

    operations = [
        migrations.CreateModel(
            name='CasaAtendida',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name_plural': 'Casas atendidas',
            },
            bases=('casas.orgao',),
        ),
    ]
