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

from sigi.apps.relatorios.reports import ReportDefault

#from abc import ABCMeta

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
        label_left = [0,1.5,7,9,11,13,15,17]
        elements = list(ReportDefault.band_page_header.elements)
        height = 4.7*cm

        elements += [
            Label(
                text="UF",
                left=label_left[0]*cm,
                top=label_top + 0.4*cm,
            ),
            Label(
                text="Municipio",
                left=label_left[1]*cm,
                top=label_top + 0.4*cm,
            ),            
            Label(
                text="Data de Adesão",
                left=label_left[2]*cm,
                top=label_top,
                width=2*cm,
            ),
            Label(
                text="Número do Convenio",
                left=label_left[3]*cm,
                top=label_top,
                width=2*cm,
            ),
            Label(
                text="Data do Convênio",
                left=label_left[4]*cm,
                top=label_top,
                width=2*cm,
            ),            
            Label(
                text="Data de Publicação",
                left=label_left[5]*cm,
                top=label_top,
                width=2*cm,
            ),
            Label(
                text="Data de Aceite",
                left=label_left[6]*cm,
                top=label_top,
                width=2*cm,
            ),
            Label(
                text="Projeto",
                left=label_left[7]*cm,
                top=label_top + 0.4*cm,
                width=2*cm,
            ),
        ]



    class band_page_footer(ReportDefault.band_page_footer):
        pass

    class band_detail(ReportDefault.band_detail):

        label_left = [0,1.5,7,9,11,13,15,17]

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
                attribute_name='data_adesao',
                left=label_left[2]*cm,
                get_value=lambda instance:
                    instance.data_adesao.strftime('%d/%m/%Y') if instance.data_adesao != None else '-'
            ),
            ObjectValue(
                attribute_name='num_convenio',
                left=label_left[3]*cm
            ),
            ObjectValue(
                attribute_name='data_retorno_assinatura',
                left=label_left[4]*cm,
                get_value=lambda instance:
                    instance.data_retorno_assinatura.strftime('%d/%m/%Y') if instance.data_retorno_assinatura != None else '-'
            ),            
            ObjectValue(
                attribute_name='data_pub_diario',
                left=label_left[5]*cm,
                get_value=lambda instance:
                    instance.data_pub_diario.strftime('%d/%m/%Y') if instance.data_pub_diario != None else '-'
            ),
            ObjectValue(
                attribute_name='data_termo_aceite',
                left=label_left[6]*cm,
                get_value=lambda instance:
                    instance.data_termo_aceite.strftime('%d/%m/%Y') if instance.data_termo_aceite != None else '-'
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


class ConvenioReportRegiao(ReportDefault):
    title = u'Relatório de Convênios por Região'

    class band_page_header(ReportDefault.band_page_header):
       label_top = ReportDefault.band_page_header.label_top
       
       elements = list(ReportDefault.band_page_header.elements)

       elements += [
            Label(
                text="Região", left=0*cm,
                top=label_top,
            ),
            Label(
                text="Casas", left=3*cm,
                top=label_top,
            ),
            Label(
                text="Conveniadas", left=5*cm,
                top=label_top,
            ),            
            Label(
                text="%", left=7*cm,
                top=label_top
            ),
            Label(
                text="Não Conveniadas", left=9*cm,
                top=label_top,
            ),
        ]
    class band_detail(ReportDefault.band_detail):
        elements=[
            ObjectValue(attribute_name='regiao', left=0*cm, ),
            ObjectValue(attribute_name='casas', left=3*cm,),
            ObjectValue(attribute_name='casas_conveniadas', left=5*cm),
            ObjectValue(attribute_name='porc_casas_conveniadas', left=7*cm),
        ]
        border = {'bottom': True}

    class band_summary(ReportBand):
        elements = [
            Label(text="Total", top=0.1*cm, left=0),
            ObjectValue(attribute_name='casas', action=FIELD_ACTION_SUM, left=3*cm, top=0.1*cm),
            ObjectValue(attribute_name='casas_conveniadas', left=6*cm, action=FIELD_ACTION_SUM),
                    ]
        borders = {'top':True}
        #child_bands = [
        #    ReportBand(
        #        height = 0.6*cm,
        #        elements = [
        #            Label(text="Total",),
        #            ObjectValue(attribute_name='casas', action=FIELD_ACTION_COUNT,)
        #            ]
        #        ),
        #    ]
class ConvenioPorCMReport(ConvenioReport):
    title = u'Relatório de Convênios por Câmera Municipal'

class ConvenioPorALReport(ConvenioReport):
    title = u'Relatório de Convênios por Assembléia Legislativa'