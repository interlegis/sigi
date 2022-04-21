# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("servicos", "0003_auto_20170407_1003"),
    ]

    operations = [
        migrations.DeleteModel(
            name="CasaAtendida",
        ),
    ]
