# Generated by Django 4.1.7 on 2023-04-14 17:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("servidores", "0012_add_user_interlegis"),
    ]

    operations = [
        migrations.AddField(
            model_name="servidor",
            name="moodle_userid",
            field=models.PositiveBigIntegerField(
                blank=True,
                help_text="Código do usuário no Saberes",
                null=True,
                verbose_name="ID usuário Saberes",
            ),
        ),
    ]
