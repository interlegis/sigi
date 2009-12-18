# -*- coding: utf-8 -*-
import reporting
from reportlab.lib.units import cm
from geraldo import Report, ReportBand, Label, ObjectValue
from sigi.apps.casas.models import CasaLegislativa

class CasasLegislativasLabels(Report):
    """
    Usage example::

      >>> from geraldo.generators import PDFGenerator
      >>> queryset = CasaLegislativa.objects.filter(municipio__uf__sigla='MG')
      >>> report = LabelsReport(queryset)
      >>> report.generate_by(PDFGenerator, filename='./inline-detail-report.pdf')

    """

    class band_detail(ReportBand):
        width  = 9.40*cm
        height = 4.60*cm

        # With this attribute as True, the band will try to align in
        # the same line.
        display_inline = True

        elements = [
            Label(text='A Sua Excelência o(a) Senhor(a)', top=0, left=0),
            ObjectValue(
                attribute_name='get_presidente_nome',
                top=0.5*cm, left=0, width=9.00*cm,
                get_value=lambda obj: obj.get_presidente_nome(),
            ),
            ObjectValue(attribute_name='nome', top=1.0*cm, left=0, width=9.00*cm),
            ObjectValue(attribute_name='logradouro', top=1.5*cm, left=0, width=9.00*cm),
            ObjectValue(attribute_name='bairro', top=2*cm, left=0, width=9.00*cm),
            ObjectValue(attribute_name='municipio', top=2.5*cm, left=0, width=9.00*cm),
            ObjectValue(attribute_name='cep', top=3*cm, left=0, width=9.00*cm),
        ]
