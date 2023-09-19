from rest_framework import serializers
from sigi.apps.eventos.models import Evento


class EventoSerializer(serializers.ModelSerializer):
    casa_nome = serializers.SerializerMethodField("get_casa_nome")
    casa_logradouro = serializers.SerializerMethodField("get_casa_logradouro")
    casa_bairro = serializers.SerializerMethodField("get_casa_bairro")
    casa_municipio = serializers.SerializerMethodField("get_casa_municipio")
    casa_uf = serializers.SerializerMethodField("get_casa_uf")
    casa_cep = serializers.SerializerMethodField("get_casa_cep")

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
