# -*- coding: utf-8 -*-
import sys
from django.core.management import setup_environ

# Produção
sys.path.insert(0, '/var/interlegis/sigi')
sys.path.insert(0, '/var/interlegis/sigi/sigi')

# Dev
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '../../..')
PROJECT_DIR = BASE_DIR + '/sigi'
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, PROJECT_DIR)

# Faça!
from sigi import settings
setup_environ(settings)

from sigi.apps.metas.views import gera_map_data_file
print gera_map_data_file(get_error=True)