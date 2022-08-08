# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def separa_turma(apps, schema_editor):
    Evento = apps.get_model("eventos", "Evento")
    for evento in Evento.objects.filter(nome__icontains='Turma'):
        split_name = evento.nome.rsplit('-', 1)
        if len(split_name) == 2:
            evento.nome = split_name[0].strip()
            evento.turma = split_name[1].strip()
            evento.save()

def junta_turma(apps, schema_editor):
    Evento = apps.get_model("eventos", "Evento")
    for evento in Evento.objects.exclude(turma=''):
        evento.nome = evento.nome + ' - ' + evento.turma
        evento.save()

class Migration(migrations.Migration):

    dependencies = [
        ('eventos', '0018_evento_turma'),
    ]

    operations = [
        migrations.RunPython(separa_turma, junta_turma),
    ]
