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
        label_top = 3.7*cm
        default_style = {'fontName': 'Helvetica', 'fontSize':9}

        BASE_DIR = os.path.abspath(os.path.dirname(__file__) + '../../../../')
        #BASE_DIR = os.path.abspath(os.getcwd() + '../..')

        elements = [
            Image(filename= BASE_DIR + '/media/images/logo-interlegis.jpg',
                left=15.5*cm,right=1*cm,top=0.1*cm,bottom=1*cm,
                width=4.2*cm,height=3*cm,
            ),
            Image(filename=  BASE_DIR + '/media/images/logo-senado.png',
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
        default_style = {'fontName': 'Helvetica', 'fontSize': 8}



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

        label_top = ReportDefault.band_page_header.label_top
        label_left = [0,1.5,6,9,11,13,15,17]
        elements = list(ReportDefault.band_page_header.elements)

        elements += [
            Label(
                text="Estado",
                left=label_left[0]*cm,
                top=label_top
            ),
            Label(
                text="Municipio",
                left=label_left[1]*cm,
                top=label_top
            ),
            Label(
                text="Nº Convenio",
                left=label_left[2]*cm,
                top=label_top
            ),
            Label(
                text="Data Adesão",
                left=label_left[3]*cm,
                top=label_top
            ),
            Label(
                text="Data Conv.",
                left=label_left[4]*cm,
                top=label_top
            ),
            Label(
                text="Data Aceite",
                left=label_left[5]*cm,
                top=label_top
            ),
            Label(
                text="Data D.O.",
                left=label_left[6]*cm,
                top=label_top
            ),
            Label(
                text="Projeto",
                left=label_left[7]*cm,
                top=label_top
            ),
        ]



    class band_page_footer(ReportDefault.band_page_footer):
        pass

    class band_detail(ReportDefault.band_detail):

        label_left = [0,1.5,6,9,11,13,15,17]

        elements=[
            ObjectValue(
                attribute_name='casa_legislativa.municipio.uf.sigla',
                left=label_left[0]*cm
            ),
            ObjectValue(
                attribute_name='casa_legislativa.municipio.nome',
                left=label_left[1]*cm
            ),
            ObjectValue(
                attribute_name='num_convenio',
                left=label_left[2]*cm
            ),
            ObjectValue(
                attribute_name='data_adesao',
                left=label_left[3]*cm,
                get_value=lambda instance:
                    instance.data_adesao.strftime('%d/%m/%Y') if instance.data_adesao != None else '-'
            ),
            ObjectValue(
                attribute_name='data_retorno_assinatura',
                left=label_left[4]*cm,
                get_value=lambda instance:
                    instance.data_retorno_assinatura.strftime('%d/%m/%Y') if instance.data_retorno_assinatura != None else '-'
            ),
            ObjectValue(
                attribute_name='data_termo_aceite',
                left=label_left[5]*cm,
                get_value=lambda instance:
                    instance.data_termo_aceite.strftime('%d/%m/%Y') if instance.data_termo_aceite != None else '-'
            ),
            ObjectValue(
                attribute_name='data_pub_diario',
                left=label_left[6]*cm,
                get_value=lambda instance:
                    instance.data_pub_diario.strftime('%d/%m/%Y') if instance.data_pub_diario != None else '-'
            ),
            ObjectValue(
                attribute_name='projeto.sigla',
                left=label_left[7]*cm
            ),
        ]                

    groups = [
        ReportGroup(attribute_name='casa_legislativa.municipio.uf',
            band_header=ReportBand(
                height=0.7*cm,
                elements= [
                    ObjectValue(attribute_name='casa_legislativa.municipio.uf',
                        get_Value= lambda instance: 'CasaLegislativa: '+ (instance.casa_legislativa.uf)
                    )
                ],
                borders={'top': True},
            )
        )
    ]


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