# Generated by Django 4.1.7 on 2023-03-10 20:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("contatos", "0006_alter_unidadefederativa_regiao"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="mesorregiao",
            options={
                "ordering": ("uf", "nome"),
                "verbose_name": "mesorregião",
                "verbose_name_plural": "mesorregiões",
            },
        ),
    ]
