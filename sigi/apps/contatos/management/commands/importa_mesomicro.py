import csv
import os
from django.core.management.base import BaseCommand, CommandError, CommandParser
from sigi.apps.contatos.models import (Municipio, UnidadeFederativa,
                                       Mesorregiao, Microrregiao)

class Command(BaseCommand):
    help = """
Importa arquivo do IBGE para preencher as tabelas de meso e microrregiões para
os municípios. A primeira linha do arquivo deve possuir um cabeçalho com os
seguintes campos obrigatórios (Os nomes dos campos devem ser grafados exatamente
como descrito):
"cod_uf" (Código IBGE da Unidade da Federação),
"cod_mesorregiao" (Código IBGE da mesorregião),
"nome_mesorregiao" (Nome da mesorregião),
"cod_microrregiao" (Código IBGE da microrregião),
"nome_microrregiao" (Nome da microrregião),
"cod_municipio" (Código IBGE do município\n)
    """

    campos = {'cod_uf', 'cod_mesorregiao', 'nome_mesorregiao',
              'cod_microrregiao', 'nome_microrregiao', 'cod_municipio'}

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('file_name', type=str,
                            help="Arquivo CSV a ser importado")

    def handle(self, *args, **options):
        file_name = options['file_name']

        if not os.path.isfile(file_name):
            raise CommandError("Arquivo %s não encontrado" % file_name)

        with open(file_name, 'rt') as csvfile:
            reader = csv.DictReader(csvfile)

            if not self.campos.issubset(reader.fieldnames):
                raise CommandError(
                    "O arquivo não possui todos os campos obrigatórios"
                )

            erros = 0

            for reg in reader:
                try:
                    uf = UnidadeFederativa.objects.get(
                        codigo_ibge=reg['cod_uf']
                    )
                except UnidadeFederativa.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        "(Linha %s): não existe UF com código IBGE '%s'" %
                        (reader.line_num, reg['cod_uf'])
                    ))
                    erros = erros + 1
                    continue

                try:
                    municipio = Municipio.objects.get(
                        codigo_ibge=reg['cod_municipio']
                    )
                except Municipio.DoesNotExist:
                    self.stdout.write(self.style.ERROR(
                        "(Linha %s): não existe Município com código IBGE '%s'"
                        % (reader.line_num, reg['cod_municipio'])
                    ))
                    erros = erros + 1
                    continue

                cod_meso = reg['cod_uf'] + reg['cod_mesorregiao']
                cod_micro = cod_meso + reg['cod_microrregiao']

                meso, _ = Mesorregiao.objects.get_or_create(
                    codigo_ibge=cod_meso,
                    defaults={
                        'uf': uf,
                        'nome': reg['nome_mesorregiao']
                    }
                )
                meso.save()

                micro, _ = Microrregiao.objects.get_or_create(
                    codigo_ibge=cod_micro,
                    defaults={
                        'mesorregiao': meso,
                        'nome': reg['nome_microrregiao']
                    }
                )
                micro.save()

                municipio.microrregiao = micro
                municipio.save()

            self.stdout.write(self.style.NOTICE(
                "Importação concluída. %s erros em %s linhas" %
                (erros, reader.line_num)
            ))