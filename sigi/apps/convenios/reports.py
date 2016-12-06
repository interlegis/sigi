# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from geraldo import (FIELD_ACTION_SUM, Label, ObjectValue, ReportBand,
                     ReportGroup)
from reportlab.lib.units import cm

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
    title = _(u'Relatório de Convênios')

    class band_page_header(ReportDefault.band_page_header):

        label_top = ReportDefault.band_page_header.label_top
        label_left = [0, 1.5, 7, 9, 11, 13, 15, 17]
        elements = list(ReportDefault.band_page_header.elements)
        height = 4.7 * cm

        elements += [
            Label(
                text=_(u"UF"),
                left=label_left[0] * cm,
                top=label_top + 0.4 * cm,
            ),
            Label(
                text=_(u"Municipio"),
                left=label_left[1] * cm,
                top=label_top + 0.4 * cm,
            ),
            Label(
                text=_(u"Data de Adesão"),
                left=label_left[2] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Número do Convênio"),
                left=label_left[3] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Data do Convênio"),
                left=label_left[4] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Data de Publicação"),
                left=label_left[5] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Data de Aceite"),
                left=label_left[6] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Projeto"),
                left=label_left[7] * cm,
                top=label_top + 0.4 * cm,
                width=2 * cm,
            ),
        ]

    class band_page_footer(ReportDefault.band_page_footer):
        pass

    class band_detail(ReportDefault.band_detail):

        label_left = [0, 1.5, 7, 9, 11, 13, 15, 17]

        elements = [
            ObjectValue(
                attribute_name='casa_legislativa.municipio.uf.sigla',
                left=label_left[0] * cm
            ),
            ObjectValue(
                attribute_name='casa_legislativa.municipio.nome',
                left=label_left[1] * cm
            ),
            ObjectValue(
                attribute_name='data_adesao',
                left=label_left[2] * cm,
                get_value=lambda instance:
                    instance.data_adesao.strftime('%d/%m/%Y') if instance.data_adesao is not None else '-'
            ),
            ObjectValue(
                attribute_name='num_convenio',
                left=label_left[3] * cm
            ),
            ObjectValue(
                attribute_name='data_retorno_assinatura',
                left=label_left[4] * cm,
                get_value=lambda instance:
                    instance.data_retorno_assinatura.strftime('%d/%m/%Y') if instance.data_retorno_assinatura is not None else '-'
            ),
            ObjectValue(
                attribute_name='data_pub_diario',
                left=label_left[5] * cm,
                get_value=lambda instance:
                    instance.data_pub_diario.strftime('%d/%m/%Y') if instance.data_pub_diario is not None else '-'
            ),
            ObjectValue(
                attribute_name='data_termo_aceite',
                left=label_left[6] * cm,
                get_value=lambda instance:
                    instance.data_termo_aceite.strftime('%d/%m/%Y') if instance.data_termo_aceite is not None else '-'
            ),
            ObjectValue(
                attribute_name='projeto.sigla',
                left=label_left[7] * cm
            ),
        ]

    groups = [
        ReportGroup(attribute_name='casa_legislativa.municipio.uf',
                    band_header=ReportBand(
                        height=0.7 * cm,
                        elements=[
                            ObjectValue(attribute_name='casa_legislativa.municipio.uf',
                                        get_Value=lambda instance: '%s: %s' % (_(u'Casa Legislativa'), instance.casa_legislativa.uf)
                                        )
                        ],
                        borders={'top': True},
                    )
                    )
    ]


class ConvenioReportSemAceite(ConvenioReport):

    class band_page_header(ReportDefault.band_page_header):

        label_top = ReportDefault.band_page_header.label_top
        label_left = [0, 1.5, 7, 9, 11, 13, 15, 17]
        elements = list(ReportDefault.band_page_header.elements)
        height = 4.7 * cm

        elements += [
            Label(
                text=_(u"UF"),
                left=label_left[0] * cm,
                top=label_top + 0.4 * cm,
            ),
            Label(
                text=_(u"Município"),
                left=label_left[1] * cm,
                top=label_top + 0.4 * cm,
            ),
            Label(
                text=_(u"Data de Adesão"),
                left=label_left[3] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Número do Convênio"),
                left=label_left[4] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Data do Convênio"),
                left=label_left[5] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Data de Publicação"),
                left=label_left[6] * cm,
                top=label_top,
                width=2 * cm,
            ),
            Label(
                text=_(u"Projeto"),
                left=label_left[7] * cm,
                top=label_top + 0.4 * cm,
                width=2 * cm,
            ),
        ]

    class band_detail(ReportDefault.band_detail):

        label_left = [0, 1.5, 7, 9, 11, 13, 15, 17]

        elements = [
            ObjectValue(
                attribute_name='casa_legislativa.municipio.uf.sigla',
                left=label_left[0] * cm
            ),
            ObjectValue(
                attribute_name='casa_legislativa.municipio.nome',
                left=label_left[1] * cm
            ),
            ObjectValue(
                attribute_name='data_adesao',
                left=label_left[3] * cm,
                get_value=lambda instance:
                    instance.data_adesao.strftime('%d/%m/%Y') if instance.data_adesao is not None else '-'
            ),
            ObjectValue(
                attribute_name='num_convenio',
                left=label_left[4] * cm
            ),
            ObjectValue(
                attribute_name='data_retorno_assinatura',
                left=label_left[5] * cm,
                get_value=lambda instance:
                    instance.data_retorno_assinatura.strftime('%d/%m/%Y') if instance.data_retorno_assinatura is not None else '-'
            ),
            ObjectValue(
                attribute_name='data_pub_diario',
                left=label_left[6] * cm,
                get_value=lambda instance:
                    instance.data_pub_diario.strftime('%d/%m/%Y') if instance.data_pub_diario is not None else '-'
            ),
            ObjectValue(
                attribute_name='projeto.sigla',
                left=label_left[7] * cm
            ),
        ]


float_duas_casas = lambda instance: '%.2f' % (instance)


class ConvenioReportRegiao(ReportDefault):
    title = _(u'Relatório de Convênios por Região')

    class band_page_header(ReportDefault.band_page_header):
        label_top = ReportDefault.band_page_header.label_top
        label_left = [0.5, 6, 8, 10, 12, 14]
        map(lambda x: x - 0.4, label_left)

        elements = list(ReportDefault.band_page_header.elements)

        elements += [
            Label(text=_(u"UF"), left=label_left[0] * cm, top=label_top,),
            Label(text=_(u"Total"), left=label_left[1] * cm, top=label_top,),
            Label(text=_(u"Aderidas"), left=label_left[2] * cm, top=label_top,),
            Label(text="%", left=label_left[3] * cm, top=label_top),
            Label(text=_(u"Ñ Aderidas"), left=label_left[4] * cm, top=label_top,),
            Label(text="%", left=label_left[5] * cm, top=label_top),
        ]

    class band_detail(ReportDefault.band_detail):
        label_left = [0.5, 6, 8, 10, 12, 14]
        display_inline = True
        float_duas_casas = lambda instance: '%.2f' % (instance.porc_casas_aderidas)
        default_style = {'fontName': 'Helvetica', 'fontSize': 11}

        elements = [
            ObjectValue(attribute_name='estado', left=label_left[0] * cm, ),
            ObjectValue(attribute_name='quant_casas', left=label_left[1] * cm,),
            ObjectValue(attribute_name='quant_casas_aderidas', left=label_left[2] * cm),
            ObjectValue(attribute_name='porc_casas_aderidas', left=label_left[3] * cm),
            ObjectValue(attribute_name='quant_casas_nao_aderidas', left=label_left[4] * cm),
            ObjectValue(attribute_name='porc_casas_nao_aderidas', left=label_left[5] * cm,),
        ]

    class band_summary(ReportBand):
        label_left = [0.5, 6, 8, 10, 12, 14]
        elements = [
            Label(text=_(u"Total"), top=0.1 * cm, left=label_left[0] * cm),
            ObjectValue(attribute_name='quant_casas', action=FIELD_ACTION_SUM, left=label_left[1] * cm, ),
            ObjectValue(attribute_name='quant_casas_aderidas', action=FIELD_ACTION_SUM, left=label_left[2] * cm),
            #            ObjectValue(attribute_name='porc_casas_aderidas', action=FIELD_ACTION_AVG, left=label_left[3]*cm,
            # get_value= lambda instance : lambda instance: '%.2f' %  (instance.porc_casas_aderidas),
            #            ),
            ObjectValue(attribute_name='quant_casas_nao_aderidas', action=FIELD_ACTION_SUM, left=label_left[4] * cm),
            #            ObjectValue(attribute_name='porc_casas_nao_aderidas', left=label_left[5]*cm,
            #               get_value=lambda x: teste(),
            #            ),
        ]
        borders = {'top': True}


class ConvenioPorCMReport(ConvenioReport):
    title = _(u'Relatório de Convênios por Câmara Municipal')


class ConvenioPorALReport(ConvenioReport):
    title = _(u'Relatório de Convênios por Assembléia Legislativa')


class ConvenioReportSemAceiteCM(ConvenioReportSemAceite):
    title = _(u'Relatório de Convênios por Câmara Municipal')


class ConvenioReportSemAceiteAL(ConvenioReportSemAceite):
    title = _(u'Relatório de Convênios por Assembléia Legislativa')
