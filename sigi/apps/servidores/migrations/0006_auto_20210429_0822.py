# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('servidores', '0005_auto_20210423_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servidor',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
