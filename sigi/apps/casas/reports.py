# -*- coding: utf-8 -*-
from geraldo import Report, DetailBand, Label, ObjectValue, ReportGroup, ReportBand, landscape, SubReport, BAND_WIDTH, SystemField
from geraldo.graphics import Image

from django.templatetags.static import static
from django.utils.translation import ugettext as _
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from sigi.apps.relatorios.reports import ReportDefault


def string_to_cm(texto):
    tamanho = 0
    minEspeciais = {
        'f': 0.1,
        'i': 0.05,
        'j': 0.05,
        'l': 0.05,
        'm': 0.2,
        'r': 0.1,
        't': 0.15,
    }
    maiuEspeciais = {
        'I': 0.05,
        'J': 0.15,
        'L': 0.15,
        'P': 0.15,
    }
    for c in texto:
        if c > 'a' and c < 'z':
            if c in minEspeciais:
                tamanho += minEspeciais[c]
            else:
                tamanho += 0.17
        else:
            if c in maiuEspeciais:
                tamanho += maiuEspeciais[c]
            else:
                tamanho += 0.2
    return tamanho


def label_text(text):
    return "%s: " % text


class CasasLegislativasLabels(Report):

    """
    Usage example::

      >>> from geraldo.generators import PDFGenerator
      >>> queryset = CasaLegislativa.objects.filter(municipio__uf__sigla='MG')
      >>> report = LabelsReport(queryset)
      >>> report.generate_by(PDFGenerator, filename='./inline-detail-report.pdf')

    """
    formato = ''
    label_margin_top = 0.6
    label_margin_left = 0.2
    label_margin_right = 0.2
    largura_etiqueta = 6.9
    altura_etiqueta = 3.25
    tamanho_fonte = 6
    delta = start = 0.5

    def __init__(self, queryset, formato):
        super(CasasLegislativasLabels, self).__init__(queryset=queryset)
        self.formato = formato
        self.page_size = A4

        if formato == '3x9_etiqueta':
            self.margin_top = 0.25 * cm
            self.margin_bottom = 0.0 * cm
            self.margin_left = 0.2 * cm
            self.margin_right = 0.0 * cm
            self.delta = 0.3
            self.start = 0
            self.label_margin_top = 0.35
            self.label_margin_left = 0.4
            self.label_margin_right = 0.2
        else:
            self.margin_top = 0.8 * cm
            self.margin_bottom = 0.8 * cm
            self.margin_left = 0.4 * cm
            self.margin_right = 0.4 * cm
            self.largura_etiqueta = 9.9
            self.altura_etiqueta = 5.6
            self.tamanho_fonte = 11
            self.label_margin_top = 0.5
            self.label_margin_left = 0.5
            self.label_margin_right = 0.5

        calc_width = (self.largura_etiqueta - self.label_margin_left - self.label_margin_right) * cm
        calc_height = lambda rows: (self.delta * rows) * cm
        calc_top = lambda row: (self.label_margin_top + row * self.delta) * cm
        calc_left = self.label_margin_left * cm

        my_elements = [
            Label(
                text=label_text(_(u'A Sua Excelência o(a) Senhor(a)')),
                top=calc_top(0), left=calc_left, width=calc_width,
            ),
            ObjectValue(
                attribute_name='presidente',
                top=calc_top(1), left=calc_left, width=calc_width,
                get_value=lambda instance:
                    unicode(instance.presidente or "").upper()
            ),
            ObjectValue(
                attribute_name='nome',
                top=calc_top(2), left=calc_left, width=calc_width, height=calc_height(2),
                get_value=lambda instance:
                    (_(u"Presidente da %s") % instance.nome)
            ),
            ObjectValue(
                attribute_name='logradouro',
                top=calc_top(4), left=calc_left, width=calc_width, height=calc_height(2),
                get_value=lambda instance:
                    "%s - %s - %s." % (instance.logradouro, instance.bairro, instance.municipio),
            ),

            ObjectValue(
                attribute_name='cep',
                top=calc_top(8), left=calc_left, width=calc_width,
                get_value=lambda instance: "%s: %s" % (_(u"CEP"), instance.cep)
            ),
        ]
        self.band_detail = DetailBand(
            width=(self.largura_etiqueta) * cm,
            height=(self.altura_etiqueta) * cm,
            elements=my_elements,
            display_inline=True,
            default_style={'fontName': 'Helvetica', 'fontSize': self.tamanho_fonte})


class CasasLegislativasLabelsSemPresidente(CasasLegislativasLabels):

    def __init__(self, queryset, formato):
        super(CasasLegislativasLabelsSemPresidente, self).__init__(queryset=queryset, formato=formato)

        calc_width = (self.largura_etiqueta - self.label_margin_left - self.label_margin_right) * cm
        calc_height = lambda rows: (self.delta * rows) * cm
        calc_top = lambda row: (self.label_margin_top + row * self.delta) * cm
        calc_left = self.label_margin_left * cm

        my_elements = [
            Label(
                text=label_text(_(u'A Sua Excelência o(a) Senhor(a)')),
                top=calc_top(0), left=calc_left, width=calc_width,
            ),
            ObjectValue(
                attribute_name='nome',
                top=calc_top(1), left=calc_left, width=calc_width, height=calc_height(2),
                get_value=lambda instance:
                    (_(u"Presidente da %s") % instance.nome)
            ),
            ObjectValue(
                attribute_name='logradouro',
                top=calc_top(3), left=calc_left, width=calc_width, height=calc_height(2),
                get_value=lambda instance:
                    "%s - %s - %s." % (instance.logradouro, instance.bairro, instance.municipio),
            ),

            ObjectValue(
                attribute_name='cep',
                top=calc_top(8), left=calc_left, width=calc_width,
                get_value=lambda instance: "%s: %s" % (_(u"CEP"), instance.cep)
            ),
        ]
        self.band_detail = DetailBand(
            width=(self.largura_etiqueta) * cm,
            height=(self.altura_etiqueta) * cm,
            elements=my_elements,
            display_inline=True,
            default_style={'fontName': 'Helvetica', 'fontSize': self.tamanho_fonte})

