# -*- coding: utf-8 -*-
# Atualiza a data de último uso dos serviços SEIT realizados pelas Casas Legislativas
# Colocar no CRON - basta executar uma vez por dia
#

import sys
from django.core.management import setup_environ

# Produção
sys.path.insert(0, '/var/interlegis/sigi')
sys.path.insert(0, '/var/interlegis/sigi/sigi')

# Dev
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '../..')
PROJECT_DIR = BASE_DIR + '/sigi'
print BASE_DIR, PROJECT_DIR
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, PROJECT_DIR)

# Faça!
from sigi import settings
setup_environ(settings)

from sigi.apps.servicos.models import Servico

queryset = Servico.objects.exclude(url="").exclude(tipo_servico__string_pesquisa="")
for obj in queryset: 
    obj.atualiza_data_uso()
    print obj.url, obj.data_ultimo_uso, obj.erro_atualizacao