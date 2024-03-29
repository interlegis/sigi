# Generated by Django 4.2.7 on 2024-03-12 14:15

from datetime import datetime
from django.db import migrations
from django.utils import timezone


def forward(apps, schema_editor):
    Evento = apps.get_model("eventos", "Evento")
    for evento in Evento.objects.all():
        if evento.data_inicio is not None:
            evento.hora_inicio = timezone.localtime(evento.data_inicio).time()
        if evento.data_termino is not None:
            evento.hora_termino = timezone.localtime(
                evento.data_termino
            ).time()
        evento.save()


def backward(apps, schema_editor):
    Evento = apps.get_model("eventos", "Evento")
    for evento in Evento.objects.all():
        if evento.data_inicio is not None and evento.hora_inicio is not None:
            evento.data_inicio = datetime.combine(
                evento.data_inicio, evento.hora_inicio
            ).replace(tzinfo=timezone.get_current_timezone())
        elif evento.data_inicio is not None:
            evento.data_inicio.replace(tzinfo=timezone.get_current_timezone())
        if evento.data_termino is not None and evento.hora_termino is not None:
            evento.data_termino = datetime.combine(
                evento.data_termino, evento.hora_termino
            ).replace(tzinfo=timezone.get_current_timezone())
        elif evento.data_termino is not None:
            evento.data_termino.replace(tzinfo=timezone.get_current_timezone())
        evento.save()


class Migration(migrations.Migration):

    dependencies = [
        ("eventos", "0058_evento_hora_inicio_evento_hora_termino"),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
