# Generated by Django 4.0.5 on 2022-06-30 17:26

from django.db import migrations


def carrega_telefone_geral(apps, schema_editor):
    Orgao = apps.get_model("casas", "Orgao")
    Telefone = apps.get_model("contatos", "Telefone")
    telefones = Telefone.objects.filter(
        content_type__app_label="casas", content_type__model="orgao"
    )
    for orgao in Orgao.objects.all():
        telefone = (
            telefones.filter(object_id=orgao.id).exclude(numero="").first()
        )
        if telefone:
            orgao.telefone_geral = telefone.numero
            orgao.save()


class Migration(migrations.Migration):
    dependencies = [
        ("casas", "0025_orgao_telefone_geral"),
    ]

    operations = [
        migrations.RunPython(carrega_telefone_geral),
    ]
