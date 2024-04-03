import base64
import magic
from pathlib import Path
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
    projeto = serializers.SlugRelatedField(read_only=True, slug_field="nome")
    status = serializers.SerializerMethodField("get_status")
    inicio_vigencia = serializers.SerializerMethodField("get_inicio_vigencia")
    termino_vigencia = serializers.SerializerMethodField(
        "get_termino_vigencia"
    )
    documento_gescon = serializers.SerializerMethodField(
        "get_documento_gescon"
    )
    anexo_set = AnexoConvenioSerializer(many=True, read_only=True)

    class Meta:
        model = Convenio
        fields = [
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
    class Meta:
        model = Evento
        fields = [
            "nome",
            "data_inicio",
            "data_termino",
            "num_processo",
            "total_participantes",
        ]


class ServicoSerializer(serializers.ModelSerializer):
    tipo_servico = serializers.SlugRelatedField(
        read_only=True, slug_field="nome"
    )
    url = serializers.SerializerMethodField("get_url")
    data_verificacao = serializers.SerializerMethodField(
        "get_data_verificacao"
    )
    resultado_verificacao = serializers.SerializerMethodField(
        "get_resultado_verificacao"
    )

    class Meta:
        model = Servico
        fields = [
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
    municipio = serializers.SlugRelatedField(read_only=True, slug_field="nome")
    uf_nome = serializers.SerializerMethodField("get_uf_nome")
    uf_sigla = serializers.SerializerMethodField("get_uf_sigla")
    foto_base64 = serializers.SerializerMethodField("get_foto_base64")
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
            "foto_base64",
            "convenio_set",
            "evento_set",
            "servico_set",
        ]

    def get_uf_nome(self, obj):
        return obj.municipio.uf.nome

    def get_uf_sigla(self, obj):
        return obj.municipio.uf.sigla

    def get_foto_base64(self, obj):
        if obj.foto and Path(obj.foto.path).exists():
            mime_type = magic.from_file(obj.foto.path, mime=True)
            obj.foto.file.seek(0)  # Garante que está no início do arquivo
            b64str = (base64.b64encode(obj.foto.file.read())).decode("ascii")
            return f"data:{mime_type};base64, {b64str}"
        return None
