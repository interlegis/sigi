# -*- coding: utf-8 -*-
from django.templatetags.static import static
from django.utils.translation import ugettext as _
from geraldo import (BAND_WIDTH, DetailBand, Label, ObjectValue, Report,
                     ReportBand, ReportGroup, SubReport, SystemField,
                     landscape)
from geraldo.graphics import Image
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


class ParlamentaresLabels(Report):

    """
    Usage example::

      >>> from geraldo.generators import PDFGenerator
      >>> queryset = CasaLegislativa.objects.filter(municipio__uf__sigla='MG')
      >>> report = LabelsReport(queryset)
      >>> report.generate_by(PDFGenerator, filename='./inline-detail-report.pdf')

    """
    formato = ''
    y = 2
    largura_etiqueta = 7
    altura_etiqueta = 3.3
    tamanho_fonte = 6.4
    altura_dados = 0.3  # logradouro, bairro, municipio, cep
    delta = start = 0.5

    def __init__(self, queryset, formato):
        super(ParlamentaresLabels, self).__init__(queryset=queryset)
        self.formato = formato
        self.page_size = A4

        if formato == '3x9_etiqueta':
            self.margin_top = 0.0 * cm
            self.margin_bottom = 0.0 * cm
            self.margin_left = -1 * cm
            self.margin_right = 0.0 * cm
            self.delta = 0.4  # espaçamento entre as "strings/linhas" da etiqueta
            self.start = 0.2  # valor entre a margin top e a etiqueta
        else:
            self.margin_top = 0.8 * cm
            self.margin_bottom = 0.8 * cm
            self.margin_left = 0.4 * cm
            self.margin_right = 0.4 * cm
            self.largura_etiqueta = 9.9
            self.altura_etiqueta = 5.6
            self.tamanho_fonte = 11
            self.altura_dados = 0.5
            self.y = 0.5

        my_elements = [
            Label(
                text=_(u'A Sua Excelência o(a) Senhor(a)'),
                top=(self.start + self.delta) * cm, left=self.y * cm, width=(self.largura_etiqueta - self.y) * cm,
            ),
            ObjectValue(
                attribute_name='nome_completo',
                top=(self.start + 2 * self.delta) * cm, left=self.y * cm, width=(self.largura_etiqueta - self.y) * cm,
                get_value=lambda instance:
                    instance.nome_completo or ""
            ),
            ObjectValue(
                attribute_name='logradouro',
                top=(self.start + 3 * self.delta) * cm, left=self.y * cm, width=(self.largura_etiqueta - self.y) * cm,
                get_value=lambda instance:
                    logradouro_parlamentar(instance)
            ),
            ObjectValue(
                attribute_name='bairro',
                top=(self.start + 4 * self.delta) * cm, left=self.y * cm, width=(self.largura_etiqueta - self.y) * cm,
                get_value=lambda instance:
                    bairro_parlamentar(instance)
            ),
            ObjectValue(
                attribute_name='municipio',
                top=(self.start + 5 * self.delta) * cm, left=self.y * cm, width=(self.largura_etiqueta - self.y) * cm,
                get_value=lambda instance:
                    municipio_parlamentar(instance)
            ),
            ObjectValue(
                attribute_name='cep',
                top=(self.start + 6 * self.delta) * cm, left=self.y * cm, width=(self.largura_etiqueta - self.y) * cm,
                get_value=lambda instance:
                    cep_parlamentar(instance)
            ),
        ]
        self.band_detail = DetailBand(width=(self.largura_etiqueta) * cm, height=(self.altura_etiqueta) * cm, margin_left=0, margin_top=0, margin_bottom=0.0 * cm, margin_right=0, elements=my_elements, display_inline=True, default_style={'fontName': 'Helvetica', 'fontSize': self.tamanho_fonte})


def logradouro_parlamentar(instance):
    try:
        return instance.mandato_set.latest('inicio_mandato').legislatura.casa_legislativa.logradouro
    except:
        return _(u"<<PARLAMENTAR SEM MANDATO - impossivel definir endereço>>")


def bairro_parlamentar(instance):
    try:
        return instance.mandato_set.latest('inicio_mandato').legislatura.casa_legislativa.bairro
    except:
        return _(u"<<PARLAMENTAR SEM MANDATO - impossivel definir endereço>>")


def municipio_parlamentar(instance):
    try:
        return instance.mandato_set.latest('inicio_mandato').legislatura.casa_legislativa.municipio
    except:
        return _(u"<<PARLAMENTAR SEM MANDATO - impossivel definir endereço>>")


def cep_parlamentar(instance):
    try:
        return instance.mandato_set.latest('inicio_mandato').legislatura.casa_legislativa.cep
    except:
        return _(u"<<PARLAMENTAR SEM MANDATO - impossivel definir endereço>>")


class CasasLegislativasReport(ReportDefault):
    title = _(u'Relatório de Casas Legislativas')
    height = 80 * cm
    page_size = landscape(A4)

    class band_page_header(ReportDefault.band_page_header):

        label_top = ReportDefault.band_page_header.label_top
        label_left = [0.3, 1, 5.5, 11, 17, 22]
        elements = list(ReportDefault.band_page_header.elements)

        elements = [
            Image(filename=ReportDefault.band_page_header.BASE_DIR + static('img/logo-interlegis.jpg'),
                  left=23.5 * cm, right=1 * cm, top=0.1 * cm, bottom=1 * cm,
                  width=4.2 * cm, height=3 * cm,
                  ),
            Image(filename=ReportDefault.band_page_header.BASE_DIR + static('img/logo-senado.png'),
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
            Label(
                text=_(u"UF"),
                left=label_left[0] * cm,
                top=label_top,
            ),
            Label(
                text=_(u"Municipio"),
                left=label_left[1] * cm,
                top=label_top,
            ),
            Label(
                text=_(u"Presidente"),
                left=label_left[2] * cm,
                top=label_top,
            ),
            Label(
                text=_(u"Endereço"),
                left=label_left[3] * cm,
                top=label_top,
            ),
            Label(
                text=_(u"Endereço na Internet"),
                left=label_left[4] * cm,
                top=label_top,
            ),
            Label(
                text=_(u"Email"),
                left=label_left[5] * cm,
                top=label_top,
            ),


        ]

    class band_page_footer(ReportDefault.band_page_footer):
        pass

    class band_detail(ReportDefault.band_detail):

        label_left = [0.3, 1, 5.5, 11, 17, 22]

        elements = [
            ObjectValue(
                attribute_name='municipio.uf.sigla',
                left=label_left[0] * cm,
                width=1 * cm,
            ),
            ObjectValue(
                attribute_name='municipio.nome',
                left=label_left[1] * cm,
            ),
            ObjectValue(
                attribute_name='presidente',
                left=label_left[2] * cm,
            ),
            ObjectValue(
                attribute_name='logradouro',
                left=label_left[3] * cm,
                get_value=lambda instance: instance.logradouro + ' - ' + instance.bairro,
            ),
            ObjectValue(
                attribute_name='pagina_web',
                left=label_left[4] * cm,
            ),
            ObjectValue(
                attribute_name='email',
                left=label_left[5] * cm,
            ),

        ]

    groups = [
        ReportGroup(attribute_name='municipio.uf',
                    band_header=ReportBand(
                        height=0.7 * cm,
                        elements=[
                            ObjectValue(attribute_name='municipio.uf')
                        ],
                        borders={'top': True},
                    )
                    )
    ]


def label_text(text):
    return "%s: " % text


class InfoCasaLegislativa(ReportDefault):
    title = _(u'Casa Legislativa')

    class band_summary(ReportBand):
        pass

    class band_page_footer(ReportBand):
        height = 1 * cm

        elements = [
            SystemField(expression=_(u'%(now:%d/%m/%Y)s às %(now:%H:%M)s'), top=0.3 * cm),
        ]

    class band_detail(ReportDefault.band_detail):

        posicao_left = [
            0, 1.3,  # Tipo
            0, 1.8,  # Regiao
            5.5, 6.8,  # U.F.
            0, 2.3,  # Municipio
            0, 2.4,  # Endereco
            0, 1.6,  # Bairro
            0, 1.3,  # CEP
            0, 1.6,  # CNPJ
            0, 2.3,  # Telefone
            0, 2.7,  # Presidente
        ]
        posicao_top = [
            0.5,  # Tipo
            1.3,  # Regiao
            1.3,  # U.F.
            2.1,  # Municipio
            2.9,  # Logradouro
            3.7,  # Bairro
            4.5,  # CEP
            5.3,  # CNPJ
            6.1,  # Telefone
            6.9,  # Presidente
        ]

        height = 30 * cm

        display_inline = True
        default_style = {'fontName': 'Helvetica', 'fontSize': 14}

        elements = [

            Label(
                text=label_text(_(u"Tipo")),
                left=posicao_left[0] * cm,
                top=posicao_top[0] * cm,
            ),
            ObjectValue(
                attribute_name='tipo.nome',
                left=posicao_left[1] * cm,
                top=posicao_top[0] * cm,
                width=6 * cm,
            ),
            Label(
                text=label_text(_(u"Região")),
                left=posicao_left[2] * cm,
                top=posicao_top[1] * cm,
            ),
            ObjectValue(
                attribute_name='municipio.uf.regiao',
                left=posicao_left[3] * cm,
                top=posicao_top[1] * cm,
                get_value=lambda instance:
                {'SL': _(u'Sul'), 'SD': _(u'Sudeste'), 'CO': _(u'Centro-Oeste'), 'NE': _(u'Nordeste'), 'NO': _(u'Norte'), }
                [instance.municipio.uf.regiao]
            ),
            Label(
                text=label_text(_(u"UF")),
                left=posicao_left[4] * cm,
                top=posicao_top[2] * cm,
            ),
            ObjectValue(
                attribute_name='municipio.uf',
                left=posicao_left[5] * cm,
                top=posicao_top[2] * cm,
            ),
            Label(
                text=label_text(_(u"Município")),
                left=posicao_left[6] * cm,
                top=posicao_top[3] * cm,
            ),
            ObjectValue(
                attribute_name='municipio.nome',
                left=posicao_left[7] * cm,
                top=posicao_top[3] * cm,
                width=20 * cm,
            ),
            # Linha 3
            Label(
                text=label_text(_(u"Endereço")),
                left=posicao_left[8] * cm,
                top=posicao_top[4] * cm,
            ),
            ObjectValue(
                attribute_name='logradouro',
                left=posicao_left[9] * cm,
                top=posicao_top[4] * cm,
                width=20 * cm,
            ),
            Label(
                text=label_text(_(u"Bairro")),
                left=posicao_left[10] * cm,
                top=posicao_top[5] * cm,
            ),
            ObjectValue(
                attribute_name='bairro',
                left=posicao_left[11] * cm,
                top=posicao_top[5] * cm,
            ),
            Label(
                text=label_text(_(u"CEP")),
                left=posicao_left[12] * cm,
                top=posicao_top[6] * cm,
            ),
            ObjectValue(
                attribute_name='cep',
                left=posicao_left[13] * cm,
                top=posicao_top[6] * cm,
            ),
            Label(
                text=label_text(_(u"CNPJ")),
                left=posicao_left[14] * cm,
                top=posicao_top[7] * cm,
            ),
            ObjectValue(
                attribute_name='cnpj',
                left=posicao_left[15] * cm,
                top=posicao_top[7] * cm,
            ),
            Label(
                text=label_text(_(u"Telefone")),
                left=posicao_left[16] * cm,
                top=posicao_top[8] * cm,
            ),
            ObjectValue(
                attribute_name='telefone',
                left=posicao_left[17] * cm,
                top=posicao_top[8] * cm,
            ),
            Label(
                text=label_text(_(u"Presidente")),
                left=posicao_left[18] * cm,
                top=posicao_top[9] * cm,
            ),
            ObjectValue(
                attribute_name='presidente',
                left=posicao_left[19] * cm,
                top=posicao_top[9] * cm,
                width=20 * cm,
            ),
        ]
    # Telefones
    tel_top = 2 * cm
    tel_left = [0, 3, 5]
    # Contato
    cont_top = 2 * cm
    cont_left = [0, 6, 9]
    # Convenios
    convenio_top = 2 * cm
    convenio_left = [0, 1.8, 4.5, 8, 10.5, 13, 15.5, 18]
    subreports = [
        # Telefones
        SubReport(
            queryset_string='%(object)s.telefones.all()',
            band_header=ReportBand(
                default_style={'fontName': 'Helvetica', 'fontSize': 12},
                height=2.5 * cm,
                elements=[
                    Label(
                        text=_(u"Telefone(s)"),
                        style={'fontSize': 14, 'alignment': TA_CENTER},
                        width=BAND_WIDTH,
                        top=1 * cm,
                    ),
                    Label(text=_(u"Número"), left=tel_left[0] * cm, top=tel_top),
                    Label(text=_(u"Tipo"), left=tel_left[1] * cm, top=tel_top),
                    Label(text=_(u"Nota"), left=tel_left[2] * cm, top=tel_top),
                ],
                borders={'bottom': True},
            ),
            band_detail=ReportBand(
                default_style={'fontName': 'Helvetica', 'fontSize': 11},
                height=0.5 * cm,
                elements=[
                    ObjectValue(attribute_name='__unicode__', left=tel_left[0] * cm),
                    ObjectValue(attribute_name='tipo', left=tel_left[1] * cm,
                                get_value=lambda instance:
                                {'F': _(u'Fixo'), 'M': _(u'Móvel'), 'X': _(u'Fax'), 'I': _(u'Indefinido')}[instance.tipo],
                                ),
                    ObjectValue(attribute_name='nota', left=tel_left[2] * cm),
                ],
                #borders = {'all':True},
            ),
        ),
        # Contatos
        SubReport(
            queryset_string='%(object)s.funcionario_set.all()',
            band_header=ReportBand(
                default_style={'fontName': 'Helvetica', 'fontSize': 12},
                height=2.5 * cm,
                elements=[
                    Label(
                        text=_(u"Contato(s)"),
                        style={'fontSize': 14, 'alignment': TA_CENTER},
                        width=BAND_WIDTH,
                        top=1 * cm,
                    ),
                    Label(text=_(u"Nome"), left=cont_left[0] * cm, top=cont_top),
                    Label(text=_(u"Nota"), left=cont_left[1] * cm, top=cont_top),
                    Label(text=_(u"E-mail"), left=cont_left[2] * cm, top=cont_top),
                ],
                borders={'bottom': True, 'top': True},
            ),
            band_detail=ReportBand(
                default_style={'fontName': 'Helvetica', 'fontSize': 11},
                height=0.5 * cm,
                elements=[
                    ObjectValue(attribute_name='nome', left=cont_left[0] * cm),
                    ObjectValue(attribute_name='nota', left=cont_left[1] * cm),
                    ObjectValue(attribute_name='email', left=cont_left[2] * cm),
                ],
                #borders = {'all':True},
            ),
        ),
        # Convenios
        SubReport(
            queryset_string='%(object)s.convenio_set.all()',
            band_header=ReportBand(
                default_style={'fontName': 'Helvetica', 'fontSize': 12},
                height=2.5 * cm,
                elements=[
                    Label(
                        text=_(u"Convênio(s)"),
                        style={'fontSize': 14, 'alignment': TA_CENTER},
                        width=BAND_WIDTH,
                        top=1 * cm,
                    ),
                    Label(text=_(u"Projeto"), left=convenio_left[0] * cm, top=convenio_top),
                    Label(text=_(u"Nº Convenio"), left=convenio_left[1] * cm, top=convenio_top),
                    Label(text=_(u"Nº Processo SF"), left=convenio_left[2] * cm, top=convenio_top),
                    Label(text=_(u"Adesão"), left=convenio_left[3] * cm, top=convenio_top),
                    Label(text=_(u"Convênio"), left=convenio_left[4] * cm, top=convenio_top),
                    Label(text=_(u"Equipada"), left=convenio_left[5] * cm, top=convenio_top),
                    Label(text=_(u"Data D.O."), left=convenio_left[6] * cm, top=convenio_top),
                ],
                borders={'bottom': True}
            ),
            band_detail=ReportBand(
                default_style={'fontName': 'Helvetica', 'fontSize': 11},
                height=0.5 * cm,
                elements=[
                    ObjectValue(attribute_name='projeto.sigla', left=convenio_left[0] * cm),
                    ObjectValue(attribute_name='num_convenio', left=convenio_left[1] * cm),
                    ObjectValue(attribute_name='num_processo_sf', left=convenio_left[2] * cm),
                    ObjectValue(attribute_name='data_adesao', left=convenio_left[3] * cm,
                                get_value=lambda instance:
                                instance.data_adesao.strftime('%d/%m/%Y') if instance.data_adesao is not None else '-'
                                ),
                    ObjectValue(attribute_name='data_retorno_assinatura', left=convenio_left[4] * cm,
                                get_value=lambda instance:
                                instance.data_retorno_assinatura.strftime('%d/%m/%Y') if instance.data_retorno_assinatura is not None else '-'
                                ),
                    ObjectValue(attribute_name='data_termo_aceite', left=convenio_left[5] * cm,
                                get_value=lambda instance:
                                instance.data_termo_aceite.strftime('%d/%m/%Y') if instance.data_termo_aceite is not None else '-'
                                ),
                    ObjectValue(attribute_name='data_pub_diario', left=convenio_left[6] * cm,
                                get_value=lambda instance:
                                instance.data_pub_diario.strftime('%d/%m/%Y') if instance.data_pub_diario is not None else '-'
                                ),
                ],
                #borders = {'all':True},
            ),
        )
    ]
