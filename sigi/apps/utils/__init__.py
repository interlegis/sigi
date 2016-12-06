# -*- coding: utf-8 -*-
from unicodedata import normalize

from django.contrib import admin
from django.db import models
from django.contrib.admin import ModelAdmin


class SearchField(models.TextField):

    def pre_save(self, model_instance, add):
        search_text = []
        for field_name in self.field_names:
            val = unicode(to_ascii(getattr(model_instance, field_name)))
            search_text.append(val)
        value = u' '.join(search_text)
        setattr(model_instance, self.name, value)
        return value

    def __init__(self, field_names, *args, **kwargs):
        self.field_names = field_names
        kwargs['editable'] = False
        super(self.__class__, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(SearchField, self).deconstruct()
        kwargs['field_names'] = self.field_names
        return name, path, args, kwargs


def to_ascii(txt, codif='utf-8'):
    if not isinstance(txt, basestring):
        txt = unicode(txt)
    if isinstance(txt, unicode):
        txt = txt.encode('utf-8')
    return normalize('NFKD', txt.decode(codif)).encode('ASCII', 'ignore')


def queryset_ascii(self, request):
    if 'q' in request.GET:
        request.GET._mutable = True
        request.GET['q'] = to_ascii(request.GET['q'])
    return admin.ModelAdmin.get_queryset(self, request)
