#-*- coding:utf-8 -*-
import os

from django.templatetags.static import static
from django.utils.translation import ugettext as _
from geraldo import (BAND_WIDTH, FIELD_ACTION_COUNT, DetailBand, Label, Line,
                     ObjectValue, Report, ReportBand, SystemField)
from geraldo.graphics import Image
from reportlab.lib.colors import navy
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm


class ReportDefault(Report):
    #__metaclass__ = ABCMeta
    title = _(u'Relatório')
    author = _(u'Interlegis')
    print_if_empty = True
    page_size = A4

    class band_page_header(ReportBand):
        height = 4.2 * cm
        label_top = 3.7 * cm
        default_style = {'fontName': 'Helvetica', 'fontSize': 9}

        BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '../../../../')
        #BASE_DIR = os.path.abspath(os.getcwd() + '../..')

        elements = [
            Image(filename=BASE_DIR + static('img/logo-interlegis.jpg'),
                  left=15.5 * cm, right=1 * cm, top=0.1 * cm, bottom=1 * cm,
                  width=4.2 * cm, height=3 * cm,
                  ),
            Image(filename=BASE_DIR + static('img/logo-senado.png'),
                  left=1 * cm, right=1 * cm, top=0.1 * cm, bottom=1 * cm,
                  width=3 * cm, height=3 * cm,
                  ),
            Label(text=_(u"SENADO FEDERAL"), top=1 * cm, left=0, width=BAND_WIDTH,
                  style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}
                  ),
            Label(text=_(u"SINTER - Secretaria Especial do Interlegis"), top=1.5 * cm, left=0, width=BAND_WIDTH,
                  style={'fontName': 'Helvetica-Bold', 'fontSize': 13, 'alignment': TA_CENTER}
                  ),
            SystemField(
                expression='%(report_title)s', top=2.5 * cm, left=0, width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}
            ),
        ]
        borders = {'bottom': True}

    class band_page_footer(ReportBand):
        height = 1 * cm

        elements = [
            SystemField(expression=_(u'%(now:%d/%m/%Y)s às %(now:%H:%M)s'), top=0.3 * cm),
            SystemField(expression=_(u'Página %(page_number)d de %(page_count)d'), top=0.3 * cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}
                        ),
        ]
        #borders = {'top': True}

    class band_detail(DetailBand):
        height = 0.5 * cm
        default_style = {'fontName': 'Helvetica', 'fontSize': 8}
        auto_expand_height = True

    class band_summary(ReportBand):
        height = 0.8 * cm
        elements = [
            Label(text=_(u"Total") + ":", top=0.1 * cm, left=0),
            ObjectValue(attribute_name='id', top=0.1 * cm, left=1 * cm,
                        action=FIELD_ACTION_COUNT, display_format='%s'),
        ]
        borders = {'top': Line(stroke_color=navy, stroke_width=2)}
