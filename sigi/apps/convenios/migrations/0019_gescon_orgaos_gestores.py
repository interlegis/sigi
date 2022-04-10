# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0018_auto_20211208_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='gescon',
            name='orgaos_gestores',
            field=models.TextField(default='SCCO', help_text='Siglas de \xf3rg\xe3os gestores que devem aparecer no campoORGAOSGESTORESTITULARES<ul><li>Informe um sigla por linha.</li><li>Ocorrendo qualquer uma das siglas, o contrato ser\xe1 importado.</li></ul>', verbose_name='\xd3rg\xe3os gestores'),
            preserve_default=True,
        ),
    ]
