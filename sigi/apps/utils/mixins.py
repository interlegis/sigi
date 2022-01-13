from collections import OrderedDict
from functools import update_wrapper
from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.options import csrf_protect_m
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext as _, ngettext
from import_export.admin import ExportMixin

class CartExportMixin(ExportMixin):
    actions = ['add_to_cart']
    change_list_template = 'admin/cart/change_list_cart_export.html'
    _cart_session_name = None
    _cart_viewing_name = None

    def __init__(self, *args, **kwargs):
        super(CartExportMixin, self).__init__(*args, **kwargs)
        self._cart_session_name = 'cart_%s' % self.opts.model_name
        self._cart_viewing_name = 'view_cart_%s' % self.opts.model_name

    def get_queryset(self, request):
        qs = super(CartExportMixin, self).get_queryset(request)
        if self._cart_viewing_name in request.session:
            ids = request.session.get(self._cart_session_name, [])
            qs = qs.filter(id__in=ids)
        return qs

    def get_actions(self, request):
        if self._cart_viewing_name in request.session:
            action = self.get_action('remove_from_cart')
            return OrderedDict([(action[1], action)])
        else:
            return super(CartExportMixin, self).get_actions(request)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if 'cart' in request.GET:
            request.GET._mutable = True
            cart = request.GET.get('cart', '0')
            request.GET.pop('cart', None)
            request.GET._mutable = False
            if cart == '1':
                request.session[self._cart_viewing_name] = True
            else:
                request.session.pop(self._cart_viewing_name, None)

        cart_item_count = len(request.session.get(self._cart_session_name, []))

        extra_context = extra_context or {}
        extra_context['cart_item_count'] = (
            _('Vazio') if cart_item_count == 0
            else _(f'{cart_item_count} itens')
        )

        if self._cart_viewing_name in request.session:
            extra_context['viewing_cart'] = True
        return super(CartExportMixin, self).changelist_view(request, extra_context)

    def get_urls(self):
        from django.urls import path
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        paths = super(CartExportMixin, self).get_urls()
        paths.insert(2, path(
            'clearcart/',
            wrap(self.clear_cart),
            name='%s_%s_clearcart' % info
        ))
        return paths

    @csrf_protect_m
    def add_to_cart(self, request, queryset):
        if request.POST.get('select_across', '0') == '0':
            selected_ids = set(
                request.POST.getlist(helpers.ACTION_CHECKBOX_NAME, [])
            )
        else:
            selected_ids = set(
                map(str, queryset.values_list('id', flat=True))
            )

        if self._cart_session_name in request.session:
            cart_ids = set(request.session[self._cart_session_name])
        else:
            cart_ids = set()

        quant = len(selected_ids.difference(cart_ids))

        if quant:
            cart_ids.update(selected_ids)
            request.session[self._cart_session_name] = list(cart_ids)
            self.message_user(
                request,
                _(u"%s itens adicionados no carrinho") % quant)
        else:
            self.message_user(
                request,
                _(u"Os itens selecionados já estavam no carrinho"))
        return HttpResponseRedirect('.')
    add_to_cart.short_description = _(
        "Armazenar itens no carrinho para exportar"
    )

    @csrf_protect_m
    def remove_from_cart(self, request, queryset):
        if self._cart_session_name not in request.session:
            self.message_user(request, _(u"O carrinho está vazio"))
            return HttpResponseRedirect('.')

        if request.POST.get('select_across', '0') == '0':
            remove_ids = set(request.POST.getlist(helpers.ACTION_CHECKBOX_NAME))
        else:
            remove_ids = set(map(str, queryset.values_list('id', flat=True)))
        cart_ids = set(request.session[self._cart_session_name])

        request.session[self._cart_session_name] = list(
            cart_ids.difference(remove_ids)
        )

        self.message_user(request, _(u"%s itens removidos do carrinho.") %
                          len(cart_ids.intersection(remove_ids)))

        return HttpResponseRedirect('.')
    remove_from_cart.short_description = _("Remove itens do carrinho")

    @csrf_protect_m
    def clear_cart(self, request):
        request.session.pop(self._cart_session_name, None)
        request.session.pop(self._cart_viewing_name, None)
        self.message_user(request, _(u"Carrinho vazio"))
        return HttpResponseRedirect('..')
