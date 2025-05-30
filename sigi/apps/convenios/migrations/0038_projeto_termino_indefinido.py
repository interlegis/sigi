# Generated by Django 5.2.1 on 2025-05-23 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("convenios", "0037_ajusta_acts_pendentes_gertiq_184827"),
    ]

    operations = [
        migrations.AddField(
            model_name="projeto",
            name="termino_indefinido",
            field=models.BooleanField(
                default=True,
                help_text="Indica se os convênios deste tipo podem estar vigentes sem ter uma data de término de vigência.",
                verbose_name="Término indefinido",
            ),
        ),
    ]
