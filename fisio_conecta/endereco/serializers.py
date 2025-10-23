from fisio_conecta import models as m
from rest_framework import serializers

class EnderecoSerializer(serializers.ModelSerializer):
    """
    Serializer para a classe Endereco.
    """
    class Meta:
        model = m.Endereco
        fields = (
            'cep',
            'logradouro',
            'bairro',
            'numero',
            'complemento',
            'cidade',
            'estado',
            'pais',
        )