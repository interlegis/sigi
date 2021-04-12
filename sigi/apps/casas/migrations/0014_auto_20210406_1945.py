# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_cropping.fields
import sigi.apps.utils


class Migration(migrations.Migration):

    dependencies = [
        # ('metas', '0002_auto_20210406_1945'),
        ('contatos', '0002_auto_20151104_0810'),
        ('servidores', '0001_initial'),
        # ('parlamentares', '0002_auto_20210406_1945'),
        # ('servicos', '0005_auto_20210406_1945'),
        ('servicos', '0004_delete_casaatendida'),
        # ('inventario', '0002_auto_20210406_1945'),
        # ('convenios', '0003_auto_20210406_1945'),
        # ('ocorrencias', '0003_auto_20210406_1945'),
        # ('diagnosticos', '0004_auto_20210406_1945'),
        # ('eventos', '0005_auto_20210406_1945'),
        ('casas', '0013_auto_20210406_1428'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CasaLegislativa',
            new_name='Orgao',
        ),
    ]
