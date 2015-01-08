# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CategoriasInteresse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefixo', models.CharField(help_text='Identifica as categorias no Moodle (campo idnumber) relacionadas a este interesse', max_length=100, verbose_name='Prefixo das categorias no Moodle')),
                ('descricao', models.CharField(max_length=100, verbose_name='Descri\xe7\xe3o')),
                ('sigla', models.CharField(max_length=20, verbose_name='Sigla')),
                ('coorte', models.BooleanField(default=False, help_text='Usa cohorte para calcular o n\xfamero de matr\xedculas/alunos', verbose_name='Usa Cohorte')),
                ('apurar_alunos', models.BooleanField(default=False, help_text='Indica que deve-se verificar o perfil da inscri\xe7\xe3o para saber se \xe9 um aluno ou se a matr\xedcula foi rejeitada', verbose_name='Apurar alunos')),
                ('apurar_conclusao', models.BooleanField(default=False, help_text='Indica se o dashboard mostrar\xe1 o n\xfamero de alunos aprovados, reprovados e desistentes', verbose_name='Apurar conclus\xe3o')),
            ],
            options={
                'verbose_name': 'Categorias de interesse',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PainelItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('painel', models.CharField(max_length=255)),
                ('descricao', models.CharField(max_length=255)),
                ('help_text', models.CharField(max_length=255)),
                ('valor', models.IntegerField()),
                ('percentual', models.FloatField(null=True)),
            ],
            options={
                'ordering': ['pk'],
            },
            bases=(models.Model,),
        ),
    ]
