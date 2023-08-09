# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("diagnosticos", "0004_auto_20210406_1945"),
    ]

    operations = [
        migrations.AlterField(
            model_name="diagnostico",
            name="casa_legislativa",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Casa Legislativa",
                to="casas.Orgao",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="diagnostico",
            name="responsavel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="respons\xe1vel",
                to="servidores.Servidor",
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="equipe",
            name="membro",
            field=models.ForeignKey(
                to="servidores.Servidor",
                on_delete=django.db.models.deletion.PROTECT,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="escolha",
            name="schema_to_open",
            field=models.ForeignKey(
                related_name="abre_por",
                on_delete=django.db.models.deletion.SET_NULL,
                verbose_name="pergunta para abrir",
                blank=True,
                to="diagnosticos.Pergunta",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="resposta",
            name="choice",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="escolha",
                blank=True,
                to="diagnosticos.Escolha",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name="resposta",
            name="schema",
            field=models.ForeignKey(
                related_name="attrs",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="pergunta",
                to="diagnosticos.Pergunta",
            ),
            preserve_default=True,
        ),
    ]
