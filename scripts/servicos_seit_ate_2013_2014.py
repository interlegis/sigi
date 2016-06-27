from datetime import date

from django.db.models import Q

from sigi.apps.servicos.models import TipoServico

anos = range(2006, 2016)

print '\t'.join(map(str, ['tipo'] + anos))


def prim_jan_ano_seguinte(ano):
    return date(ano + 1, 1, 1)


for tipo_servico in TipoServico.objects.all():
    print '\t'.join(map(str,
                        [tipo_servico] +
                        [tipo_servico.servico_set.filter(
                            Q(data_ativacao__lt=prim_jan_ano_seguinte(ano)),
                            Q(data_desativacao=None) | Q(data_desativacao__gte=prim_jan_ano_seguinte(ano))
                        ).count() for ano in anos]
                        ))
