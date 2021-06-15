# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0006_casaatendida'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servico',
            name='casa_legislativa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Casa Legislativa', to='casas.Orgao'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='servico',
            name='tipo_servico',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Tipo de servi\xe7o', to='servicos.TipoServico'),
            preserve_default=True,
        ),
    ]
