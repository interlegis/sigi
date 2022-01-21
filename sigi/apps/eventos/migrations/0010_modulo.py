# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servidores', '0007_auto_20210430_0735'),
        ('eventos', '0009_tipoevento_categoria'),
    ]

    operations = [
        migrations.CreateModel(
            name='Modulo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, verbose_name='Nome')),
                ('descricao', models.TextField(verbose_name='Descri\xe7\xe3o do m\xf3dulo')),
                ('tipo', models.CharField(max_length=1, verbose_name='Tipo', choices=[('A', 'Aula'), ('P', 'Palestra'), ('R', 'Apresenta\xe7\xe3o')])),
                ('inicio', models.DateTimeField(null=True, verbose_name='Data/hora de in\xedcio', blank=True)),
                ('termino', models.DateTimeField(null=True, verbose_name='Data/hora de t\xe9rmino', blank=True)),
                ('carga_horaria', models.PositiveIntegerField(default=0, verbose_name='carga hor\xe1ria')),
                ('qtde_participantes', models.PositiveIntegerField(default=0, help_text='Deixar Zero significa que todos os participantes do evento participaram do m\xf3dulo', verbose_name='n\xfamero de participantes')),
                ('apresentador', models.ForeignKey(related_name='modulo_apresentador', on_delete=django.db.models.deletion.PROTECT, verbose_name='Apresentador', blank=True, to='servidores.Servidor', null=True)),
                ('evento', models.ForeignKey(verbose_name='Evento', to='eventos.Evento', on_delete=models.CASCADE)),
                ('monitor', models.ForeignKey(related_name='modulo_monitor', on_delete=django.db.models.deletion.PROTECT, blank=True, to='servidores.Servidor', help_text='Monitor, mediador, auxiliar, etc.', null=True, verbose_name='Monitor')),
            ],
            options={
                'verbose_name': 'M\xf3dulo do evento',
                'verbose_name_plural': 'M\xf3dulos do evento',
            },
            bases=(models.Model,),
        ),
    ]
