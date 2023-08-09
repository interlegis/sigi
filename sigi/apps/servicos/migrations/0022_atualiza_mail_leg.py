# Generated by Django 4.1.5 on 2023-01-25 14:40

from django.db import migrations


def mailleg_fw(apps, schema_editor):
    TipoServico = apps.get_model("servicos", "TipoServico")
    tipo = TipoServico.objects.get(sigla__icontains="mail")
    tipo.tipo_rancher = "emailleg"
    tipo.arquivo_rancher = "mail.json"
    tipo.spec_rancher = "mail"
    tipo.prefixo_padrao = "correioadm"
    tipo.save()


def mailleg_rw(apps, schema_editor):
    TipoServico = apps.get_model("servicos", "TipoServico")
    tipo = TipoServico.objects.get(sigla__icontains="mail")
    tipo.tipo_rancher = ""
    tipo.arquivo_rancher = ""
    tipo.spec_rancher = ""
    tipo.prefixo_padrao = ""
    tipo.save()


class Migration(migrations.Migration):
    dependencies = [
        ("servicos", "0021_remove_servico_unique_instance_and_more"),
    ]

    operations = [
        migrations.RunPython(mailleg_fw, mailleg_rw),
    ]
