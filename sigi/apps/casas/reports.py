# -*- coding: utf-8 -*-
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from geraldo import Report, DetailBand, Label, ObjectValue, ManyElements, \
                    ReportGroup, ReportBand

from sigi.apps.relatorios.reports import ReportDefault

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

class CasasLegislativasReport(ReportDefault):
    title = u'Relatório de Casas Legislativas'

    class band_page_header(ReportDefault.band_page_header):

        label_top = ReportDefault.band_page_header.label_top
        label_left = [0.3,1,5.5,6.5,12]
        elements = list(ReportDefault.band_page_header.elements)

        elements += [
            Label(
                text="UF",
                left=label_left[0]*cm,
                top=label_top
            ),
            Label(
                text="Municipio",
                left=label_left[1]*cm,
                top=label_top
            ),
            Label(
                text="Tipo",
                left=label_left[2]*cm,
                top=label_top
            ),
            Label(
                text="Presidente",
                left=label_left[3]*cm,
                top=label_top
            ),
            Label(
                text="Logradouro",
                left=label_left[4]*cm,
                top=label_top
            ),
            
        ]



    class band_page_footer(ReportDefault.band_page_footer):
        pass

    class band_detail(ReportDefault.band_detail):

        label_left = [0.3,1,5.5,6.5,12]

        elements=[
            ObjectValue(
                attribute_name='municipio.uf.sigla',
                left=label_left[0]*cm
            ),
            ObjectValue(
                attribute_name='municipio.nome',
                left=label_left[1]*cm
            ),
            ObjectValue(
                attribute_name='tipo',
                left=label_left[2]*cm
            ),
            ObjectValue(
                attribute_name='parlamentar',
                left=label_left[3]*cm
            ),
            ObjectValue(
                attribute_name='logradouro',
                left=label_left[4]*cm,
            ),
        ]

    groups = [
        ReportGroup(attribute_name='municipio.uf',
            band_header=ReportBand(
                height=0.7*cm,
                elements= [
                    ObjectValue(attribute_name='municipio.uf')
                ],
                borders={'top': True},
            )
        )
    ]