# Generated by Django 4.1.7 on 2023-03-29 18:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("convenios", "0033_alter_projeto_modelo_minuta_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="gescon",
            name="checksums",
            field=models.JSONField(null=True),
        ),
    ]
