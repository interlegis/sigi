# -*- coding: utf-8 -*-
import csv
from datetime import datetime
import json as simplejson  # XXX trocar isso por simplesmente import json e refatorar o codigo
import os
import time
from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext
from django.utils.datastructures import SortedDict
from django.utils.translation import gettext as _
from django.views.decorators.cache import cache_page
from easy_thumbnails.templatetags.thumbnail import thumbnail_url

from sigi.apps.casas.models import Orgao, TipoOrgao
from sigi.apps.contatos.models import UnidadeFederativa
from sigi.apps.convenios.models import Convenio, Projeto
from sigi.apps.financeiro.models import Desembolso
from sigi.apps.servicos.models import TipoServico
from sigi.apps.utils import to_ascii
from sigi.settings import MEDIA_ROOT, STATIC_URL
from sigi.shortcuts import render_to_pdf
from sigi.apps.servidores.models import Servidor


JSON_FILE_NAME = os.path.join(MEDIA_ROOT, 'apps/metas/map_data.json')


@login_required
def dashboard(request):
    if request.user.groups.filter(name__in=['SPDT-Servidores', 'SSPLF']).count() <= 0:
        raise PermissionDenied

    desembolsos_max = 0
    matriz = SortedDict()
    dados = SortedDict()
    projetos = Projeto.objects.all()
    meses = Desembolso.objects.dates('data', 'month', 'DESC')[:6]
    colors = ['ffff00', 'cc7900', 'ff0000', '92d050', '006600', '0097cc', '002776', 'ae78d6', 'ff00ff', '430080',
              '28d75c', '0000ff', 'fff200']

    for date in reversed(meses):
        mes_ano = '%s/%s' % (date.month, date.year)
        dados[mes_ano] = 0

    for p in projetos:
        matriz[p.id] = (p.sigla, dados.copy())

    for date in meses:
        mes_ano = '%s/%s' % (date.month, date.year)
        for d in Desembolso.objects.filter(data__year=date.year, data__month=date.month).values('projeto').annotate(total_dolar=Sum('valor_dolar')):
            if int(d['total_dolar']) > desembolsos_max:
                desembolsos_max = int(d['total_dolar'])
            matriz[d['projeto']][1][mes_ano] += int(d['total_dolar'])

    meses = ["%s/%s" % (m.month, m.year) for m in reversed(meses)]
    extra_context = {'desembolsos': matriz, 'desembolsos_max': desembolsos_max, 'meses': meses, 'colors': ','.join(colors[:len(matriz)])}
    return render_to_response('metas/dashboard.html', extra_context, context_instance=RequestContext(request))

def openmap(request):
    reptype = request.GET.get('reptype', None)

    if reptype is None:
        context = {
            'tipos_orgao': TipoOrgao.objects.filter(legislativo=True),
            'tipos_servico': TipoServico.objects.all(),
            'tipos_convenio': Projeto.objects.all(),
            'gerentes': Servidor.objects.exclude(casas_que_gerencia=None),
            'regioes': [(s, n, UnidadeFederativa.objects.filter(regiao=s))
                        for s, n in UnidadeFederativa.REGIAO_CHOICES],
        }
        return render(request, 'metas/openmap.html', context)
    else:
        tipos_orgao = request.GET.getlist('tipo_orgao', [])
        tipos_servico = request.GET.getlist('tipo_servico', [])
        tipos_convenio = request.GET.getlist('tipo_convenio', [])
        gerentes = request.GET.getlist('gerente', [])
        ufs = request.GET.getlist('uf', [])
        casas = openmapdata(request)

        context = {
            'tipos_orgao': TipoOrgao.objects.filter(legislativo=True,
                                                    sigla__in=tipos_orgao),
            'tipos_servico': TipoServico.objects.filter(
                sigla__in=tipos_servico
            ),
            'tipos_convenio': Projeto.objects.filter(sigla__in=tipos_convenio),
            'gerentes': Servidor.objects.exclude(
                casas_que_gerencia=None).filter(id__in=gerentes),
            'ufs': UnidadeFederativa.objects.filter(sigla__in=ufs),
            'casas': casas
        }

        if reptype == "lista":
            return render_to_pdf("metas/lista_casas.html", context)
        else:
            fieldnames = ['cnpj', 'nome', 'uf', 'regiao', 'endereco', 'bairro',
                         'cep', 'ult_alt_endereco', 'presidente',
                         'ult_atualizacao_presidente', 'telefone_presidente',
                         'email_presidente', 'telefones', 'emails', 'contatos',
                         'convenios', 'servicos']
            response = HttpResponse(content_type='text/csv')
            writer = csv.DictWriter(response, fieldnames=fieldnames)
            writer.writeheader()
            for casa in casas:
                row = {
                    'cnpj': casa.cnpj.encode('utf8'),
                    'nome': casa.nome.encode('utf8'),
                    'uf': casa.municipio.uf.nome.encode('utf8'),
                    'regiao':
                        casa.municipio.uf.get_regiao_display().encode('utf8'),
                    'endereco': casa.logradouro.encode('utf8'),
                    'bairro': casa.bairro.encode('utf8'),
                    'cep': casa.cep.encode('utf8'),
                    'ult_alt_endereco': (casa.ult_alt_endereco.strftime(
                        "%d/%m/%Y").encode('utf8')
                                         if casa.ult_alt_endereco else ""),
                    'telefones': u", ".join(casa.telefones.values_list('numero',
                                                                      flat=True)
                                           ).encode('utf8'),
                    'emails': u", ".join([casa.email] + list(
                        casa.funcionario_set.values_list('email',flat=True))
                                        ).encode('utf8'),
                    'contatos': u", ".join(casa.funcionario_set.values_list(
                        'nome', flat=True)).encode('utf8'),
                    'convenios': u", ".join([c.__unicode__() for c in
                                            casa.convenio_set.all()]
                                           ).encode('utf8'),
                    'servicos': u", ".join([u"{tipo} ({url})".format(
                        tipo=s.tipo_servico.nome, url=s.url)
                                           for s in casa.servico_set.all()]
                                          ).encode('utf8')
                }
                if casa.presidente:
                    row['presidente'] = casa.presidente.nome.encode('utf8')
                    row['ult_atualizacao_presidente'] = (
                        casa.presidente.ult_alteracao.strftime("%d/%m/%Y")
                        if casa.presidente.ult_alteracao else "")
                    row['telefone_presidente'] = casa.presidente.nota.encode(
                        'utf8') if  casa.presidente.nota else ""
                    row['email_presidente'] = casa.presidente.email.encode(
                        'utf8')
                writer.writerow(row)

            return response

def openmapdata(request):
    tipos_orgao = request.GET.getlist('tipo_orgao', None)
    tipos_servico = request.GET.getlist('tipo_servico', None)
    tipos_convenio = request.GET.getlist('tipo_convenio', None)
    ufs = request.GET.getlist('uf', None)
    gerentes = request.GET.getlist('gerente', None)
    reptype = request.GET.get('reptype', None)

    dados = Orgao.objects.all()

    if tipos_orgao:
        dados = dados.filter(tipo__sigla__in=tipos_orgao)
    else:
        dados = dados.filter(tipo__legislativo=True)

    if tipos_servico:
        if "none" in tipos_servico:
            dados = dados.filter(servico=None)
        else:
            dados = dados.filter(servico__tipo_servico__sigla__in=tipos_servico,
                                 servico__data_desativacao=None)

    if tipos_convenio:
        if "none" in tipos_convenio:
            dados = dados.filter(convenio=None)
        else:
            dados = dados.filter(convenio__projeto__sigla__in=tipos_convenio)

    if ufs:
        dados = dados.filter(municipio__uf__sigla__in=ufs)

    if gerentes:
        if "none" in gerentes:
            dados = dados.filter(gerentes_interlegis=None)
        else:
            dados = dados.filter(gerentes_interlegis__id__in=gerentes)


    if not reptype:
        dados = dados.order_by('nome', 'id').distinct('nome', 'id')
        dados = dados.values_list("id", "nome", "municipio__latitude",
                                  "municipio__longitude")
        return JsonResponse(list(dados), safe=False)
    else:
        dados = dados.order_by(
            'municipio__uf__regiao',
            'municipio__uf__nome',
            'nome',
            'id'
        ).distinct(
            'municipio__uf__regiao',
            'municipio__uf__nome',
            'nome',
            'id'
        ).prefetch_related(
            'servico_set',
            'convenio_set',
            'municipio__uf',
            'gerentes_interlegis'
        )
        return dados

def openmapdetail(request, orgao_id):
    orgao = get_object_or_404(Orgao, id=orgao_id)
    return render(request, "metas/openmapdetail.html", {'orgao': orgao})

def openmapsearch(request):
    q = request.GET.get('q', '')
    if len(q) < 3:
        return JsonResponse({'result': 'unsearchable'})

    dados = Orgao.objects.filter(
        tipo__legislativo=True,
        search_text__icontains=to_ascii(q)
    )[:10]
    dados = dados.values("id", "nome", "municipio__latitude",
                         "municipio__longitude")
    dados = [{'id': d['id'],
              'label': d['nome'],
              'lat': d['municipio__latitude'],
              'lng': d['municipio__longitude']} for d in dados]
    return JsonResponse(list(dados), safe=False)
