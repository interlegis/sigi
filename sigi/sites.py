from django.contrib.admin.sites import AdminSite
from sigi.apps.casas.admin import CasaLegislativa, CasaLegislativaAdmin

class DefaultSite(AdminSite):
    index_template = 'index.html'
    login_template = 'login.html'

default = DefaultSite()
default.register(CasaLegislativa, CasaLegislativaAdmin)
