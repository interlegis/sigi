# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils import simplejson
from django.db.models import Q
from sigi.apps.servicos.models import CasaAtendida

def municipios_atendidos(self, servico):
    municipios = []
    servico = servico.upper()
    
    query = Q()
    
    if servico != 'ALL':
        for sigla in servico.split('_'):
            query = query | Q(tipo_servico__sigla=sigla)
            
    query = Q(data_desativacao=None) & query
    
    for casa in CasaAtendida.objects.all():
        if casa.servico_set.filter(query).exists():
            m = casa.municipio
            municipio = {'nome': casa.nome + ', ' + m.uf.sigla,
                         'lat': str(m.latitude),
                         'lng': str(m.longitude),
                         'servicos': "<ul><li>" + "</li><li>".join([s.tipo_servico.nome for s in casa.servico_set.filter(query)]) + "</li></ul>",}
            municipios.append(municipio)

    return HttpResponse(simplejson.dumps(municipios), mimetype="application/json")