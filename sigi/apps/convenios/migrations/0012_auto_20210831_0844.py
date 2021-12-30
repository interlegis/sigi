# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date
from django.db import models, migrations

def migra_data_termino_vigencia(apps, schema_editor):
    Convenio = apps.get_model('convenios', 'Convenio')

    for c in Convenio.objects.all():
        if (c.data_retorno_assinatura is None or c.duracao is None):
            continue

        ano = c.data_retorno_assinatura.year + int(c.duracao / 12)
        mes = int(c.data_retorno_assinatura.month + int(c.duracao % 12))
        if mes > 12:
            ano = ano + 1
            mes = mes - 12
        dia = c.data_retorno_assinatura.day

        while True:
            try:
                data_fim = date(year=ano, month=mes,day=dia)
                break
            except:
                dia = dia - 1

        c.data_termino_vigencia = data_fim
        c.save()

class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0011_convenio_data_termino_vigencia'),
    ]

    operations = [
        migrations.RunPython(migra_data_termino_vigencia),
    ]
