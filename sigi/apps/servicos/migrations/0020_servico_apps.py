# Generated by Django 4.1.2 on 2022-11-08 19:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("servicos", "0019_ajusta_dominios"),
    ]

    operations = [
        migrations.AddField(
            model_name="servico",
            name="apps",
            field=models.TextField(
                blank=True, verbose_name="apps instaladas no DNS"
            ),
        ),
    ]
