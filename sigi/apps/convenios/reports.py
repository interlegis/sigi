# -*- coding: utf-8 -*-
from operator import attrgetter
from geraldo import Report, ReportBand, ObjectValue, DetailBand, Label, \
                    landscape,SystemField, BAND_WIDTH,ReportGroup, \
                    FIELD_ACTION_SUM, FIELD_ACTION_COUNT


from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

class CasasAderidasReport(object):
    pass

class CasasNaoAderidasReport(object):
    pass

class CasasComEquipamentosReport(object):
    pass

class SemEquipamentosReport(object):
    pass
class ConvenioReport(Report):
    title = u'Relatórios dos Convênios'
    #author = u'Interlegis'
    print_if_empty = True
    page_size = A4#landscape(A4)

    class band_page_header(ReportBand):
        height = 1.3*cm

        elements = [
            SystemField(
                expression='%(report_title)s',top=0.1*cm,left=0,width=BAND_WIDTH,
                style={'fontName': 'Helvetica-Bold','fontSize':14, 'alignment': TA_CENTER}
            ),
            SystemField(expression=u'Página %(page_number)d de %(page_count)d', top=0.1*cm,
                    width=BAND_WIDTH, style={'alignment': TA_RIGHT}
            ),
            Label(
                text="Nº Processo", left=0.5*cm, top=0.8*cm
            ),
            Label(
                text="Nome", left=3*cm, top=0.8*cm
            ),
            Label(
                text="Data Adesão", left=7*cm, top=0.8*cm
            ),
            Label(
                text="Projeto", left=10*cm, top=0.8*cm
            ),
        ]
        borders = {'bottom': True}

    class band_page_footer(ReportBand):
        height = 0.5*cm

        elements = [
            Label(text='Interlegis', top=0.1*cm),
            SystemField(expression=u'Impresso em %(now:%d/%m/%Y)s às %(now:%H:%M)s', top=0.1*cm,
                width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
        ]
        borders = {'top': True}

    class band_detail(DetailBand):
        height = 0.5*cm
        elements=[
            ObjectValue(attribute_name='num_processo_sf', left=0.5*cm),
            ObjectValue(attribute_name='casa_legislativa', left=3*cm),
            ObjectValue(attribute_name='data_adesao', left=7*cm),
            ObjectValue(attribute_name='projeto', left=10*cm)
        ]
        #border = {'bottom': True}

    groups = [
        ReportGroup(attribute_name='casa_legislativa.municipio.uf',
            band_header=ReportBand(
                height=0.7*cm,
                elements= [
                    ObjectValue(attribute_name='casa_legislativa.municipio.uf',
                        get_Value= lambda instance: 'CasaLegislativa: '+ (instance.casa_legislativa.uf.regiao)
                    )
                ],
                borders={'bottom': True},
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
