#-*- coding:utf-8 -*-
from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.convenios.models import Convenio, Projeto
from sigi.apps.contatos.models import UnidadeFederativa

def charts_data(request):
    '''
        Busca informacoes para a criacao dos graficos e resumos
    '''

    projetos = Projeto.objects.all()
    convenios = Convenio.objects.all()
    convenios_assinados = convenios.exclude(data_retorno_assinatura=None)

    tabela_resumo_camara = busca_informacoes_camara()
    g_conv_proj = grafico_convenio_projeto(convenios)
    g_convassinado_proj = grafico_convenio_projeto(convenios_assinados)

    return {        
        'tabela_resumo_camara' : tabela_resumo_camara,
        'g_conv_proj': g_conv_proj,
        "g_convassinado_proj":g_convassinado_proj,
    }

def busca_informacoes_camara():
    '''
        Busca informacoes no banco para montar tabela de resumo de camaras por projeto
        Retorna um dicionario de listas
    '''
    casas = CasaLegislativa.objects.all()
    camaras = casas.filter(tipo__sigla='CM')
    convenios = Convenio.objects.filter(casa_legislativa__tipo__sigla='CM')
    projetos = Projeto.objects.all()

    convenios_assinados = convenios.exclude(data_retorno_assinatura=None)
    convenios_em_andamento = convenios.filter(data_retorno_assinatura=None)

    camaras_nao_aderidas = camaras.filter(convenio__data_adesao=None)
    camaras_aderidas = camaras.exclude(convenio__data_adesao=None)

    camaras_equipadas = camaras.exclude(convenio__data_termo_aceite=None)

    # Criacao das listas para o resumo de camaras por projeto

    cabecalho_topo = ['','Total'] # Cabecalho superior da tabela

    lista_total = [camaras.count()]
    lista_nao_aderidas =  [camaras_nao_aderidas.count()]
    lista_aderidas = [camaras_aderidas.count()]
    lista_convenios_assinados = [convenios_assinados.count()]
    lista_convenios_em_andamento = [convenios_em_andamento.count()]
    lista_camaras_equipadas = [camaras_equipadas.count()]
    for projeto in projetos:
        cabecalho_topo.append(projeto.sigla)
        lista_total.append(camaras.filter(convenio__projeto=projeto).count())
        lista_nao_aderidas.append(camaras_nao_aderidas.filter(convenio__projeto=projeto).count())
        lista_aderidas.append(camaras_aderidas.filter(convenio__projeto=projeto).count())
        lista_convenios_assinados.append(convenios_assinados.filter(projeto=projeto).count())
        lista_convenios_em_andamento.append(convenios_em_andamento.filter(projeto=projeto).count())
        lista_camaras_equipadas.append(camaras_equipadas.filter(convenio__projeto=projeto).count())

    # Cabecalho da esquerda na tabela
    cabecalho_esquerda = (
        u'Total de câmaras municipais',
        u'Câmaras municipais não aderidas',
        u'Câmaras municipais aderidas',
        u'Câmaras municipais com convênios assinados',
        u'Câmaras municipais convênios em andamento',
        u'Câmaras municipais equipadas'
    )

    linhas = (
        lista_total,
        lista_nao_aderidas,
        lista_aderidas,
        lista_convenios_assinados,
        lista_convenios_em_andamento,
        lista_camaras_equipadas,
    )

    # Unindo as duas listass para que o cabecalho da esquerda fique junto com sua
    # respectiva linha
    lista_zip = zip(cabecalho_esquerda,linhas)

    # Retornando listas em forma de dicionario
    return {
        u'cabecalho_topo': cabecalho_topo,
        u'lista_zip': lista_zip,
        u'linhas' : linhas,
        
    }

def grafico_convenio_projeto(convenios):    
    projetos = Projeto.objects.all()

    lista_convenios = []
    for projeto in projetos:
        lista_convenios.append(convenios.filter(projeto=projeto).count())

    dic = {
        "total_convenios":("Total: " + str(convenios.count())),
        "convenios":lista_convenios,
        "projetos":projetos
    }
    return dic


