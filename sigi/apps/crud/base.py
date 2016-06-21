# -*- coding: utf-8 -*-

from __future__ import absolute_import
from braces.views import FormMessagesMixin
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.utils.decorators import classonlymethod
from django.utils.translation import ugettext_lazy as _
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .utils import make_pagination
from sigi.apps.crispy_layout_mixin import CrispyLayoutFormMixin, get_field_display

LIST, CREATE, DETAIL, UPDATE, DELETE = \
    u'list', u'create', u'detail', u'update', u'delete'


def _form_invalid_message(msg):
    return u'%s %s' % (_(u'Formulário inválido.'), msg)

FORM_MESSAGES = {CREATE: (_(u'Registro criado com sucesso!'),
                          _(u'O registro não foi criado.')),
                 UPDATE: (_(u'Registro alterado com sucesso!'),
                          _(u'Suas alterações não foram salvas.')),
                 DELETE: (_(u'Registro excluído com sucesso!'),
                          _(u'O registro não foi excluído.'))}
FORM_MESSAGES = dict((k, (a, _form_invalid_message(b)))
                 for k, (a, b) in FORM_MESSAGES.items())


class CrudBaseMixin(CrispyLayoutFormMixin):

    @classmethod
    def url_name(cls, suffix):
        return u'%s_%s' % (cls.model._meta.model_name, suffix)

    def resolve_url(self, suffix, args=None):
        namespace = self.model._meta.app_label
        return reverse(u'%s:%s' % (namespace, self.url_name(suffix)),
                       args=args)

    @property
    def list_url(self):
        return self.resolve_url(LIST)

    @property
    def create_url(self):
        return self.resolve_url(CREATE)

    @property
    def detail_url(self):
        return self.resolve_url(DETAIL, args=(self.object.id,))

    @property
    def update_url(self):
        return self.resolve_url(UPDATE, args=(self.object.id,))

    @property
    def delete_url(self):
        return self.resolve_url(DELETE, args=(self.object.id,))

    def get_template_names(self):
        names = super(CrudBaseMixin, self).get_template_names()
        names.append(u"crud/%s.html" %
                     self.template_name_suffix.lstrip(u'_'))
        return names

    @property
    def verbose_name(self):
        return self.model._meta.verbose_name

    @property
    def verbose_name_plural(self):
        return self.model._meta.verbose_name_plural


class CrudListView(ListView):

    @classmethod
    def get_url_regex(cls):
        return ur'^$'

    paginate_by = 10
    no_entries_msg = _(u'Nenhum registro encontrado.')

    def get_rows(self, object_list):
        return [self._as_row(obj) for obj in object_list]

    def get_headers(self):
        return [self.model._meta.get_field(fieldname).verbose_name
                for fieldname in self.list_field_names]

    def _as_row(self, obj):
        return [
            (get_field_display(obj, name)[1],
             self.resolve_url(DETAIL, args=(obj.id,)) if i == 0 else None)
            for i, name in enumerate(self.list_field_names)]

    def get_context_data(self, **kwargs):
        context = super(CrudListView, self).get_context_data(**kwargs)
        context.setdefault(u'title', self.verbose_name_plural)

        # pagination
        if self.paginate_by:
            page_obj = context[u'page_obj']
            paginator = context[u'paginator']
            context[u'page_range'] = make_pagination(
                page_obj.number, paginator.num_pages)

        # rows
        object_list = context[u'object_list']
        context[u'headers'] = self.get_headers()
        context[u'rows'] = self.get_rows(object_list)

        context[u'NO_ENTRIES_MSG'] = self.no_entries_msg

        return context


class CrudCreateView(FormMessagesMixin, CreateView):

    @classmethod
    def get_url_regex(cls):
        return ur'^create$'

    form_valid_message, form_invalid_message = FORM_MESSAGES[CREATE]

    @property
    def cancel_url(self):
        return self.list_url

    def get_success_url(self):
        return self.detail_url

    def get_context_data(self, **kwargs):
        kwargs.setdefault(u'title', _(u'Adicionar %(verbose_name)s') % {
            u'verbose_name': self.verbose_name})
        return super(CrudCreateView, self).get_context_data(**kwargs)


class CrudDetailView(DetailView):

    @classmethod
    def get_url_regex(cls):
        return ur'^(?P<pk>\d+)$'


class CrudUpdateView(FormMessagesMixin, UpdateView):

    @classmethod
    def get_url_regex(cls):
        return ur'^(?P<pk>\d+)/edit$'

    form_valid_message, form_invalid_message = FORM_MESSAGES[UPDATE]

    @property
    def cancel_url(self):
        return self.detail_url

    def get_success_url(self):
        return self.detail_url


class CrudDeleteView(FormMessagesMixin, DeleteView):

    @classmethod
    def get_url_regex(cls):
        return ur'^(?P<pk>\d+)/delete$'

    form_valid_message, form_invalid_message = FORM_MESSAGES[DELETE]

    @property
    def cancel_url(self):
        return self.detail_url

    def get_success_url(self):
        return self.list_url


class Crud(object):
    BaseMixin = CrudBaseMixin
    ListView = CrudListView
    CreateView = CrudCreateView
    DetailView = CrudDetailView
    UpdateView = CrudUpdateView
    DeleteView = CrudDeleteView
    help_path = u''

    @classonlymethod
    def get_urls(cls):

        def _add_base(view):
            class CrudViewWithBase(cls.BaseMixin, view):
                model = cls.model
                help_path = cls.help_path
                crud = cls
            CrudViewWithBase.__name__ = view.__name__
            return CrudViewWithBase

        CrudListView = _add_base(cls.ListView)
        CrudCreateView = _add_base(cls.CreateView)
        CrudDetailView = _add_base(cls.DetailView)
        CrudUpdateView = _add_base(cls.UpdateView)
        CrudDeleteView = _add_base(cls.DeleteView)

        return [url(regex, view.as_view(), name=view.url_name(suffix))
                for regex, view, suffix in [
                    (CrudListView.get_url_regex(), CrudListView, LIST),
                    (CrudCreateView.get_url_regex(), CrudCreateView, CREATE),
                    (CrudDetailView.get_url_regex(), CrudDetailView, DETAIL),
                    (CrudUpdateView.get_url_regex(), CrudUpdateView, UPDATE),
                    (CrudDeleteView.get_url_regex(), CrudDeleteView, DELETE),
        ]]

    @classonlymethod
    def build(cls, _model, _help_path):

        class ModelCrud(cls):
            model = _model
            help_path = _help_path

        ModelCrud.__name__ = u'%sCrud' % _model.__name__
        return ModelCrud
