# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0015_anexo'),
    ]

    operations = [
        migrations.AddField(
            model_name='evento',
            name='data_pedido',
            field=models.DateField(help_text='Data em que o pedido do Gabinete chegou \xe0 COPERI', null=True, verbose_name='Data do pedido', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evento',
            name='num_processo',
            field=models.CharField(help_text='Formato:<em>XXXXX.XXXXXX/XXXX-XX</em>', max_length=20, verbose_name='n\xfamero do processo SIGAD', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evento',
            name='observacao',
            field=models.TextField(verbose_name='Observa\xe7\xf5es e anota\xe7\xf5es', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evento',
            name='status',
            field=models.CharField(max_length=1, verbose_name='Status', choices=[(b'E', 'Em planejamento'), (b'G', 'Aguardando abertura SIGAD'), (b'P', 'Previs\xe3o'), (b'A', 'A confirmar'), (b'O', 'Confirmado'), (b'R', 'Realizado'), (b'C', 'Cancelado')]),
            preserve_default=True,
        ),
    ]
