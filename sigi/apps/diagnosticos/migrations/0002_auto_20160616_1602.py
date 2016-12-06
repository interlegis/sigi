# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
import eav.models


class Migration(migrations.Migration):

    dependencies = [
        ('diagnosticos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anexo',
            name='descricao',
            field=models.CharField(max_length=70, verbose_name='descri\xe7\xe3o'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='escolha',
            name='schema_to_open',
            field=models.ForeignKey(related_name='schema_to_open_related', verbose_name='pergunta para abrir', blank=True, to='diagnosticos.Pergunta', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='pergunta',
            name='name',
            field=autoslug.fields.AutoSlugField(populate_from=b'title', editable=True, max_length=250, blank=True, verbose_name='name', slugify=eav.models.slugify_attr_name),
            preserve_default=True,
        ),
    ]
