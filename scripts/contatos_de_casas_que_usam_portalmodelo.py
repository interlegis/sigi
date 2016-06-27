import codecs
import cStringIO
import csv

from sigi.apps.casas.models import Funcionario
from sigi.apps.contatos.models import Telefone
from sigi.apps.servicos.models import Servico, TipoServico

# cria um CSV com contatos das casas legislativas que possuem portal modelo ativo
# rodar em um shell:
#     ./manage.py shell
#     %run scripts/contatos_de_casas_que_usam_portalmodelo.py
#     ... verificar <ARQUIVO_CSV>

ARQUIVO_CSV = '/tmp/contatos_casas_pm.csv'


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


pm = TipoServico.objects.get(nome=u'Portal Modelo')
servicos = Servico.objects.filter(tipo_servico=pm, data_desativacao__isnull=True)
casas = {s.casa_legislativa for s in servicos}

tipos_telefone = dict(Telefone.TELEFONE_CHOICES)
setores_funcionarios = dict(Funcionario.SETOR_CHOICES)

with open(ARQUIVO_CSV, "wb") as f:
    writer = UnicodeWriter(f, delimiter='\t', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow([
        "casa: ID", "casa: NOME",
        "contato: NOME", "contato: TIPO",
        "contato: EMAIL", "contato: CARGO", "contato: FUNCAO", "contato: TELEFONES",
    ])
    for casa in casas:
        contatos = casa.funcionario_set.filter(setor__in=["contato_interlegis", "estrutura_de_ti"])
        if not contatos:
            contatos = casa.funcionario_set.all()
        for contato in contatos:
            writer.writerow([
                casa.pk, casa.nome,
                contato.nome, setores_funcionarios.get(contato.setor, '?').decode('utf-8'),
                contato.email, contato.cargo, contato.funcao,
                '; '.join('%s [tipo: %s]' % (t.numero, tipos_telefone.get(t.tipo)) for t in contato.telefones.all()),
            ])
        if not contatos:
            writer.writerow([
                casa.pk, casa.nome,
                'SEM CONTATOS CADASTRADOS',
            ])
