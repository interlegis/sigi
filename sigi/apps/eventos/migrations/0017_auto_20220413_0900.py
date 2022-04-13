# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0016_auto_20220407_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evento',
            name='status',
            field=models.CharField(max_length=1, verbose_name='Status', choices=[(b'E', 'Em planejamento'), (b'G', 'Aguardando abertura SIGAD'), (b'P', 'Previs\xe3o'), (b'A', 'A confirmar'), (b'O', 'Confirmado'), (b'R', 'Realizado'), (b'C', 'Cancelado'), (b'Q', 'Arquivado')]),
            preserve_default=True,
        ),
    ]
