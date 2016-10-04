# coding: utf-8
from django.http import HttpResponse,HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from ipware.ip import get_ip

import re
from urlparse import urlparse
from collections import OrderedDict

from sigi.apps.servicos.models import *
from sigi.settings import WHOIS_WHITELIST

class WhitelistPermission(permissions.BasePermission):
    """
    Allow only whitelisted IP addresses
    """

    def has_permission(self, request, view):
        ip_addr = get_ip(request)
        if ip_addr in WHOIS_WHITELIST:
            return True
        else:
            return False

def consulta_valida(consulta):
    """
    Determina se uma consulta é válida. Além de ser um domínio válido, deve terminar em uf.leg.br
    """

    regex_dominio=r'^[a-zA-Z\d]{,63}(\.[a-zA-Z\d-]{,63})*.(ac|al|ap|am|ba|ce|df|es|go|ma|mt|ms|mg|pr|pb|pa|pe|pi|rj|rn|rs|ro|rr|sc|se|sp|to).leg.br$'
    m = re.match(regex_dominio, consulta)
    if m == None:
        return False

    return True

def match_url_dominio(url, dominio):
    """
    Compara o url cadastrado no serviço com o domínio pesquisado.
    """

    url=urlparse(url)
    if url.netloc == dominio:
        return True
    else:
        return False

@api_view(['GET'])
@permission_classes([WhitelistPermission])
def whois_query(request, dominio):
    """
    Consulta a base do SIGI por um domínio e retorna um dicionário.
    """

    if not consulta_valida(dominio):
        return Response({'detail':'406 Not Acceptable'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    servicos = Servico.objects.filter(tipo_servico__sigla='LEGBR', url__contains=dominio)
    resposta_dic = OrderedDict()

    for s in servicos:
        # valida se pegamos o dominio correto, a busca pode retornar mais de
        # um registro. ex. itapemirim.es.leg.br / cachoeirodeitapemirim.es.leg.br
        if not match_url_dominio(s.url, dominio):
            continue

        resposta_dic['_encoding'] = 'utf-8'
        resposta_dic['domain'] = urlparse(s.url).netloc
        resposta_dic['owner'] = "%s - %s " % (s.casa_legislativa.nome, s.casa_legislativa.municipio.uf.sigla)
        resposta_dic['cnpj'] = s.casa_legislativa.cnpj
        resposta_dic['created'] = unicode(s.data_ativacao)
        resposta_dic['modified'] = unicode(s.data_alteracao)
        resposta_dic['tech-name'] = s.contato_tecnico.nome
        resposta_dic['tech-email'] = s.contato_tecnico.email
        resposta_dic['tech-modified'] = unicode(s.contato_tecnico.ult_alteracao)
        resposta_dic['admin-name'] = s.contato_administrativo.nome
        resposta_dic['admin-email'] = s.contato_administrativo.email
        resposta_dic['admin-modified'] = unicode(s.contato_administrativo.ult_alteracao)

    return Response(resposta_dic, status=status.HTTP_200_OK)

