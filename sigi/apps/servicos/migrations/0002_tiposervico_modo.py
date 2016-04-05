# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiposervico',
            name='modo',
            field=models.CharField(default='H', max_length=1, verbose_name='Modo de presta\xe7\xe3o do servi\xe7o', choices=[(b'H', 'Hospedagem'), (b'R', 'Registro')]),
            preserve_default=False,
        ),
    ]
