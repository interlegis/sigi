from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^sigi/', include('sigi.casas.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
)
