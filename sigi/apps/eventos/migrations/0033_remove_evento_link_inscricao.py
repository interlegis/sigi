# Generated by Django 4.1.7 on 2023-04-14 15:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("eventos", "0032_set_moodle_courseid"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="evento",
            name="link_inscricao",
        ),
    ]