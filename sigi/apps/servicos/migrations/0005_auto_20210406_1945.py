# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0004_delete_casaatendida'),
        ('casas', '0014_auto_20210406_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casamanifesta',
            name='casa_legislativa',
            field=models.OneToOneField(to='casas.Orgao', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='servico',
            name='casa_legislativa',
            field=models.ForeignKey(verbose_name='Casa Legislativa', to='casas.Orgao', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
