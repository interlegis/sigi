# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db.models import Sum


def atualiza_participantes(apps, schema_editor):
    if schema_editor.connection.alias != "default":
        return

    Evento = apps.get_model("eventos", "Evento")

    for e in Evento.objects.all():
        total = e.convite_set.aggregate(total=Sum("qtde_participantes"))
        total = total["total"]
        if (total is not None) or (total > 0):
            e.total_participantes = total
            e.save()


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0011_auto_20211117_0633"),
    ]

    operations = [
        migrations.RunPython(atualiza_participantes),
    ]
