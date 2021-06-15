try:
    from sigi.settings.prod import *
except ImportError as e:
    from django.core.exceptions import ImproperlyConfigured
    msg = """

  ######################################################################
  Arquivo prod.py (django settings) nao encontrado.
  Se vc esta num ambiente de desenvolvimento pode cria-lo com
    ln -s dev.py prod.py
  ######################################################################


""" + str(e)
    raise ImproperlyConfigured(msg)
