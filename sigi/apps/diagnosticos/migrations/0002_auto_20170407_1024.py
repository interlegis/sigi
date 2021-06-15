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
            model_name='pergunta',
            name='name',
            field=autoslug.fields.AutoSlugField(populate_from=b'title', editable=True, max_length=250, blank=True, verbose_name='name', slugify=eav.models.slugify_attr_name),
            preserve_default=True,
        ),
    ]
