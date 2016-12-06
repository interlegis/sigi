# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solicitacoes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitacao',
            name='email_contato',
            field=models.EmailField(max_length=75, null=True, verbose_name='Email de contato', blank=True),
            preserve_default=True,
        ),
    ]
