from django.contrib import admin


def site_context(request):
    return admin.site.each_context(request) or {}
