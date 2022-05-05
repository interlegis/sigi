# Generated by Django 4.0.4 on 2022-05-05 13:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('convenios', '0021_projeto_texto_minuta_projeto_texto_oficio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projeto',
            name='texto_minuta',
        ),
        migrations.AddField(
            model_name='projeto',
            name='modelo_minuta',
            field=models.FileField(blank=True, help_text='Use as seguintes marcações:<ul><li>{{ casa.nome }} para o nome da Casa Legislativa / órgão</li><li>{{ casa.municipio.uf.sigla }} para a sigla da UF da Casa legislativa</li><li>{{ presidente.nome }} para o nome do presidente</li><li>{{ contato.nome }} para o nome do contato Interlegis</li></ul>', upload_to='convenios/minutas/', validators=[django.core.validators.FileExtensionValidator], verbose_name='Modelo de minuta'),
        ),
    ]
