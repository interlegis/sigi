# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0013_modelodeclaracao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelodeclaracao',
            name='texto',
            field=tinymce.models.HTMLField(help_text='Use as seguintes marca\xe7\xf5es:<ul><li>{{ casa.nome }} para o nome da Casa Legislativa / \xf3rg\xe3o</li><li>{{ casa.municipio.uf.sigla }} para a sigla da UF da Casa legislativa</li><li>{{ nome }} para o nome do visitante</li><li>{{ data }} para a data de emiss\xe3o da declara\xe7\xe3o</li><li>{{ evento.data_inicio }} para a data/hora do in\xedcio da visita</li><li>{{ evento.data_termino }} para a data/hora do t\xe9rmino da visita</li><li>{{ evento.nome }} para o nome do evento</li><li>{{ evento.descricao }} para a descri\xe7\xe3o do evento</li></ul>', verbose_name='Texto da declara\xe7\xe3o'),
            preserve_default=True,
        ),
    ]
