import base64
import magic
from datetime import datetime
from rest_framework import serializers
from django.utils import timezone
from sigi.apps.eventos.models import Evento


class EventoSerializer(serializers.ModelSerializer):
    casa_nome = serializers.SerializerMethodField("get_casa_nome")
    casa_logradouro = serializers.SerializerMethodField("get_casa_logradouro")
    casa_bairro = serializers.SerializerMethodField("get_casa_bairro")
    casa_municipio = serializers.SerializerMethodField("get_casa_municipio")
    casa_uf = serializers.SerializerMethodField("get_casa_uf")
    casa_cep = serializers.SerializerMethodField("get_casa_cep")
    banner_base64 = serializers.SerializerMethodField("get_banner_base64")
    data_inicio = serializers.SerializerMethodField("get_data_inicio")
    data_termino = serializers.SerializerMethodField("get_data_termino")

    class Meta:
        model = Evento
        fields = [
            "id",
            "nome",
            "turma",
            "publico_alvo",
            "data_inicio",
            "data_termino",
            "carga_horaria",
            "local",
            "casa_nome",
            "casa_logradouro",
            "casa_bairro",
            "casa_municipio",
            "casa_uf",
            "casa_cep",
            "link_inscricao",
            "chave_inscricao",
            "perfil_aluno",
            "observacao_inscricao",
            "contato_inscricao",
            "telefone_inscricao",
            "banner",
            "banner_base64",
        ]

    def get_casa_nome(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.nome
        return ""

    def get_casa_logradouro(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.logradouro
        return ""

    def get_casa_bairro(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.bairro
        return ""

    def get_casa_municipio(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.municipio.nome
        return ""

    def get_casa_uf(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.municipio.uf.nome
        return ""

    def get_casa_cep(self, obj):
        if obj.casa_anfitria:
            return obj.casa_anfitria.cep
        return ""

    def get_banner_base64(self, obj):
        if obj.banner:
            mime_type = magic.from_file(obj.banner.path, mime=True)
            obj.banner.file.seek(0)  # Garante que está no início do arquivo
            b64str = (base64.b64encode(obj.banner.file.read())).decode("ascii")
            return f"data:{mime_type};base64, {b64str}"
        return None

    def get_data_inicio(self, obj):
        if obj.data_inicio and obj.hora_inicio:
            return datetime.combine(obj.data_inicio, obj.hora_inicio)
        else:
            return obj.data_inicio

    def get_data_termino(self, obj):
        if obj.data_termino and obj.hora_termino:
            return datetime.combine(obj.data_termino, obj.hora_termino)
        else:
            return obj.data_termino


class EventoListSerializer(EventoSerializer):
    class Meta:
        model = Evento
        fields = [
            "id",
            "nome",
            "turma",
            "data_inicio",
            "data_termino",
            "carga_horaria",
            "local",
            "casa_nome",
            "casa_logradouro",
            "casa_bairro",
            "casa_municipio",
            "casa_uf",
            "casa_cep",
        ]
