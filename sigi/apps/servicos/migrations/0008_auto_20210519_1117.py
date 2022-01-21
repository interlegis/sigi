# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0007_auto_20210416_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servico',
            name='data_ultimo_uso',
            field=models.DateField(help_text='Data em que o servi\xe7o foi utilizado pela Casa Legislativa pela \xfaltima vez', null=True, verbose_name='Data da \xfaltima utiliza\xe7\xe3o', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='servico',
            name='erro_atualizacao',
            field=models.TextField(help_text='Erro ocorrido na \xfaltima tentativa de verificar a data de \xfaltima atualiza\xe7\xe3o do servi\xe7o', verbose_name='Erro na atualiza\xe7\xe3o', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiposervico',
            name='modo',
            field=models.CharField(max_length=1, verbose_name='modo de presta\xe7\xe3o do servi\xe7o', choices=[('H', 'Hospedagem'), ('R', 'Registro')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiposervico',
            name='nome',
            field=models.CharField(max_length=60, verbose_name='nome'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiposervico',
            name='sigla',
            field=models.CharField(max_length='12', verbose_name='sigla'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tiposervico',
            name='string_pesquisa',
            field=models.TextField(help_text='Par\xe2metros da pesquisa para averiguar a data da \xfaltima atualiza\xe7\xe3o do servi\xe7o. Formato:<br/><ul><li>/caminho/da/pesquisa/?parametros [xml|json] campo.de.data</li>', verbose_name='string de pesquisa', blank=True),
            preserve_default=True,
        ),
    ]
