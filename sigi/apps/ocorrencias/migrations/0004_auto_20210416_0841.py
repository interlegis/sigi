# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ocorrencias', '0003_auto_20210406_1945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='categoria',
            name='setor_responsavel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Setor respons\xe1vel', to='servidores.Servico'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='comentario',
            name='encaminhar_setor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Encaminhar para setor', blank=True, to='servidores.Servico', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='comentario',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Usu\xe1rio', to='servidores.Servidor'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ocorrencia',
            name='categoria',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Categoria', to='ocorrencias.Categoria'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ocorrencia',
            name='servidor_registro',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Servidor que registrou a ocorr\xeancia', to='servidores.Servidor'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ocorrencia',
            name='setor_responsavel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Setor respons\xe1vel', to='servidores.Servico'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ocorrencia',
            name='tipo_contato',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Tipo de contato', to='ocorrencias.TipoContato'),
            preserve_default=True,
        ),
    ]
