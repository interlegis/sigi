# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('casas', '0009_auto_20210406_1055'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='TipoCasaLegislativa',
            new_name='TipoOrgao',
        ),
    ]
