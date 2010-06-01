from sigi.apps.casas.models import CasaLegislativa
from sigi.apps.convenios.models import Convenio, Projeto

def charts_data(request):
    casas = CasaLegislativa.objects.all()
    convenios = Convenio.objects.all()
    projetos = Projeto.objects.all()

    convenios_firmados = convenios.exclude(data_retorno_assinatura=None)

    num_convenios_firmados = convenios_firmados.count()
    num_convenios_nao_firmados = convenios.filter(data_retorno_assinatura=None).count()
    num_casas_nao_aderidas = casas.count() - convenios.exclude(data_adesao=None).count()

    # Verifica quantidade de convenios por projeto
    convenios_por_projeto = []
    for p in projetos:
        convenios_por_projeto.append(convenios_firmados.filter(projeto=p).count())
    
    num_casas_regiao = [
        casas.filter(municipio__uf__regiao='CO').count(),
        casas.filter(municipio__uf__regiao='NO').count(),
        casas.filter(municipio__uf__regiao='NE').count(),
        casas.filter(municipio__uf__regiao='SD').count(),
        casas.filter(municipio__uf__regiao='SL').count()
    ]
    num_convenios_firmados_regiao = [
        convenios_firmados.filter(casa_legislativa__municipio__uf__regiao='CO').count(),
        convenios_firmados.filter(casa_legislativa__municipio__uf__regiao='NO').count(),
        convenios_firmados.filter(casa_legislativa__municipio__uf__regiao='NE').count(),
        convenios_firmados.filter(casa_legislativa__municipio__uf__regiao='SD').count(),
        convenios_firmados.filter(casa_legislativa__municipio__uf__regiao='SL').count()
    ]
    
    # Verifica qual regiao tem mais convenios e guarda valor para "axis" do grafico de regioes
    num_regiao_maior = 0
    for i in num_casas_regiao:
        if num_regiao_maior<i:
            num_regiao_maior = i

    equip_n_recebidos = convenios.filter(data_termo_aceite=None).count()
    equip_recebidos = convenios.exclude(data_termo_aceite=None).count()

    return {
        'regioes_chart_data': [num_convenios_firmados_regiao, num_casas_regiao],
        'convenios_chart_data': [num_convenios_firmados, num_convenios_nao_firmados,
                                 num_casas_nao_aderidas],
        'equipamentos_chart_data': [equip_recebidos, equip_n_recebidos],
        'projetos_chart_data': projetos,
        'convenios_por_projeto_chart_data': convenios_por_projeto,
        'num_regiao_maior_chart_data': num_regiao_maior,
    }
