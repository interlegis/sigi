from django import forms
from django.utils.translation import gettext as _
from localflavor.br.forms import BRCNPJField, BRCPFField, BRZipCodeField
from material.admin.widgets import MaterialAdminTextareaWidget
from sigi.apps.casas.models import Funcionario, Orgao
from sigi.apps.parlamentares.models import Parlamentar
