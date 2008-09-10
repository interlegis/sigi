from django.contrib.admin.sites import AdminSite
from django.contrib.sites.admin import Site, SiteAdmin
from maintenancemode.admin import AllowedPath, AllowedPathAdmin
from sigi.apps.casas.admin import CasaLegislativa, CasaLegislativaAdmin

class DefaultSite(AdminSite):
    index_template = 'index.html'
    login_template = 'login.html'

default = DefaultSite()
default.register(Site, SiteAdmin)
default.register(AllowedPath, AllowedPathAdmin)
default.register(CasaLegislativa, CasaLegislativaAdmin)
