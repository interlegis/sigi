# Generated by Django 4.0.1 on 2022-02-13 13:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ocorrencias', '0006_alter_anexo_arquivo_alter_anexo_descricao_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comentario',
            name='encaminhar_setor',
        ),
        migrations.RemoveField(
            model_name='ocorrencia',
            name='setor_responsavel',
        ),
    ]
