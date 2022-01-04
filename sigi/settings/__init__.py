try:
    from sigi.settings.production import *
except ImportError:
    from django.core.exceptions import ImproperlyConfigured
    msg = """
  ######################################################################
  Arquivo production.py (django settings) nao encontrado.
  Se vc esta num ambiente de desenvolvimento pode cria-lo com
    ln -s development.py production.py
  ######################################################################
"""
    raise ImproperlyConfigured(msg)
