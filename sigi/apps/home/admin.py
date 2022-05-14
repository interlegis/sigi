from django.contrib import admin
from sigi.apps.home.models import Cards, Dashboard


@admin.register(Cards)
class CardAdmin(admin.ModelAdmin):
    list_display = ("codigo", "titulo", "categoria", "ordem", "default")
    list_editable = ("titulo", "categoria", "ordem", "default")
    search_fields = ("titulo", "codigo")


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("card", "categoria", "ordem")
    exclude = ("usuario",)
    list_editable = ("categoria", "ordem")
    autocomplete_fields = ("card",)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.usuario = request.user
        if obj.categoria == "":
            obj.categoria = obj.card.categoria
        if obj.ordem == 0:
            obj.ordem = obj.card.ordem
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(usuario=request.user)
