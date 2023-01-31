# Generated by Django 4.1.5 on 2023-01-26 14:35

from django.db import migrations
from django.contrib.auth import get_user_model


def forwards_migration(apps, schema_editor):
    Servidor = apps.get_model("servidores", "Servidor")
    User = get_user_model()

    sigi = Servidor.objects.get(sigi=True)

    if sigi.user is not None:
        # everything is already fine
        return

    try:
        usuario = User.objects.get_by_natural_key("interlegis")
    except User.DoesNotExist:
        usuario = User.objects.create_superuser("interlegis")

    sigi.user_id = usuario.id
    sigi.save()


class Migration(migrations.Migration):

    dependencies = [
        ("servidores", "0011_add_servidor_sigi"),
    ]

    operations = [
        migrations.RunPython(forwards_migration, migrations.RunPython.noop),
    ]
