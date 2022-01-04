# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0005_auto_20210406_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convite',
            name='casa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Casa convidada', to='casas.Orgao'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='convite',
            name='servidor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Servidor que convido', to='servidores.Servidor'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='equipe',
            name='funcao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Fun\xe7\xe3o na equipe', to='eventos.Funcao'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='equipe',
            name='membro',
            field=models.ForeignKey(related_name='equipe_evento', on_delete=django.db.models.deletion.PROTECT, to='servidores.Servidor'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evento',
            name='casa_anfitria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Casa anfitri\xe3', blank=True, to='casas.Orgao', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evento',
            name='municipio',
            field=models.ForeignKey(to='contatos.Municipio', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evento',
            name='tipo_evento',
            field=models.ForeignKey(to='eventos.TipoEvento', on_delete=django.db.models.deletion.PROTECT),
            preserve_default=True,
        ),
    ]
