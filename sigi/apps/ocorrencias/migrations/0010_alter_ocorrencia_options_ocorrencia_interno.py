# Generated by Django 4.0.6 on 2022-08-02 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ocorrencias', '0009_alter_comentario_options_categoria_projeto_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ocorrencia',
            options={'ordering': ['prioridade', '-data_modificacao', '-data_criacao'], 'verbose_name': 'ocorrência', 'verbose_name_plural': 'ocorrências'},
        ),
        migrations.AddField(
            model_name='ocorrencia',
            name='interno',
            field=models.BooleanField(default=True, help_text='Se marcado, essa ocorrência será visível apenas para servidores do Interlegis', verbose_name='Interno'),
        ),
    ]
