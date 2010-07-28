# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from geraldo import Report, DetailBand, Label, ObjectValue, ManyElements

class CasasLegislativasLabels(Report):
    """
    Usage example::

      >>> from geraldo.generators import PDFGenerator
      >>> queryset = CasaLegislativa.objects.filter(municipio__uf__sigla='MG')
      >>> report = LabelsReport(queryset)
      >>> report.generate_by(PDFGenerator, filename='./inline-detail-report.pdf')

    """

    page_size = A4
    margin_top = 0.8*cm
    margin_bottom = 0.8*cm
    margin_left = 0.4*cm
    margin_right = 0.4*cm

    class band_detail(DetailBand):
        width  = 9.9*cm
        height = 5.6*cm
        margin_bottom = 0.0*cm
        margin_right  = 0.3*cm

        # With this attribute as True, the band will try to align in
        # the same line.
        display_inline = True

        default_style = {'fontName': 'Helvetica', 'fontSize': 11}

        elements = [
            Label(
                text='A Sua Excelência o(a) Senhor(a)',
                top=1*cm, left=1*cm, width=9.4*cm,
            ),
            ManyElements(
                ObjectValue,
                count=5,
                attribute_name=('get_presidente_nome','nome','logradouro','municipio','cep'),
                start_top=1.5*cm, height=0.5*cm, left=1*cm, width=9.4*cm,
            ),
        ]
