from django.contrib.admin.filterspecs import FilterSpec, ChoicesFilterSpec, BooleanFieldFilterSpec
from django.utils.encoding import smart_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from sigi.apps.contatos.models import UnidadeFederativa
from abc import ABCMeta
from apps.servicos.models import TipoServico
from apps.convenios.models import Projeto
from apps.casas.models import TipoCasaLegislativa

class IsActiveFilterSpec(BooleanFieldFilterSpec):
    """
    Adds filtering by user is_active attr in the admin filter sidebar
    my_model_user_field.is_active__filter = True
    """

    def __init__(self, f, request, params, model, model_admin):
        super(IsActiveFilterSpec, self).__init__(f, request, params, model,
                                                   model_admin)
        self.lookup_kwarg = '%s__is_active__exact' % f.name
        self.lookup_kwarg2 = '%s__is_active__isnull' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_val2 = request.GET.get(self.lookup_kwarg2, None)

    def title(self):
        return _('active')

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'is_active__filter', False),
                                   IsActiveFilterSpec))

class AlphabeticFilterSpec(ChoicesFilterSpec):
    """
    Adds filtering by first char (alphabetic style) of values in the admin
    filter sidebar. Set the alphabetic filter in the model field attribute
    'alphabetic_filter'.

    my_model_field.alphabetic_filter = True
    """

    def __init__(self, f, request, params, model, model_admin):
        super(AlphabeticFilterSpec, self).__init__(f, request, params, model,
                                                   model_admin)
        self.lookup_kwarg = '%s__istartswith' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        values_list = model.objects.values_list(f.name, flat=True)
        # getting the first char of values
        self.lookup_choices = list(set(val[0] for val in values_list if val))
        self.lookup_choices.sort()

    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val}),
                    'display': val.upper()}
    def title(self):
        return _('%(field_name)s that starts with') % \
            {'field_name': self.field.verbose_name}

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'alphabetic_filter', False),
                                   AlphabeticFilterSpec))

class AbstractFilterSpec(ChoicesFilterSpec):
    """  
    This is an abstract class and customs filters by 'Uf' have to extend this class.
    """
    __metaclass__ = ABCMeta
    def __init__(self, f, request, params, model, model_admin):
        super(AbstractFilterSpec, self).__init__(f, request, params, model, 
                                             model_admin)
        
    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val.codigo_ibge) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val.codigo_ibge}),
                    'display': val.nome}

class MunicipioUFFilterSpec(AbstractFilterSpec):
    """
    Usage:

      my_municipio_field.uf_filter = True

    On Django 1.3 you will can specify a lookup on admin filters. Example:

      list_filter = ('municipio__uf',)

    """

    def __init__(self, f, request, params, model, model_admin):
        super(MunicipioUFFilterSpec, self).__init__(f, request, params, model,
                                                    model_admin)
        self.lookup_kwarg = '%s__uf__codigo_ibge__exact' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = UnidadeFederativa.objects.all().order_by('nome')
    def title(self):
        return _('UF') % \
            {'field_name': self.field.verbose_name}


# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'uf_filter', False),
                             MunicipioUFFilterSpec))

class CasaUFFilterSpec(AbstractFilterSpec):
    """
    Usage:

      my_casa_legislativa_field.casa_uf_filter = True

    On Django 1.3 you will can specify a lookup on admin filters. Example:

      list_filter = ('casa_legislativa__municipio__uf',)

    """

    def __init__(self, f, request, params, model, model_admin):
        super(CasaUFFilterSpec, self).__init__(f, request, params, model,
                                                    model_admin)
        self.lookup_kwarg = '%s__municipio__uf__codigo_ibge__exact' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = UnidadeFederativa.objects.all().order_by('nome')
    def title(self):
        return _('UF') % \
            {'field_name': self.field.verbose_name}


# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'casa_uf_filter', False),
                             CasaUFFilterSpec))

class CasaTipoFilterSpec(ChoicesFilterSpec):
    """
    Usage:

      my_casa_legislativa_field.casa_tipo_filter = True

    On Django 1.3 you will can specify a lookup on admin filters. Example:

      list_filter = ('casa_legislativa__municipio__uf',)

    """

    def __init__(self, f, request, params, model, model_admin):
        super(CasaTipoFilterSpec, self).__init__(f, request, params, model,
                                                    model_admin)
        self.lookup_kwarg = '%s__tipo__id__exact' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = TipoCasaLegislativa.objects.all()
    def title(self):
        return _('Tipo de Casa Legislativa') % {'field_name': self.field.verbose_name}
    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val.id) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val.id}),
                    'display': val.nome}


# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'casa_tipo_filter', False),
                             CasaTipoFilterSpec))

class ConvenioUFFilterSpec(AbstractFilterSpec):
    """
    Usage:

      my_casa_legislativa_field.convenio_uf_filter = True

    On Django 1.3 you will can specify a lookup on admin filters. Example:

      list_filter = ('casa_legislativa__municipio__uf',)

    """
    def __init__(self, f, request, params, model, model_admin):
        super(ConvenioUFFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_kwarg = '%s__municipio__uf__codigo_ibge__exact' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = UnidadeFederativa.objects.all().order_by('nome')
    def title(self):
        return _('UF') % \
            {'field_name': self.field.verbose_name}

FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'convenio_uf_filter', False),
ConvenioUFFilterSpec))

class MunicipioRegiaoFilterSpec(AbstractFilterSpec):
    """
    Usage:

      my_municipio_field.uf_filter = True

    On Django 1.3 you will can specify a lookup on admin filters. Example:

      list_filter = ('municipio__uf',)

    """

    def __init__(self, f, request, params, model, model_admin):
        super(MunicipioRegiaoFilterSpec, self).__init__(f, request, params, model,
                                                    model_admin)
        self.lookup_kwarg = '%s__uf__regiao__exact' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = UnidadeFederativa.REGIAO_CHOICES
    def title(self):
        return _('UF') % \
            {'field_name': self.field.verbose_name}

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'regiao_filter', False),
                             MunicipioRegiaoFilterSpec))

class ConvenioRegiaoFilterSpec(AbstractFilterSpec):
    def __init__(self, f, request, params, model, model_admin):
        super(ConvenioUFFilterSpec, self).__init__(f, request, params, model, model_admin)
        self.lookup_kwarg = '%s__municipio__uf__regiao__exact' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = UnidadeFederativa.REGIAO_CHOICES

FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'convenio_regiao_filter', False), ConvenioRegiaoFilterSpec))

class RangeValuesFilterSpec(FilterSpec):
    """
    Author: Willie Gollino (wgollino@yahoo.com)
    License: LGPLv3

    Adds filtering by ranges of values in the admin filter sidebar.
    Set range split points in the model field attribute 'list_filter_range'.

    my_model_field.list_filter_range = [100, 200, 300]

    Will define the ranges:
      my_model_field < 100
      my_model_field >= 100 AND my_model_field < 200
      my_model_field >= 200 AND my_model_field < 300
      my_model_field >= 300
    """

    def __init__(self, f, request, params, model, model_admin):
        super(RangeValuesFilterSpec, self).__init__(f, request, params, model,
                                                    model_admin)
        self.field_generic = '%s__' % self.field.name
        self.parsed_params = dict([(k, v) for k, v in params.items() if k.startswith(self.field_generic)])

        self.links = [(_('All'), {})]

        last_value = None
        for max_value in sorted(f.list_filter_range):
            max_value = str(max_value)
            if last_value == None:
                label = '&lt; ' + max_value
                range = {'%s__lt' % f.name: max_value}
            else:
                label = last_value + ' - ' + max_value
                range = {'%s__gte' % self.field.name: last_value, '%s__lt' % f.name: max_value}
            self.links.append((_(mark_safe(label)), range))
            last_value = max_value
        self.links.append((_(mark_safe('&ge; ' + max_value)), {'%s__gte' % f.name: max_value}))

    def choices(self, cl):
        for title, param_dict in self.links:
            yield {'selected': self.parsed_params == param_dict,
                   'query_string': cl.get_query_string(param_dict, [self.field_generic]),
                   'display': title}

FilterSpec.filter_specs.insert(-1, (lambda f: hasattr(f, 'list_filter_range'),
                                    RangeValuesFilterSpec))

class TipoServicoFilterSpec(ChoicesFilterSpec):
    """
    Usage:

      tipo_servico_field.ts_filter = True

    On Django 1.3 you will can specify a lookup on admin filters. Example:

      list_filter = ('municipio__uf',)

    """

    def __init__(self, f, request, params, model, model_admin):
        super(TipoServicoFilterSpec, self).__init__(f, request, params, model,
                                                    model_admin)
        self.lookup_kwarg = 'servico__tipo_servico__id__exact'
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = TipoServico.objects.all().order_by('nome')
        
    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val.id) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val.id}),
                    'display': val.nome}
        
        
    def title(self):
        return _('Tipo de servico')

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'ts_filter', False),
                             TipoServicoFilterSpec))

class CasaProjetoFilterSpec(ChoicesFilterSpec):
    """
    For usage with CasaLegislativa model:

      any_field.projeto_filter = True

    On Django 1.3 you will can specify a lookup on admin filters. Example:

      list_filter = ('convenio_set',)

    """

    def __init__(self, f, request, params, model, model_admin):
        super(CasaProjetoFilterSpec, self).__init__(f, request, params, model,
                                                    model_admin)
        self.lookup_kwarg = 'convenio__projeto__id__exact'
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
        self.lookup_choices = Projeto.objects.all().order_by('sigla')
        
    def choices(self, cl):
        yield {'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
        for val in self.lookup_choices:
            yield {'selected': smart_unicode(val.id) == self.lookup_val,
                    'query_string': cl.get_query_string({self.lookup_kwarg: val.id}),
                    'display': val.sigla}
        
    def title(self):
        return _('Projeto')

# registering the filter
FilterSpec.filter_specs.insert(0, (lambda f: getattr(f, 'projeto_filter', False),
                             CasaProjetoFilterSpec))
