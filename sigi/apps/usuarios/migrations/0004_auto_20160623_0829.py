# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-23 08:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_auto_20160616_1602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='confirmaemail',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email'),
        ),
    ]
