from csv_writer import CsvWriter
from sigi.apps.servicos.models import Servico

ARQUIVO_CSV = '/tmp/casas_que_usam_PM_e_SAPL.csv'


def escrever_casas(casas, arquivo):
    with open(arquivo, "wb") as f:
        writer = CsvWriter(f)
        writer.writerow([
            "casa: sigla UF", "casa: nome UF", "casa: NOME",
        ])
        for casa in casas:
            writer.writerow([
                casa.municipio.uf.sigla, casa.municipio.uf, casa.nome,
            ])

casas_pm = {s.casa_legislativa for s in Servico.objects.filter(tipo_servico__sigla='PM', data_desativacao__isnull=True)}
casas_sapl = {s.casa_legislativa for s in Servico.objects.filter(tipo_servico__sigla='SAPL', data_desativacao__isnull=True)}
casas_ativas = casas_pm & casas_sapl
escrever_casas(casas_ativas, '/tmp/casas_que_usam_PM_e_SAPL__AMBOS_ATIVOS.csv')

casas_pm = {s.casa_legislativa for s in Servico.objects.filter(tipo_servico__sigla='PM')}
casas_sapl = {s.casa_legislativa for s in Servico.objects.filter(tipo_servico__sigla='SAPL')}
casas_todas = casas_pm & casas_sapl
escrever_casas(casas_todas, '/tmp/casas_que_usam_PM_e_SAPL__TODOS.csv')


casas = casas_pm.union(casas_sapl)
escrever_casas(casas, '/tmp/casas_que_usam_PM_ou_SAPL.csv')


casas_algum_inativo = casas_todas
