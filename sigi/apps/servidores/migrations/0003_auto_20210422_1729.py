# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servidores', '0002_auto_20210416_0841'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ferias',
            name='servidor',
        ),
        migrations.DeleteModel(
            name='Ferias',
        ),
        migrations.RemoveField(
            model_name='funcao',
            name='servidor',
        ),
        migrations.DeleteModel(
            name='Funcao',
        ),
        migrations.RemoveField(
            model_name='licenca',
            name='servidor',
        ),
        migrations.DeleteModel(
            name='Licenca',
        ),
        migrations.RemoveField(
            model_name='subsecretaria',
            name='responsavel',
        ),
        migrations.RemoveField(
            model_name='servico',
            name='subsecretaria',
        ),
        migrations.DeleteModel(
            name='Subsecretaria',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='apontamentos',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='ato_exoneracao',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='ato_numero',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='cpf',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='data_nascimento',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='data_nomeacao',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='de_fora',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='email_pessoal',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='matricula',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='obs',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='ramal',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='rg',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='sexo',
        ),
        migrations.RemoveField(
            model_name='servidor',
            name='turno',
        ),
        migrations.AddField(
            model_name='servico',
            name='subordinado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='subordinado a', to='servidores.Servico', null=True),
            preserve_default=True,
        ),
    ]
