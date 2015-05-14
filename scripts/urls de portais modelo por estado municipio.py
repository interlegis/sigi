from sigi.apps.servicos.models import TipoServico

pm = TipoServico.objects.first()
res = sorted([(p.casa_legislativa.municipio.uf, p.casa_legislativa.municipio.nome, p.url) for p in pm.servico_set.all()])

with open('/tmp/pm.csv', 'w+') as f:
    for uf, cid, url in res:
        f.write(('%s,%s,%s' % (uf.nome, cid, url) + '\n').encode('utf-8'))
