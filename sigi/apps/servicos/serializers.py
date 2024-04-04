from rest_framework import serializers


class ProdutosSerializer(serializers.Serializer):
    produto = serializers.CharField(max_length=40)
    quantidade = serializers.IntegerField()
