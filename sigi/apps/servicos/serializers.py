from rest_framework import serializers
from yaml import serialize

from sigi.apps.casas.models import Orgao, TipoOrgao
from sigi.apps.servicos.models import Servico, TipoServico


class ProdutosSerializer(serializers.Serializer):
    produto = serializers.CharField(max_length=40)
    quantidade = serializers.IntegerField()


class OrgaoSerializer(serializers.ModelSerializer):
    sigla = serializers.ReadOnlyField(source="get_sigla")
    tipo_orgao_nome = serializers.CharField(source="tipo.nome", read_only=True)
    tipo_orgao_sigla = serializers.CharField(
        source="tipo.sigla", read_only=True
    )
    municipio = serializers.CharField(source="municipio.nome", read_only=True)
    uf = serializers.CharField(source="municipio.uf.sigla", read_only=True)
    telefone = serializers.ReadOnlyField()

    class Meta:
        model = Orgao
        fields = [
            "nome",
            "sigla",
            "tipo_orgao_nome",
            "tipo_orgao_sigla",
            "cnpj",
            "logradouro",
            "bairro",
            "municipio",
            "cep",
            "uf",
            "email",
            "ult_alt_endereco",
            "telefone",
        ]


class ServicoSerializer(serializers.ModelSerializer):
    casa_legislativa = OrgaoSerializer(read_only=True)
    tipo_servico_nome = serializers.CharField(
        source="tipo_servico.nome", read_only=True
    )
    tipo_servico_sigla = serializers.CharField(
        source="tipo_servico.sigla", read_only=True
    )

    class Meta:
        model = Servico
        fields = [
            "casa_legislativa",
            "tipo_servico_nome",
            "tipo_servico_sigla",
            "url",
            "hospedagem_interlegis",
            "data_ativacao",
        ]
