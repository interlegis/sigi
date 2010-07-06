# -*- coding: utf-8 -*-
import os
from ctypes import alignment
from operator import attrgetter
from geraldo import Report, ReportBand, ObjectValue, DetailBand, Label, \
                    landscape,SystemField, BAND_WIDTH,ReportGroup, \
                    FIELD_ACTION_SUM, FIELD_ACTION_COUNT


from geraldo.graphics import Image


from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

#from abc import ABCMeta

class ReportDefault(Report):
    #__metaclass__ = ABCMeta
    title = u'Relatório'
    author = u'Interlegis'
    print_if_empty = True
    page_size = A4

    class band_page_header(ReportBand):
        height = 4.2*cm

        elements = [
            Image(filename=  'apps/convenios/templates/imagens/logo-interlegis.jpg',
                left=15.5*cm,right=1*cm,top=0.1*cm,bottom=1*cm,
                width=4.2*cm,height=3*cm,
            ),
            Image(filename=  'apps/convenios/templates/imagens/logo-senado.png',
                left=1*cm,right=1*cm,top=0.1*cm,bottom=1*cm,
                width=3*cm,height=3*cm,
            ),
            Label(text="SENADO FEDERAL",top=1*cm,left=0,width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold','fontSize':14, 'alignment': TA_CENTER}
            ),
            Label(text="SINTER - Secretaria Especial do Interlegis",top=1.5*cm,left=0,width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold','fontSize':13, 'alignment': TA_CENTER}
            ),
            SystemField(
                expression='%(report_title)s',top=2.5*cm,left=0,width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold','fontSize':14, 'alignment': TA_CENTER}
            ),
        ]
        borders = {'bottom': True}

    class band_page_footer(ReportBand):
        height = 0.5*cm

        elements = [
            SystemField(expression=u'%(now:%d/%m/%Y)s às %(now:%H:%M)s', top=0.1*cm),
            SystemField(expression=u'Página %(page_number)d de %(page_count)d', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}
            ),
        ]
        borders = {'top': True}

    class band_detail(DetailBand):
        height = 0.5*cm



class CasasAderidasReport(object):
    pass

class CasasNaoAderidasReport(object):
    pass

class CasasComEquipamentosReport(object):
    pass

class SemEquipamentosReport(object):
    pass
class ConvenioReport(ReportDefault):
    title = u'Relatório de Convênios'

    class band_page_header(ReportDefault.band_page_header):

        ReportDefault.band_page_header.elements += [
            (Label(text="Estado", left=0.5*cm,top=3.7*cm)),
            (Label(text="Nº Processo", left=3*cm,top=3.7*cm)),
            (Label(text="Nome", left=6*cm,top=3.7*cm)),
            (Label(text="Data Adesão", left=11*cm,top=3.7*cm)),
            (Label(text="Projeto", left=14*cm,top=3.7*cm)),
        ]



    class band_page_footer(ReportDefault.band_page_footer):
        pass

    class band_detail(ReportDefault.band_detail):
        elements=[
            ObjectValue(attribute_name='casa_legislativa.municipio.uf', left=0.5*cm),
            ObjectValue(attribute_name='num_processo_sf', left=3*cm),
            ObjectValue(attribute_name='casa_legislativa', left=6*cm),
            ObjectValue(attribute_name='data_adesao', left=11*cm,
                get_value=lambda instance: instance.data_adesao.strftime('%d/%m/%Y')
            ),
            ObjectValue(attribute_name='projeto', left=14*cm)
        ]
        #border = {'bottom': True}

    #groups = [
    #    ReportGroup(attribute_name='casa_legislativa.municipio.uf',
    #        band_header=ReportBand(
    #            height=0.7*cm,
    #            elements= [
    #                ObjectValue(attribute_name='casa_legislativa.municipio.uf',
    #                    get_Value= lambda instance: 'CasaLegislativa: '+ (instance.casa_legislativa.uf.regiao)
    #                )
    #            ],
    #            borders={'bottom': True},
    #        )
    #    )
    #]


class ConvenioReportRegiao(Report):
    title = u'Relatório dos Convênios por Região'
    author = u'Interlegis'
    class band_page_header(ReportBand):
        elements = [
            Label(
                text="Região", left=0*cm
            ),
            Label(
                text="Quantidade Casas", left=3*cm,
            ),
            Label(
                text="Quantidade Casas Conveniadas", left=6*cm
            ),
            Label(
                text="Porcentagem Casas Conveniadas", left=15*cm
            ),
        ]
    class band_detail(DetailBand):
        height = 0.5*cm
        elements=[
            ObjectValue(attribute_name='regiao', left=0*cm, ),
            ObjectValue(attribute_name='casas', left=3*cm,),
            ObjectValue(attribute_name='casas_conveniadas', left=6*cm),
            ObjectValue(attribute_name='porc_casas_conveniadas', left=15*cm),
        ]
        border = {'bottom': True}

    class band_summary(ReportBand):
        elements = [
            Label(text="Total", top=0.1*cm, left=0),
            ObjectValue(attribute_name='casas', action=FIELD_ACTION_SUM, left=3*cm, top=0.1*cm),
            ObjectValue(attribute_name='casas_conveniadas', left=6*cm, action=FIELD_ACTION_SUM),
                    ]
        borders = {'top':True}
        child_bands = [
            ReportBand(
                height = 0.6*cm,
                elements = [
                    Label(text="Total",),
                    ObjectValue(attribute_name='casas', action=FIELD_ACTION_COUNT,)
                    ]
                ),
            ]