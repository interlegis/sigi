import codecs
import cStringIO
import csv

from sigi.apps.servicos.models import Servico, TipoServico

# cria um CSV com contatos das casas legislativas que possuem portal modelo ativo
# rodar em um shell:
#     ./manage.py shell
#     %run scripts/contatos_de_casas_que_usam_portalmodelo.py
#     ... verificar <ARQUIVO_CSV>

ARQUIVO_CSV = '/tmp/casas_que_usam_LEGBR_ou_PM.csv'


class UnicodeWriter:

    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.

    from https://docs.python.org/2/library/csv.html
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def clean(self, cell):
        return unicode(cell) if cell else '-'

    def writerow(self, row):
        self.writer.writerow([self.clean(s).encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


pm = TipoServico.objects.get(sigla=u'PM')
leg = TipoServico.objects.get(sigla=u'LEGBR')
servicos = Servico.objects.filter(tipo_servico__in=[pm, leg], data_desativacao__isnull=True)

casas = {s.casa_legislativa for s in servicos}

with open(ARQUIVO_CSV, "wb") as f:
    writer = UnicodeWriter(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow([
        "casa: UF", "casa: NOME",
    ])
    for casa in casas:
        writer.writerow([
            casa.municipio.uf, casa.nome,
        ])
