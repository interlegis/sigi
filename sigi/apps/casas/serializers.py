from rest_framework import serializers
from sigi.apps.casas.models import Orgao
from sigi.apps.convenios.models import Convenio, Anexo
from sigi.apps.eventos.models import Evento
from sigi.apps.servicos.models import Servico


class AnexoConvenioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anexo
        fields = ["arquivo", "descricao"]


class ConvenioSerializer(serializers.ModelSerializer):
    sigla = serializers.ReadOnlyField(source="projeto.sigla")
    projeto = serializers.ReadOnlyField(source="projeto.nome")
    status = serializers.SerializerMethodField("get_status")
    inicio_vigencia = serializers.SerializerMethodField("get_inicio_vigencia")
    termino_vigencia = serializers.SerializerMethodField("get_termino_vigencia")
    documento_gescon = serializers.SerializerMethodField("get_documento_gescon")
    anexo_set = AnexoConvenioSerializer(many=True, read_only=True)

    class Meta:
        model = Convenio
        fields = [
            "sigla",
            "projeto",
            "num_convenio",
            "status",
            "inicio_vigencia",
            "termino_vigencia",
            "documento_gescon",
            "anexo_set",
        ]

    def get_status(self, obj):
        return obj.get_status()

    def get_inicio_vigencia(self, obj):
        return obj.data_retorno_assinatura

    def get_termino_vigencia(self, obj):
        return obj.data_termino_vigencia

    def get_documento_gescon(self, obj):
        return obj.get_url_gescon()


class EventoSerializer(serializers.ModelSerializer):
    categoria_sigla = serializers.SerializerMethodField("get_categoria_sigla")
    categoria_nome = serializers.SerializerMethodField("get_categoria_nome")

    class Meta:
        model = Evento
        fields = [
            "nome",
            "categoria_nome",
            "categoria_sigla",
            "data_inicio",
            "data_termino",
            "num_processo",
            "total_participantes",
        ]

    def get_categoria_sigla(self, obj):
        return obj.tipo_evento.categoria

    def get_categoria_nome(self, obj):
        return obj.tipo_evento.get_categoria_display()


class ServicoSerializer(serializers.ModelSerializer):
    sigla = serializers.ReadOnlyField(source="tipo_servico.sigla")
    tipo_servico = serializers.ReadOnlyField(source="tipo_servico.nome")
    url = serializers.SerializerMethodField("get_url")
    data_verificacao = serializers.SerializerMethodField("get_data_verificacao")
    resultado_verificacao = serializers.SerializerMethodField(
        "get_resultado_verificacao"
    )

    class Meta:
        model = Servico
        fields = [
            "sigla",
            "tipo_servico",
            "data_ativacao",
            "url",
            "data_verificacao",
            "resultado_verificacao",
            "data_ultimo_uso",
        ]

    def get_url(self, obj):
        if not obj.url:
            return ""
        if "http" in obj.url:
            return obj.url
        else:
            return f"http://{ obj.url }"

    def get_data_verificacao(self, obj):
        if obj.data_verificacao:
            return obj.data_verificacao.date()
        return None

    def get_resultado_verificacao(self, obj):
        return obj.get_resultado_verificacao_display()


class OrgaoAtendidoSerializer(serializers.ModelSerializer):
    tipo = serializers.StringRelatedField()
    tipo_sigla = serializers.ReadOnlyField(source="tipo.sigla")
    municipio = serializers.SlugRelatedField(read_only=True, slug_field="nome")
    uf_nome = serializers.SerializerMethodField("get_uf_nome")
    uf_sigla = serializers.SerializerMethodField("get_uf_sigla")
    convenio_set = ConvenioSerializer(many=True, read_only=True)
    evento_set = EventoSerializer(many=True, read_only=True)
    servico_set = ServicoSerializer(many=True, read_only=True)

    class Meta:
        model = Orgao
        fields = [
            "id",
            "nome",
            "sigla",
            "tipo",
            "tipo_sigla",
            "cnpj",
            "logradouro",
            "bairro",
            "municipio",
            "uf_nome",
            "uf_sigla",
            "cep",
            "email",
            "telefone_geral",
            "foto",
            "convenio_set",
            "evento_set",
            "servico_set",
        ]

    def get_uf_nome(self, obj):
        return obj.municipio.uf.nome

    def get_uf_sigla(self, obj):
        return obj.municipio.uf.sigla
